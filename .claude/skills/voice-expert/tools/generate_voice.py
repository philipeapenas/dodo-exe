#!/usr/bin/env python3
"""
generate_voice.py: Gera audio (Text-to-Speech) via API do ElevenLabs.

Le a API key e a configuracao da voz de `secrets.local.json` (mesma pasta).
Nunca tem credencial hardcoded.

Uso:
    python generate_voice.py "texto a falar"           # 1 mp3
    python generate_voice.py --file script.txt          # 1 mp3 por linha (001.mp3, 002.mp3, ...)
    python generate_voice.py --doc 2_motion_copy.md     # voz da secao '## Copy' -> 2_motion_voz.mp3
    python generate_voice.py "texto" --voice modelo_2    # escolhe a voz do registro
    python generate_voice.py "texto" --out audios/oi.mp3 # destino custom

Saida:
    MP3 44100 Hz 128 kbps na pasta `output/` (ou no --out informado).
"""

import argparse
import json
import os
import sys
import unicodedata
import urllib.error
import urllib.request
from pathlib import Path

API_BASE = "https://api.elevenlabs.io/v1/text-to-speech"
OUTPUT_FORMAT = "mp3_44100_128"
DEFAULT_TIMEOUT = 60
TOOLS_DIR = Path(__file__).resolve().parent
SECRETS_PATH = TOOLS_DIR / "secrets.local.json"
DEFAULT_OUT_DIR = TOOLS_DIR / "output"


class VoiceGenError(RuntimeError):
    """Erro de geracao de voz com mensagem amigavel (capturavel por item no lote)."""


# --------------------------------------------------------------------------- #
# Config / secrets
# --------------------------------------------------------------------------- #
def load_secrets(secrets_path=SECRETS_PATH) -> dict:
    """Le e valida o secrets.local.json. Levanta VoiceGenError com instrucao clara."""
    path = Path(secrets_path)
    if not path.exists():
        raise VoiceGenError(
            f"secrets.local.json nao encontrado em {path}.\n"
            "Crie o arquivo com a estrutura:\n"
            '  { "elevenlabs_api_key": "sk_...", "voices": { "nome": '
            '{ "voice_id": "...", "model_id": "eleven_multilingual_v2", '
            '"settings": { "stability": 0.4, "similarity_boost": 0.85, '
            '"style": 0.1, "use_speaker_boost": true } } } }'
        )
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise VoiceGenError(f"secrets.local.json com JSON invalido: {exc}")
    if not isinstance(data, dict):
        raise VoiceGenError("secrets.local.json deve conter um objeto JSON na raiz.")

    key = data.get("elevenlabs_api_key", "")
    if not isinstance(key, str) or not key.strip():
        raise VoiceGenError(
            "Campo 'elevenlabs_api_key' ausente ou vazio em secrets.local.json. "
            "Cole sua key do ElevenLabs (elevenlabs.io -> Profile -> API Key)."
        )

    voices = data.get("voices")
    if not isinstance(voices, dict) or not voices:
        raise VoiceGenError(
            "Campo 'voices' ausente ou vazio em secrets.local.json. "
            "Cadastre pelo menos uma voz com voice_id."
        )
    return data


def resolve_voice(secrets: dict, voice_name=None) -> tuple:
    """
    Seleciona a config de voz no registro.

    Returns: (voice_name, voice_config)
    Regra: se voice_name dado, busca exato; senao usa a unica voz disponivel
    (erro se houver mais de uma e nenhuma for especificada).
    """
    voices = secrets["voices"]

    if voice_name is not None:
        config = voices.get(voice_name)
        if config is None:
            disponiveis = ", ".join(sorted(voices.keys()))
            raise VoiceGenError(
                f"Voz '{voice_name}' nao existe no registro. Disponiveis: {disponiveis}"
            )
    else:
        if len(voices) > 1:
            disponiveis = ", ".join(sorted(voices.keys()))
            raise VoiceGenError(
                f"Ha {len(voices)} vozes cadastradas. Especifique uma com --voice. "
                f"Disponiveis: {disponiveis}"
            )
        voice_name, config = next(iter(voices.items()))

    _validate_voice_config(voice_name, config)
    return voice_name, config


def _validate_voice_config(voice_name: str, config) -> None:
    if not isinstance(config, dict):
        raise VoiceGenError(f"Config da voz '{voice_name}' deve ser um objeto JSON.")
    if not config.get("voice_id"):
        raise VoiceGenError(f"Voz '{voice_name}' sem 'voice_id' em secrets.local.json.")
    if not config.get("model_id"):
        raise VoiceGenError(f"Voz '{voice_name}' sem 'model_id' em secrets.local.json.")
    if not isinstance(config.get("settings"), dict):
        raise VoiceGenError(f"Voz '{voice_name}' sem bloco 'settings' (objeto JSON).")


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #
def _fmt_size(n_bytes: int) -> str:
    if n_bytes >= 1024 * 1024:
        return f"{n_bytes / (1024 * 1024):.1f} MB"
    return f"{n_bytes / 1024:.0f} KB"


def slugify(text: str, max_len: int = 40) -> str:
    """Gera um nome de arquivo ASCII seguro a partir do texto (achata acentos, remove emojis)."""
    normalized = unicodedata.normalize("NFKD", text)
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii")
    cleaned = []
    for ch in ascii_text.lower():
        if ch.isalnum():
            cleaned.append(ch)
        elif ch in (" ", "-", "_"):
            cleaned.append("_")
    slug = "".join(cleaned).strip("_")
    while "__" in slug:
        slug = slug.replace("__", "_")
    slug = slug[:max_len].strip("_")
    return slug or "audio"


def _unique_path(path: Path) -> Path:
    """Evita sobrescrever: se o arquivo existir, adiciona _2, _3, ..."""
    if not path.exists():
        return path
    stem, suffix, parent = path.stem, path.suffix, path.parent
    counter = 2
    while True:
        candidate = parent / f"{stem}_{counter}{suffix}"
        if not candidate.exists():
            return candidate
        counter += 1


def _read_script_lines(file_path: str) -> list:
    """Le linhas nao-vazias de um arquivo de script (UTF-8)."""
    path = Path(file_path)
    if not path.exists():
        raise VoiceGenError(f"Arquivo --file nao encontrado: {file_path}")
    if not path.is_file():
        raise VoiceGenError(f"O caminho --file nao e um arquivo: {file_path}")
    try:
        raw = path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        raise VoiceGenError(f"Arquivo --file nao esta em UTF-8: {exc}")
    lines = [ln.strip() for ln in raw.splitlines() if ln.strip()]
    if not lines:
        raise VoiceGenError(f"Arquivo --file esta vazio (sem linhas com texto): {file_path}")
    return lines


def _read_doc_copy(doc_path: str) -> str:
    """
    Le um doc `_copy.md` (gerado por transcribe_video.py) e extrai SO o texto sob
    a secao `## Copy` (ate a proxima secao `## ` ou o fim do arquivo).
    """
    path = Path(doc_path)
    if not path.exists():
        raise VoiceGenError(f"Doc --doc nao encontrado: {doc_path}")
    if not path.is_file():
        raise VoiceGenError(f"O caminho --doc nao e um arquivo: {doc_path}")
    try:
        raw = path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        raise VoiceGenError(f"Doc --doc nao esta em UTF-8: {exc}")

    lines = raw.splitlines()
    start = None
    for i, ln in enumerate(lines):
        if ln.strip().lower() == "## copy":
            start = i + 1
            break
    if start is None:
        raise VoiceGenError(
            "Doc sem secao '## Copy'. Esperado o formato gerado por transcribe_video.py."
        )

    collected = []
    for ln in lines[start:]:
        if ln.strip().startswith("## "):
            break
        collected.append(ln)
    text = "\n".join(collected).strip()
    if not text:
        raise VoiceGenError(f"A secao '## Copy' do doc esta vazia: {doc_path}")
    return text


# --------------------------------------------------------------------------- #
# Core: geracao
# --------------------------------------------------------------------------- #
def generate(text: str, voice_config: dict, api_key: str, out_path: str,
             timeout: int = DEFAULT_TIMEOUT) -> str:
    """
    Gera um MP3 a partir de texto usando a API TTS do ElevenLabs.

    Args:
        text:         Texto a ser falado (nao vazio).
        voice_config: Dict com voice_id, model_id, settings.
        api_key:      Chave da API ElevenLabs.
        out_path:     Caminho de saida do .mp3.
        timeout:      Timeout da request em segundos.

    Returns:
        Caminho absoluto do .mp3 gerado.

    Raises:
        VoiceGenError: Em qualquer falha (texto vazio, rede, HTTP, escrita).
    """
    if not text or not text.strip():
        raise VoiceGenError("Texto vazio: nada para gerar.")

    voice_id = voice_config["voice_id"]
    url = f"{API_BASE}/{voice_id}?output_format={OUTPUT_FORMAT}"
    payload = {
        "text": text,
        "model_id": voice_config["model_id"],
        "voice_settings": voice_config["settings"],
    }
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")

    req = urllib.request.Request(url, data=body, method="POST")
    req.add_header("xi-api-key", api_key)
    req.add_header("Content-Type", "application/json")
    req.add_header("Accept", "audio/mpeg")

    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            audio = resp.read()
    except urllib.error.HTTPError as exc:
        raise VoiceGenError(_explain_http_error(exc))
    except urllib.error.URLError as exc:
        raise VoiceGenError(
            f"Falha de rede ao chamar ElevenLabs: {exc.reason}. "
            "Verifique sua conexao ou aumente o timeout."
        )
    except TimeoutError:
        raise VoiceGenError(f"Timeout ({timeout}s) ao gerar audio. Tente novamente.")

    if not audio:
        raise VoiceGenError("ElevenLabs retornou resposta vazia (0 bytes).")

    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    try:
        out.write_bytes(audio)
    except OSError as exc:
        raise VoiceGenError(f"Falha ao salvar o arquivo {out}: {exc}")

    return str(out.resolve())


def _explain_http_error(exc: urllib.error.HTTPError) -> str:
    """Traduz o codigo HTTP da API em mensagem acionavel."""
    try:
        detail = exc.read().decode("utf-8", errors="replace")[:400]
    except Exception:
        detail = ""
    code = exc.code
    if code == 401:
        return ("HTTP 401: API key invalida ou expirada. "
                "Confira 'elevenlabs_api_key' em secrets.local.json. " + detail)
    if code == 422:
        return (f"HTTP 422: texto ou parametros invalidos. "
                f"Cheque voice_id/model_id/settings. Detalhe: {detail}")
    if code == 429:
        return ("HTTP 429: limite de requisicoes ou de creditos atingido no ElevenLabs. "
                "Aguarde ou verifique seu plano. " + detail)
    return f"HTTP {code}: erro da API ElevenLabs. Detalhe: {detail}"


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #
def _run_single(text, voice_config, api_key, out_arg) -> int:
    out_path = _resolve_single_out(out_arg, text)
    print(f"Gerando: {text[:60]!r} ...")
    try:
        saved = generate(text, voice_config, api_key, str(out_path))
    except VoiceGenError as exc:
        print(f"[ERRO] {exc}", file=sys.stderr)
        return 1
    print(f"[OK] {saved} ({_fmt_size(os.path.getsize(saved))})")
    return 0


def _run_batch(lines, voice_config, api_key, out_arg) -> int:
    out_dir = _resolve_batch_dir(out_arg)
    out_dir.mkdir(parents=True, exist_ok=True)
    total = len(lines)
    ok = 0
    fails = []

    print(f"Lote: {total} linhas -> {out_dir}")
    for i, text in enumerate(lines, start=1):
        preview = text[:40] + ("..." if len(text) > 40 else "")
        print(f"[{i:03d}/{total:03d}] {preview!r} ... ", end="", flush=True)
        out_path = out_dir / f"{i:03d}.mp3"
        try:
            saved = generate(text, voice_config, api_key, str(out_path))
        except VoiceGenError as exc:
            print(f"FALHA: {exc}")
            fails.append((i, str(exc)))
            continue
        print(f"OK ({_fmt_size(os.path.getsize(saved))})")
        ok += 1

    print(f"\nResumo: {ok} geradas, {len(fails)} falhas.")
    if fails:
        print("Linhas com falha:")
        for idx, err in fails:
            print(f"  [{idx:03d}] {err}")
    return 0 if not fails else 1


def _resolve_single_out(out_arg, text) -> Path:
    """Resolve o caminho de saida no modo single (texto unico)."""
    slug = slugify(text)
    if out_arg is None:
        return _unique_path(DEFAULT_OUT_DIR / f"{slug}.mp3")
    out = Path(out_arg)
    if out.suffix.lower() == ".mp3":
        return out  # caminho de arquivo explicito: respeita (sobrescreve)
    return _unique_path(out / f"{slug}.mp3")  # tratado como diretorio


def _resolve_batch_dir(out_arg) -> Path:
    """Resolve o diretorio de saida no modo lote."""
    if out_arg is None:
        return DEFAULT_OUT_DIR
    out = Path(out_arg)
    if out.suffix.lower() == ".mp3":
        raise VoiceGenError(
            "No modo --file (lote), --out deve ser um DIRETORIO, nao um arquivo .mp3."
        )
    return out


def _run_doc(doc_path, voice_config, api_key, out_arg) -> int:
    try:
        text = _read_doc_copy(doc_path)
    except VoiceGenError as exc:
        print(f"[ERRO] {exc}", file=sys.stderr)
        return 1
    out_path = _resolve_doc_out(out_arg, doc_path)
    print(f"Doc: {Path(doc_path).name} -> {Path(out_path).name} ...")
    try:
        saved = generate(text, voice_config, api_key, str(out_path))
    except VoiceGenError as exc:
        print(f"[ERRO] {exc}", file=sys.stderr)
        return 1
    print(f"[OK] {saved} ({_fmt_size(os.path.getsize(saved))})")
    return 0


def _resolve_doc_out(out_arg, doc_path) -> Path:
    """
    Resolve a saida no modo --doc: `<stem>_voz.mp3` onde stem = nome do doc sem
    o sufixo `_copy`. Default: mesmo dir do doc.
    """
    doc = Path(doc_path)
    stem = doc.stem
    if stem.endswith("_copy"):
        stem = stem[: -len("_copy")]
    name = f"{stem}_voz.mp3"
    if out_arg is None:
        return doc.parent / name
    out = Path(out_arg)
    if out.suffix.lower() == ".mp3":
        return out
    return out / name


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Gera audio TTS via ElevenLabs a partir de texto ou de um script.",
    )
    parser.add_argument("text", nargs="?", help="Texto a falar (modo single).")
    parser.add_argument("--file", help="Arquivo de script: 1 mp3 por linha nao-vazia.")
    parser.add_argument("--doc", help="Doc _copy.md: voz da secao '## Copy' em 1 mp3.")
    parser.add_argument("--voice", help="Nome da voz no registro de secrets.local.json.")
    parser.add_argument("--out", help="Arquivo .mp3 (single/doc) ou diretorio (lote).")
    parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT,
                        help=f"Timeout da request em segundos (default {DEFAULT_TIMEOUT}).")
    args = parser.parse_args()

    modes = [bool(args.text), bool(args.file), bool(args.doc)]
    if sum(modes) != 1:
        parser.error("Informe exatamente UM: um texto, --file ou --doc.")

    try:
        secrets = load_secrets()
        _, voice_config = resolve_voice(secrets, args.voice)
    except VoiceGenError as exc:
        print(f"[ERRO] {exc}", file=sys.stderr)
        sys.exit(1)

    api_key = secrets["elevenlabs_api_key"]

    if args.doc:
        sys.exit(_run_doc(args.doc, voice_config, api_key, args.out))
    if args.file:
        try:
            lines = _read_script_lines(args.file)
        except VoiceGenError as exc:
            print(f"[ERRO] {exc}", file=sys.stderr)
            sys.exit(1)
        sys.exit(_run_batch(lines, voice_config, api_key, args.out))
    sys.exit(_run_single(args.text, voice_config, api_key, args.out))


if __name__ == "__main__":
    main()
