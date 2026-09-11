"""
runninghub_run.py - Etapa 4 do pipeline motion-expert (Motion Control).

Roda o workflow Wan 2.2 Animate no RunningHub via OpenAPI: sobe o swap (imagem)
+ o video original, sobrescreve os nos do workflow (imagem, video, duracao, seed),
dispara a task, faz poll do status e baixa o mp4 final.

DOIS MODOS:

1) LOTE (fan-out paralelo multi-conta) - modo principal:
     python runninghub_run.py --manifest lote.json            # PREVIEW (nao chama API)
     python runninghub_run.py --manifest lote.json --fire     # dispara de verdade
   Cada conta ativa tem 2 API keys. Limite atual do RunningHub = 1 video/dia por
   key, entao cada key renderiza 1 video e todos os jobs disparam EM PARALELO
   (ThreadPoolExecutor). O manifest so diz o @ do repertorio de cada conta; o
   script DESCOBRE os swaps (Conta N/output), PAREIA por nome com o video original
   (Repertorio/@) e le a duracao via ffprobe.

   Regras de seguranca de cota (1 video/key/dia):
   - Pula job cujo mp4 de saida JA existe (ja renderizado). Force com --overwrite.
   - Fallback de key SO quando ha folga: se a conta tem mais keys que jobs, um job
     que der 414 (cota gasta) / 810 (workflow) cai na key reserva DA PROPRIA conta.
     Sem folga (2 jobs / 2 keys), nao ha reserva - 1 job por key.

   Formato do manifest ("mes" e opcional: quando presente, FaceSwap e Motion ganham
   o nivel de mes -- Material/<mes>/<dia>/ -- e o Repertorio NAO):
   {
     "motion_control_root": "<...>\\Skills\\Motion Control",
     "repertorio_root": "<raiz da producao>\\Repertorio",
     "mes": "Julho",
     "dia": "13 07 26",
     "seed": 514990883467325,
     "contas": [
       { "conta": "Conta 1", "repertorio": "<@ do perfil de referencia 1>" },
       { "conta": "Conta 2", "repertorio": "<@ do perfil de referencia 2>" }
     ]
   }

2) SINGLE (compat com o pipeline antigo, 1 par por vez, com rotacao de conta):
     python runninghub_run.py --image <swap> --video <original> \
         --duration 14 --output "<.../2_Final/>"

Config das contas em secrets.local.json (gitignored):
  - "runninghub_active_accounts": [ { "conta": "Conta 1",
        "keys": [ {api_key, workflow_id}, {api_key, workflow_id} ] }, ... ]
  - fallback: "runninghub_accounts" (lista plana) e auto-pareada 2-a-2 nas contas
    do manifest, na ordem.

Contrato da API (doc oficial runninghub-api-doc-en, doc-8287472 / doc-8287463):
  POST /task/openapi/upload   -> sobe arquivo, retorna fileName
  POST /task/openapi/create   -> { apiKey, workflowId, nodeInfoList } -> taskId
  POST /task/openapi/status   -> { apiKey, taskId } -> status
  POST /task/openapi/outputs  -> { apiKey, taskId } -> urls de saida

Dependencias: requests (pip install requests) e ffprobe (ffmpeg no PATH).
"""

import argparse
import json
import math
import re
import shutil
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

try:
    import requests
except ImportError:
    sys.exit("[FATAL] Falta a lib 'requests'. Rode: pip install requests")

# ---- Configuracao ----
BASE_URL = "https://www.runninghub.ai"  # alternativa: https://www.runninghub.cn
SECRETS_FILE = Path(__file__).with_name("secrets.local.json")
DEFAULT_SEED = 514990883467325
KEYS_PER_CONTA = 2  # limite atual: 1 video/dia por key -> 2 keys = 2 videos/conta

SWAP_EXTS = (".jpeg", ".jpg", ".png", ".webp")
VIDEO_EXTS = (".mp4", ".mov", ".m4v", ".webm")

# Mapa dos nos a sobrescrever (do motion_control_api.json).
NODE_IMAGE = ("391", "image")     # LoadImage  -> swap aprovado
NODE_VIDEO = ("392", "video")     # VHS_LoadVideo -> video original
NODE_DURATION = ("341", "value")  # Int "DURACAO DO VIDEO" (segundos)
NODE_SEED = ("335", "seed")       # WanVideo Sampler seed (determinismo)

POLL_INTERVAL_S = 10
POLL_TIMEOUT_S = 1800   # 30 min teto
HTTP_TIMEOUT_S = 120

# Sem credito/power. Confirmado empiricamente: code 414 +
# msg TASK_CREATE_FAILED_BY_NOT_ENOUGH_POWER_VALUE. Cobrimos por codigo e por texto.
CREDIT_ERROR_CODES = (414, "414")
CREDIT_ERROR_HINTS = ("insufficient credit", "insufficient credits", "no credit",
                      "not_enough_power", "not enough power", "power",
                      "balance", "quota", "saldo")

# Workflow nao salvo/rodando naquela conta -> key inutil hoje.
WORKFLOW_ERROR_CODES = (810, "810")
WORKFLOW_ERROR_HINTS = ("workflow_not_saved", "not_saved", "not saved", "not_running",
                        "not running")

# Fila da conta cheia -> transitorio, ESPERAR e tentar de novo na MESMA key.
QUEUE_ERROR_CODES = (421, "421")
QUEUE_ERROR_HINTS = ("task_queue_maxed", "queue_maxed", "queue maxed", "task queue")
QUEUE_RETRY_WAIT_S = 60
QUEUE_MAX_RETRIES = 5

# Task terminou FAILED (tipicamente torch.OutOfMemoryError na GPU do RunningHub).
# Confirmado: FAILED por OOM NAO consome a cota da key (saldo intacto) -> re-tentar
# na MESMA key resolve. Esperas crescentes entre as tentativas.
FAILED_RETRY_WAITS_S = (30, 60, 120)


class CreditExhausted(Exception):
    """Key sem credito/cota (414)."""


class TaskFailed(Exception):
    """Task terminou com status FAILED -> transitorio, retry na mesma key."""


class AccountUnavailable(Exception):
    """Key com workflow nao salvo/rodando (810)."""


class QueueBusy(Exception):
    """Fila da key cheia (421) -> transitorio, esperar e retry na mesma key."""


class ApiError(Exception):
    """Falha generica da API / local."""


def mask(key: str) -> str:
    return f"...{key[-6:]}" if key and len(key) >= 6 else "***"


def _category(exc: Exception) -> str:
    if isinstance(exc, CreditExhausted):
        return "credit"
    if isinstance(exc, AccountUnavailable):
        return "workflow"
    if isinstance(exc, QueueBusy):
        return "queue"
    return "api"


# ---------------------------------------------------------------- secrets ----

def load_secrets() -> dict:
    if not SECRETS_FILE.exists():
        sys.exit(f"[FATAL] {SECRETS_FILE.name} nao existe. "
                 f"Copie de secrets.example.json e preencha as contas.")
    try:
        return json.loads(SECRETS_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        sys.exit(f"[FATAL] {SECRETS_FILE.name} invalido: {exc}")


def _valid_flat_accounts(secrets: dict) -> list:
    """Lista plana [{api_key, workflow_id}] com key E workflow preenchidos."""
    accounts = []
    for acc in secrets.get("runninghub_accounts", []):
        key = (acc.get("api_key") or "").strip()
        wid = (acc.get("workflow_id") or "").strip()
        if key and "KEY_DA_CONTA" not in key and wid:
            accounts.append({"api_key": key, "workflow_id": wid})
    return accounts


def resolve_active_accounts(secrets: dict, conta_names: list) -> dict:
    """
    Retorna { conta -> [ {api_key, workflow_id}, ... ] }.

    Preferencia: bloco explicito runninghub_active_accounts. Fallback: auto-pareia
    runninghub_accounts (lista plana) 2-a-2, na ordem das contas do manifest.
    """
    active = secrets.get("runninghub_active_accounts")
    result = {}
    if active:
        for entry in active:
            conta = entry.get("conta")
            if not conta:
                continue
            keys = []
            for k in entry.get("keys", []):
                api_key = (k.get("api_key") or "").strip()
                wid = (k.get("workflow_id") or "").strip()
                if api_key and "KEY_DA_CONTA" not in api_key:
                    keys.append({"api_key": api_key, "workflow_id": wid})
            result[conta] = keys
        return result

    flat = _valid_flat_accounts(secrets)
    for i, conta in enumerate(conta_names):
        result[conta] = flat[i * KEYS_PER_CONTA:(i + 1) * KEYS_PER_CONTA]
    return result


# -------------------------------------------------------------- API layer ----

def _check_response(resp_json: dict):
    """RunningHub retorna { code, msg, data }. code 0 = sucesso."""
    code = resp_json.get("code")
    msg = (resp_json.get("msg") or "").lower()
    if code in (0, "0", 200):
        return resp_json.get("data")
    if code in CREDIT_ERROR_CODES or any(h in msg for h in CREDIT_ERROR_HINTS):
        raise CreditExhausted(resp_json.get("msg"))
    if code in WORKFLOW_ERROR_CODES or any(h in msg for h in WORKFLOW_ERROR_HINTS):
        raise AccountUnavailable(resp_json.get("msg"))
    if code in QUEUE_ERROR_CODES or any(h in msg for h in QUEUE_ERROR_HINTS):
        raise QueueBusy(resp_json.get("msg"))
    raise ApiError(f"code={code} msg={resp_json.get('msg')}")


def _post(path: str, *, json_body=None, files=None, data=None):
    url = BASE_URL + path
    try:
        resp = requests.post(url, json=json_body, files=files, data=data,
                             timeout=HTTP_TIMEOUT_S)
        resp.raise_for_status()
    except requests.RequestException as exc:
        raise ApiError(f"falha de rede em {path}: {exc}") from exc
    try:
        return _check_response(resp.json())
    except ValueError as exc:
        raise ApiError(f"resposta nao-JSON de {path}: {exc}") from exc


def upload_file(api_key: str, file_path: Path) -> str:
    """Sobe um arquivo e retorna o fileName que o RunningHub atribuiu."""
    with file_path.open("rb") as fh:
        files = {"file": (file_path.name, fh)}
        result = _post("/task/openapi/upload", files=files, data={"apiKey": api_key})
    if isinstance(result, dict):
        name = result.get("fileName") or result.get("fileId") or result.get("name")
        if name:
            return name
    if isinstance(result, str):
        return result
    raise ApiError(f"upload nao retornou fileName: {result}")


def create_task(api_key: str, workflow_id: str, node_info_list: list) -> str:
    body = {"apiKey": api_key, "workflowId": workflow_id,
            "nodeInfoList": node_info_list}
    result = _post("/task/openapi/create", json_body=body)
    task_id = result.get("taskId") if isinstance(result, dict) else None
    if not task_id:
        raise ApiError(f"create nao retornou taskId: {result}")
    return task_id


def get_status(api_key: str, task_id: str) -> str:
    result = _post("/task/openapi/status",
                   json_body={"apiKey": api_key, "taskId": task_id})
    if isinstance(result, str):
        return result.upper()
    if isinstance(result, dict):
        return str(result.get("taskStatus") or result.get("status") or "").upper()
    return ""


def get_outputs(api_key: str, task_id: str) -> list:
    result = _post("/task/openapi/outputs",
                   json_body={"apiKey": api_key, "taskId": task_id})
    items = result if isinstance(result, list) else result.get("outputs", [])
    urls = []
    for it in items:
        if isinstance(it, str):
            urls.append(it)
        elif isinstance(it, dict):
            u = it.get("fileUrl") or it.get("url")
            if u:
                urls.append(u)
    return urls


def failed_reason(api_key: str, task_id: str) -> str:
    """
    Motivo real de uma task FAILED. O /outputs de uma task falhada responde
    code 805 com data.failedReason -> nao da pra usar _post (ele levanta no 805).
    Best-effort: nunca levanta, so enriquece a mensagem de erro.
    """
    try:
        resp = requests.post(BASE_URL + "/task/openapi/outputs",
                             json={"apiKey": api_key, "taskId": task_id},
                             timeout=HTTP_TIMEOUT_S)
        reason = ((resp.json().get("data") or {}).get("failedReason")) or {}
    except (requests.RequestException, ValueError, AttributeError):
        return "motivo desconhecido"
    exc = reason.get("exception_type") or "motivo desconhecido"
    node = reason.get("node_name")
    return f"{exc} (no {node})" if node else exc


def download(url: str, dest: Path):
    try:
        with requests.get(url, stream=True, timeout=HTTP_TIMEOUT_S) as r:
            r.raise_for_status()
            with dest.open("wb") as fh:
                for chunk in r.iter_content(chunk_size=1 << 16):
                    fh.write(chunk)
    except requests.RequestException as exc:
        raise ApiError(f"falha ao baixar {url}: {exc}") from exc


def build_node_info(image_name: str, video_name: str, duration: int, seed: int):
    # fieldValue como string (a doc tipa fieldValue como string).
    return [
        {"nodeId": NODE_IMAGE[0], "fieldName": NODE_IMAGE[1], "fieldValue": image_name},
        {"nodeId": NODE_VIDEO[0], "fieldName": NODE_VIDEO[1], "fieldValue": video_name},
        {"nodeId": NODE_DURATION[0], "fieldName": NODE_DURATION[1], "fieldValue": str(duration)},
        {"nodeId": NODE_SEED[0], "fieldName": NODE_SEED[1], "fieldValue": str(seed)},
    ]


def _create_with_queue_retry(api_key, workflow_id, node_info, tag) -> str:
    """Cria a task; 421 (fila cheia) e transitorio -> espera e re-tenta na mesma key."""
    for attempt in range(1, QUEUE_MAX_RETRIES + 1):
        try:
            return create_task(api_key, workflow_id, node_info)
        except QueueBusy as exc:
            if attempt == QUEUE_MAX_RETRIES:
                raise
            print(f"{tag} fila cheia {attempt}/{QUEUE_MAX_RETRIES} ({exc}); "
                  f"espera {QUEUE_RETRY_WAIT_S}s...")
            time.sleep(QUEUE_RETRY_WAIT_S)


def _poll(api_key, task_id, tag):
    waited = 0
    while waited < POLL_TIMEOUT_S:
        status = get_status(api_key, task_id)
        if status in ("SUCCESS", "SUCCEEDED", "COMPLETED"):
            return
        if status in ("FAILED", "ERROR", "CANCELLED"):
            raise TaskFailed(f"task {task_id} {status}: {failed_reason(api_key, task_id)}")
        time.sleep(POLL_INTERVAL_S)
        waited += POLL_INTERVAL_S
    raise ApiError(f"timeout ({POLL_TIMEOUT_S}s) esperando a task {task_id}")


# -------------------------------------------------------------- duracao ------

def ffprobe_duration(video_path: Path) -> int:
    """Duracao do video em segundos (arredonda pra cima). Requer ffprobe no PATH."""
    try:
        out = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "default=noprint_wrappers=1:nokey=1", str(video_path)],
            capture_output=True, text=True, timeout=60)
    except FileNotFoundError:
        raise ApiError("ffprobe nao encontrado (instale ffmpeg e garanta no PATH).")
    except subprocess.SubprocessError as exc:
        raise ApiError(f"ffprobe falhou em {video_path.name}: {exc}")
    raw = (out.stdout or "").strip()
    try:
        secs = float(raw)
    except ValueError:
        raise ApiError(f"ffprobe nao retornou duracao pra {video_path.name}: "
                       f"{(out.stderr or '').strip()}")
    if secs <= 0:
        raise ApiError(f"duracao invalida ({secs}) pra {video_path.name}")
    return math.ceil(secs)


# ----------------------------------------------------------- descoberta ------

def _list_files(folder: Path, exts) -> list:
    if not folder.is_dir():
        return []
    return sorted(p for p in folder.iterdir()
                  if p.is_file() and p.suffix.lower() in exts)


def _match_video(swap: Path, videos: list):
    """Pareia o swap com o video de mesmo nome. Retorna (video, fuzzy_bool) ou (None, False)."""
    stem = swap.stem.lower()
    for v in videos:                       # match exato de nome
        if v.stem.lower() == stem:
            return v, False
    for v in videos:                       # match aproximado (swap pode ter sufixo)
        vs = v.stem.lower()
        if stem.startswith(vs) or vs.startswith(stem):
            return v, True
    return None, False


def _assign_keys(keys: list, num_jobs: int) -> list:
    """
    Distribui as keys da conta entre os jobs. keys[i] = lista (primaria + reservas)
    que o job i pode usar. Reserva SO existe quando ha keys sobrando (num_jobs <
    len(keys)); nunca ha cruzamento de key entre dois jobs.
    """
    assign = [[] for _ in range(num_jobs)]
    if num_jobs == 0:
        return assign
    for i in range(min(num_jobs, len(keys))):     # 1 primaria por job
        assign[i].append(keys[i])
    for idx, k in enumerate(keys[num_jobs:]):      # sobras viram reserva
        assign[idx % num_jobs].append(k)
    return assign


def _resolve_video_dir(rep_root: Path, arroba: str, dia: str) -> Path:
    """Os videos do dia ficam em Repertorio/<@>/<dia>/ (subpasta). Fallback: raiz do @."""
    day_dir = rep_root / arroba / dia
    return day_dir if day_dir.is_dir() else rep_root / arroba


def _resolve_video(video_ref: str, rep_root: Path, arroba: str, dia: str):
    """Resolve o video de um pareamento explicito: absoluto, subpasta do dia, raiz do @, ou repertorio_root."""
    if not video_ref:
        return None
    p = Path(video_ref)
    if p.is_absolute():
        return p if p.is_file() else None
    for cand in (rep_root / arroba / dia / video_ref,
                 rep_root / arroba / video_ref,
                 rep_root / video_ref):
        if cand.is_file():
            return cand
    return None


def _out_name(swap: Path, video):
    """Nome do mp4 de saida = nome do repertorio (convencao do fundador); senao o swap."""
    return f"{video.stem}.mp4" if video else f"{swap.stem}_motion.mp4"


# Pasta agrupada de swaps, nomeada por FAIXA de contas (ex: "Contas 2-4"). Dentro dela
# o arquivo e batizado pelo NUMERO da conta (2.jpeg -> Conta 2).
GROUPED_DIR_RE = re.compile(r"^contas?\s*\d+\s*-\s*\d+$", re.IGNORECASE)


def _conta_num(conta: str):
    m = re.search(r"(\d+)", conta or "")
    return m.group(1) if m else None


def _resolve_swaps(day_root: Path, conta: str):
    """
    Acha os swaps da conta. O fundador organiza de 3 jeitos; tentamos nessa ordem:
      1. <dia>/<Conta N>/output/          (uma pasta por conta)
      2. <dia>/output/<Conta N>/          (pasta individual dentro do output)
      3. <dia>/output/<Contas X-Y>/       (agrupada; filtra os arquivos que comecam
                                           pelo numero da conta)
    Retorna (swaps, origem_legivel, swap_dir).
    """
    direto = day_root / conta / "output"
    swaps = _list_files(direto, SWAP_EXTS)
    if swaps:
        return swaps, f"{conta}/output", direto

    out_root = day_root / "output"
    individual = out_root / conta
    swaps = _list_files(individual, SWAP_EXTS)
    if swaps:
        return swaps, f"output/{conta}", individual

    num = _conta_num(conta)
    if num and out_root.is_dir():
        for sub in sorted(p for p in out_root.iterdir() if p.is_dir()):
            if not GROUPED_DIR_RE.match(sub.name.strip()):
                continue
            swaps = [p for p in _list_files(sub, SWAP_EXTS) if p.stem.startswith(num)]
            if swaps:
                return swaps, f"output/{sub.name}", sub

    return [], f"{conta}/output", direto


def discover_jobs(manifest: dict, accounts_by_conta: dict):
    """Monta a lista de jobs do dia a partir do manifest. Nao chama a API."""
    mc_root = Path(manifest["motion_control_root"])
    rep_root = Path(manifest["repertorio_root"])
    dia = manifest["dia"]
    # FaceSwap e Motion podem ter nivel de mes (Material/<mes>/<dia>); o Repertorio nao.
    mes = (manifest.get("mes") or "").strip()
    material_dia = Path(mes) / dia if mes else Path(dia)
    jobs, warnings = [], []

    for entry in manifest.get("contas", []):
        conta = entry.get("conta")
        arroba = entry.get("repertorio")
        if not conta or not arroba:
            warnings.append(f"entrada de conta invalida no manifest: {entry}")
            continue
        keys = accounts_by_conta.get(conta, [])
        day_root = mc_root / "FaceSwap" / "Material" / material_dia
        swaps, origem, swap_dir = _resolve_swaps(day_root, conta)
        video_dir = _resolve_video_dir(rep_root, arroba, dia)
        out_dir = mc_root / "Motion" / "Material" / material_dia / conta / "output"
        videos = _list_files(video_dir, VIDEO_EXTS)

        # Pares (swap, video, fuzzy): explicitos no manifest OU auto-descobertos por nome.
        pairs = []
        explicit = entry.get("jobs")
        if explicit:
            for spec in explicit:
                swap_path = swap_dir / spec.get("swap", "")
                if not swap_path.is_file():
                    warnings.append(f"{conta}: swap explicito nao encontrado: {swap_path.name}")
                video_path = _resolve_video(spec.get("video"), rep_root, arroba, dia)
                if spec.get("video") and video_path is None:
                    warnings.append(f"{conta}: video explicito nao encontrado: {spec.get('video')}")
                pairs.append((swap_path, video_path, False))
        else:
            if not swaps:
                warnings.append(f"{conta}: nenhum swap em {swap_dir}")
            if not videos:
                warnings.append(f"{conta}: nenhum video em {video_dir}")
            for swap in swaps:
                video, fuzzy = _match_video(swap, videos)
                pairs.append((swap, video, fuzzy))

        if not keys:
            warnings.append(f"{conta}: nenhuma API key atribuida (ver secrets)")
        if len(pairs) > len(keys):
            warnings.append(f"{conta}: {len(pairs)} videos para {len(keys)} keys "
                            f"(limite 1 video/key/dia).")

        key_assign = _assign_keys(keys, len(pairs))
        for i, (swap, video, fuzzy) in enumerate(pairs):
            out_path = out_dir / _out_name(swap, video)
            jobs.append({
                "conta": conta, "arroba": arroba, "origem": origem,
                "swap": swap, "video": video, "fuzzy": fuzzy,
                "available_videos": videos,
                "keys": key_assign[i],
                "out_dir": out_dir, "out_path": out_path,
                "done": out_path.exists(),
                "duration": None, "duration_error": None,
            })
    return jobs, warnings


def resolve_durations(jobs: list):
    """Preenche job['duration'] via ffprobe (best-effort). So pros jobs com video."""
    cache = {}
    for j in jobs:
        v = j["video"]
        if v is None:
            continue
        if v in cache:
            j["duration"], j["duration_error"] = cache[v]
            continue
        try:
            j["duration"], j["duration_error"] = ffprobe_duration(v), None
        except ApiError as exc:
            j["duration"], j["duration_error"] = None, str(exc)
        cache[v] = (j["duration"], j["duration_error"])


def _job_runnable(j: dict) -> bool:
    """Tem recurso pra rodar (key + video pareado + duracao)."""
    return bool(j["keys"] and j["video"] and j["duration"])


def _firing_set(jobs: list, overwrite: bool) -> list:
    return [j for j in jobs if _job_runnable(j) and (overwrite or not j["done"])]


def print_plan(jobs: list, warnings: list, manifest: dict, overwrite: bool) -> int:
    print("=" * 72)
    print(f"PLANO DO LOTE - dia {manifest.get('dia')}  ({len(jobs)} swaps)")
    print(f"  motion_control_root: {manifest.get('motion_control_root')}")
    print(f"  repertorio_root:     {manifest.get('repertorio_root')}")
    print("=" * 72)

    by_conta = {}
    for j in jobs:
        by_conta.setdefault(j["conta"], []).append(j)

    fire = _firing_set(jobs, overwrite)
    for conta, cjobs in by_conta.items():
        print(f"\n{conta}   (repertorio @{cjobs[0]['arroba']}"
              f" | swap de: {cjobs[0]['origem']})")
        for j in cjobs:
            keys_txt = " + ".join(mask(k["api_key"]) for k in j["keys"]) or "SEM KEY"
            if j["done"] and not overwrite:
                print(f"  [DONE] {j['swap'].name}  (ja existe {j['out_path'].name}, pulado)")
                continue
            if j["video"] is None:
                print(f"  [X] {j['swap'].name}  ->  SEM VIDEO PAREADO   | key {keys_txt}")
                avail = ", ".join(v.name for v in j["available_videos"]) or "(vazio/inexistente)"
                print(f"      videos em @{j['arroba']}: {avail}")
                continue
            mark = "OK" if j in fire else "!!"
            dur = f"{j['duration']}s" if j["duration"] else f"? ({j['duration_error']})"
            fuzzy = "  <- MATCH APROXIMADO, confira!" if j["fuzzy"] else ""
            reserva = "  (+reserva)" if len(j["keys"]) > 1 else ""
            print(f"  [{mark}] {j['swap'].name}  ->  {j['video'].name}{fuzzy}")
            print(f"      duracao {dur} | key {keys_txt}{reserva}")
            print(f"      saida {j['out_path']}")

    if warnings:
        print("\nAVISOS:")
        for w in warnings:
            print(f"  - {w}")
    print(f"\nJobs prontos pra disparar: {len(fire)}/{len(jobs)}")
    return len(fire)


# ------------------------------------------------------------- execucao ------

def _render_with_retry(key: dict, node_info: list, out_path: Path, tag: str):
    """
    Cria a task, espera e baixa o mp4. FAILED (OOM da GPU deles) e transitorio e NAO
    queima cota -> re-tenta na MESMA key, com espera crescente. Esgotou = ApiError.
    """
    tentativas = len(FAILED_RETRY_WAITS_S) + 1
    for attempt in range(1, tentativas + 1):
        task_id = _create_with_queue_retry(key["api_key"], key["workflow_id"],
                                           node_info, tag)
        print(f"{tag} task {task_id} (workflow {key['workflow_id']}), aguardando...")
        try:
            _poll(key["api_key"], task_id, tag)
        except TaskFailed as exc:
            if attempt == tentativas:
                raise ApiError(f"{exc} (falhou {tentativas}x na mesma key)") from exc
            espera = FAILED_RETRY_WAITS_S[attempt - 1]
            print(f"{tag} FALHOU {attempt}/{tentativas} ({exc}); "
                  f"retry na mesma key em {espera}s...")
            time.sleep(espera)
            continue
        urls = get_outputs(key["api_key"], task_id)
        if not urls:
            raise ApiError(f"task {task_id} sem outputs")
        mp4 = next((u for u in urls if u.lower().endswith(".mp4")), urls[0])
        download(mp4, out_path)
        return


def run_job(job: dict, seed: int) -> dict:
    """
    Executa 1 job. Tenta as keys do job em ordem: 414/810/421-esgotado caem pra
    proxima key (reserva); erro generico de API para o job. Nunca levanta.
    """
    conta = job["conta"]
    keys = job["keys"]
    if not keys:
        return {"job": job, "ok": False, "category": "api", "msg": "sem key atribuida"}
    if job["video"] is None:
        return {"job": job, "ok": False, "category": "api", "msg": "sem video pareado"}
    if not job["duration"] or job["duration"] <= 0:
        return {"job": job, "ok": False, "category": "api",
                "msg": f"duracao invalida: {job['duration_error']}"}

    out_path = job["out_path"]
    out_path.parent.mkdir(parents=True, exist_ok=True)
    last = None
    for ki, key in enumerate(keys):
        tag = f"[{conta} | {mask(key['api_key'])}]"
        try:
            if not key["workflow_id"]:
                raise AccountUnavailable("key sem workflow_id")
            print(f"{tag} upload swap {job['swap'].name}")
            image_name = upload_file(key["api_key"], job["swap"])
            print(f"{tag} upload video {job['video'].name}")
            video_name = upload_file(key["api_key"], job["video"])
            node_info = build_node_info(image_name, video_name, job["duration"], seed)
            _render_with_retry(key, node_info, out_path, tag)
            print(f"{tag} OK -> {out_path}")
            return {"job": job, "ok": True, "category": "ok", "msg": str(out_path)}
        except (CreditExhausted, AccountUnavailable, QueueBusy) as exc:
            last = exc
            tem_reserva = ki + 1 < len(keys)
            alvo = "tenta key reserva da conta" if tem_reserva else "sem reserva"
            print(f"{tag} {type(exc).__name__}: {exc} -> {alvo}")
            continue
        except ApiError as exc:
            print(f"{tag} ERRO: {exc}")
            return {"job": job, "ok": False, "category": "api", "msg": str(exc)}

    return {"job": job, "ok": False, "category": _category(last), "msg": str(last)}


def run_batch(jobs: list, seed: int, overwrite: bool):
    """Dispara todos os jobs prontos EM PARALELO (1 thread por job)."""
    fire = _firing_set(jobs, overwrite)
    if not fire:
        sys.exit("[FATAL] Nenhum job executavel. Rode sem --fire pra ver o plano/avisos.")

    print(f"\nDisparando {len(fire)} job(s) em paralelo...\n")
    results = []
    with ThreadPoolExecutor(max_workers=len(fire)) as ex:
        futures = [ex.submit(run_job, j, seed) for j in fire]
        for fut in as_completed(futures):
            results.append(fut.result())

    print("\n" + "=" * 72)
    print("RESUMO DO LOTE")
    print("=" * 72)
    ok = [r for r in results if r["ok"]]
    fail = [r for r in results if not r["ok"]]
    for r in sorted(ok, key=lambda r: r["job"]["conta"]):
        print(f"  [OK] {r['job']['conta']} {r['job']['swap'].name} -> {r['msg']}")
    for r in sorted(fail, key=lambda r: r["job"]["conta"]):
        print(f"  [FALHA] {r['job']['conta']} {r['job']['swap'].name} "
              f"({r['category']}): {r['msg']}")
    print(f"\nTotal: {len(ok)} ok, {len(fail)} falhas de {len(fire)} disparados.")
    if fail:
        sys.exit(1)


def run_manifest(args, secrets: dict):
    manifest_path = Path(args.manifest)
    if not manifest_path.is_file():
        sys.exit(f"[FATAL] manifest nao encontrado: {manifest_path}")
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        sys.exit(f"[FATAL] manifest invalido: {exc}")

    for req in ("motion_control_root", "repertorio_root", "dia", "contas"):
        if req not in manifest:
            sys.exit(f"[FATAL] manifest sem campo obrigatorio '{req}'.")

    seed = int(manifest.get("seed", args.seed))
    conta_names = [c.get("conta") for c in manifest["contas"] if c.get("conta")]
    accounts_by_conta = resolve_active_accounts(secrets, conta_names)

    jobs, warnings = discover_jobs(manifest, accounts_by_conta)
    resolve_durations(jobs)
    ready = print_plan(jobs, warnings, manifest, args.overwrite)

    if not args.fire:
        print("\n[PREVIEW] Nada foi enviado a API. Revise o pareamento acima.")
        print("Para disparar de verdade, rode o mesmo comando com --fire.")
        return
    if ready == 0:
        sys.exit("\n[FATAL] --fire pedido, mas 0 jobs prontos. Corrija o plano antes.")
    run_batch(jobs, seed, args.overwrite)


def run_single(args, secrets: dict):
    """Modo compat: 1 par swap+video, com rotacao entre todas as contas planas."""
    if not args.output:
        sys.exit("[FATAL] modo single exige --output.")
    image_p, video_p = Path(args.image), Path(args.video)
    if not image_p.is_file():
        sys.exit(f"[FATAL] imagem nao encontrada: {image_p}")
    if not video_p.is_file():
        sys.exit(f"[FATAL] video nao encontrado: {video_p}")

    duration = args.duration if args.duration else ffprobe_duration(video_p)
    if duration <= 0:
        sys.exit("[FATAL] duracao invalida.")

    if args.stage:
        stage_dir = Path(args.stage)
        stage_dir.mkdir(parents=True, exist_ok=True)
        for src in (image_p, video_p):
            dst = stage_dir / src.name
            if dst.resolve() != src.resolve():
                shutil.copy2(src, dst)
        image_p, video_p = stage_dir / image_p.name, stage_dir / video_p.name
        print(f"  inputs copiados para {stage_dir}")

    out_dir = Path(args.output)
    out_dir.mkdir(parents=True, exist_ok=True)
    flat = _valid_flat_accounts(secrets)
    if not flat:
        sys.exit("[FATAL] Nenhuma conta valida (key + workflow) em runninghub_accounts.")

    job = {"conta": "single", "swap": image_p, "video": video_p,
           "duration": duration, "duration_error": None, "keys": flat,
           "out_dir": out_dir, "out_path": out_dir / f"{image_p.stem}_motion.mp4",
           "done": False, "fuzzy": False, "available_videos": []}
    res = run_job(job, args.seed)
    if res["ok"]:
        print(f"\n[OK] Video salvo: {res['msg']}")
        return
    sys.exit(f"\n[FATAL] Todas as {len(flat)} contas indisponiveis "
             f"({res['category']}). Ultimo motivo: {res['msg']}")


def main():
    parser = argparse.ArgumentParser(description="Motion Control via RunningHub API.")
    # Lote (principal)
    parser.add_argument("--manifest", help="JSON do lote do dia (fan-out multi-conta).")
    parser.add_argument("--fire", action="store_true",
                        help="Dispara de verdade (sem isso e so PREVIEW).")
    parser.add_argument("--overwrite", action="store_true",
                        help="Re-renderiza mesmo se o mp4 de saida ja existir.")
    # Single (compat)
    parser.add_argument("--image", help="Swap aprovado (modo single).")
    parser.add_argument("--video", help="Video original (modo single).")
    parser.add_argument("--duration", type=int, help="Duracao em s (single; senao ffprobe).")
    parser.add_argument("--output", help="Pasta destino (modo single).")
    parser.add_argument("--stage", help="Pasta pra copiar inputs antes (single).")
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED, help="Seed (determinismo).")
    args = parser.parse_args()

    secrets = load_secrets()
    if args.manifest:
        run_manifest(args, secrets)
    elif args.image and args.video:
        run_single(args, secrets)
    else:
        parser.error("informe --manifest (lote) OU --image + --video (single).")


if __name__ == "__main__":
    main()
