#!/usr/bin/env python3
"""
transcribe_video.py: Transcreve video(s) via ElevenLabs Scribe (Speech-to-Text)
e salva a copy em um doc Markdown para revisao humana.

Fluxo do pipeline de voz (motion control):
    2_Final/<video>.mp4  ->  [transcribe_video.py]  ->  3_Voz/<video>_copy.md
                                                         (revisao humana)
                                                              |
                              generate_voice.py --doc <_copy.md>  ->  <video>_voz.mp3

Uso:
    py transcribe_video.py "<pasta 2_Final do dia>"      # lote: todos os videos
    py transcribe_video.py "<video.mp4>"                  # video unico
    py transcribe_video.py "<pasta>" --out "<dir>"        # diretorio de saida custom
    py transcribe_video.py "<pasta>" --lang por           # forca o idioma (default: auto)

Saida (default): pasta `3_Voz/` IRMA da pasta de entrada (ao lado da 2_Final).
"""

import argparse
import json
import os
import re
import sys
import tempfile
import unicodedata
import urllib.error
import urllib.request
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

# Importa o extrator de audio irmao (reuso, DRY). O dir do script entra no path
# para que o import funcione tanto como script quanto como modulo.
TOOLS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(TOOLS_DIR))
import extract_audio  # noqa: E402  (import apos manipular sys.path, intencional)

STT_URL = "https://api.elevenlabs.io/v1/speech-to-text"
STT_MODEL = "scribe_v1"
DEFAULT_TIMEOUT = 120
VIDEO_EXTS = {".mp4", ".mov", ".mkv", ".webm"}
SECRETS_PATH = TOOLS_DIR / "secrets.local.json"
BRASILIA = timezone(timedelta(hours=-3))

# Eventos de audio que o Scribe marca entre parenteses/colchetes. Lista
# conservadora: so removemos quando o conteudo inteiro for um destes (normalizado).
_EVENT_WORDS_RAW = {
    "silencio", "silêncio", "silence", "musica", "música", "music",
    "risos", "laughter", "applause", "aplausos",
    "inaudible", "inaudivel", "inaudível", "ruido", "ruído", "noise",
}


class TranscribeError(RuntimeError):
    """Erro de transcricao com mensagem amigavel (capturavel por item no lote)."""


# --------------------------------------------------------------------------- #
# Config
# --------------------------------------------------------------------------- #
def load_api_key(secrets_path=SECRETS_PATH) -> str:
    """Le apenas a elevenlabs_api_key de secrets.local.json (STT nao precisa de voices)."""
    path = Path(secrets_path)
    if not path.exists():
        raise TranscribeError(
            f"secrets.local.json nao encontrado em {path}. "
            "Crie o arquivo com o campo 'elevenlabs_api_key'."
        )
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise TranscribeError(f"secrets.local.json com JSON invalido: {exc}")
    key = data.get("elevenlabs_api_key", "") if isinstance(data, dict) else ""
    if not isinstance(key, str) or not key.strip():
        raise TranscribeError(
            "Campo 'elevenlabs_api_key' ausente ou vazio em secrets.local.json."
        )
    return key


# --------------------------------------------------------------------------- #
# Limpeza da transcricao
# --------------------------------------------------------------------------- #
def _normalize(text: str) -> str:
    return unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii").lower().strip()


_EVENT_WORDS_NORM = {_normalize(w) for w in _EVENT_WORDS_RAW}


def clean_transcript(text: str) -> str:
    """
    Remove marcadores de evento de audio entre () ou [] quando o conteudo inteiro
    e um evento conhecido (silencio, musica, risos, etc). Preserva parenteses com
    fala legitima. Depois normaliza espacos.
    """
    def _repl(match):
        inner = match.group(1) if match.group(1) is not None else match.group(2)
        if inner is not None and _normalize(inner) in _EVENT_WORDS_NORM:
            return ""
        return match.group(0)

    out = re.sub(r"\(([^)]*)\)|\[([^\]]*)\]", _repl, text)
    out = re.sub(r"\s+([.,!?…])", r"\1", out)  # remove espaco antes de pontuacao
    out = re.sub(r"[ \t]{2,}", " ", out)        # colapsa espacos
    return out.strip()


# --------------------------------------------------------------------------- #
# Scribe (STT)
# --------------------------------------------------------------------------- #
def _mp_field(boundary: str, name: str, value: str) -> bytes:
    return (f"--{boundary}\r\n"
            f'Content-Disposition: form-data; name="{name}"\r\n\r\n'
            f"{value}\r\n").encode("utf-8")


def _mp_file(boundary: str, name: str, filename: str, content: bytes, ctype: str) -> bytes:
    head = (f"--{boundary}\r\n"
            f'Content-Disposition: form-data; name="{name}"; filename="{filename}"\r\n'
            f"Content-Type: {ctype}\r\n\r\n").encode("utf-8")
    return head + content + b"\r\n"


def transcribe_audio(wav_path: str, api_key: str, language_code=None,
                     timeout: int = DEFAULT_TIMEOUT) -> dict:
    """
    Envia um arquivo de audio ao Scribe e retorna o JSON parseado
    (text, language_code, language_probability, words).
    """
    boundary = "----DodoBoundary" + uuid.uuid4().hex
    parts = [_mp_field(boundary, "model_id", STT_MODEL)]
    if language_code:
        parts.append(_mp_field(boundary, "language_code", language_code))
    with open(wav_path, "rb") as f:
        parts.append(_mp_file(boundary, "file", os.path.basename(wav_path), f.read(), "audio/wav"))
    body = b"".join(parts) + f"--{boundary}--\r\n".encode("utf-8")

    req = urllib.request.Request(STT_URL, data=body, method="POST")
    req.add_header("xi-api-key", api_key)
    req.add_header("Content-Type", f"multipart/form-data; boundary={boundary}")

    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        raise TranscribeError(_explain_http_error(exc))
    except urllib.error.URLError as exc:
        raise TranscribeError(
            f"Falha de rede ao chamar o Scribe: {exc.reason}. "
            "Verifique a conexao ou aumente o --timeout."
        )
    except TimeoutError:
        raise TranscribeError(f"Timeout ({timeout}s) na transcricao. Tente novamente.")


def _explain_http_error(exc: urllib.error.HTTPError) -> str:
    try:
        detail = exc.read().decode("utf-8", errors="replace")[:400]
    except Exception:
        detail = ""
    code = exc.code
    if code == 401:
        return ("HTTP 401: API key invalida ou expirada. "
                "Confira 'elevenlabs_api_key' em secrets.local.json. " + detail)
    if code == 422:
        return (f"HTTP 422: request invalida pro Scribe (arquivo ou parametros). "
                f"Detalhe: {detail}")
    if code == 429:
        return ("HTTP 429: limite de requisicoes ou creditos do ElevenLabs atingido. "
                "Aguarde ou verifique seu plano. " + detail)
    return f"HTTP {code}: erro da API Scribe. Detalhe: {detail}"


# --------------------------------------------------------------------------- #
# Core
# --------------------------------------------------------------------------- #
def transcribe_video(video_path: str, api_key: str, language_code=None,
                     timeout: int = DEFAULT_TIMEOUT) -> dict:
    """
    Extrai o audio de um video (WAV temporario), transcreve via Scribe e devolve
    {raw_text, text, language_code, language_probability}. Limpa o WAV temporario.

    Raises:
        TranscribeError: video inexistente, sem audio, transcricao vazia, falha de API.
    """
    video = Path(video_path)
    if not video.exists():
        raise TranscribeError(f"Video nao encontrado: {video}")
    if not video.is_file():
        raise TranscribeError(f"O caminho nao e um arquivo: {video}")

    tmp_wav = None
    try:
        fd, tmp_wav = tempfile.mkstemp(suffix=".wav", prefix="dodo_stt_")
        os.close(fd)
        try:
            extract_audio.extract_audio(str(video), tmp_wav)
        except (RuntimeError, FileNotFoundError, ValueError) as exc:
            raise TranscribeError(f"Falha ao extrair audio de '{video.name}': {exc}")
        data = transcribe_audio(tmp_wav, api_key, language_code, timeout)
    finally:
        if tmp_wav and os.path.exists(tmp_wav):
            try:
                os.remove(tmp_wav)
            except OSError:
                pass

    raw = (data.get("text") or "").strip()
    if not raw:
        raise TranscribeError(
            f"Transcricao vazia para '{video.name}' (o video tem fala audivel?)."
        )
    clean = clean_transcript(raw)
    if not clean:
        clean = raw  # tudo era tag de evento; preserva o original pra nao perder conteudo

    return {
        "raw_text": raw,
        "text": clean,
        "language_code": data.get("language_code", "?"),
        "language_probability": data.get("language_probability"),
    }


def write_copy_doc(video_path: str, result: dict, out_dir: str) -> Path:
    """Escreve `<stem>_copy.md` no out_dir seguindo o contrato com generate_voice.py."""
    video = Path(video_path)
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    doc_path = out / f"{video.stem}_copy.md"

    prob = result.get("language_probability")
    prob_str = f"{prob * 100:.0f}%" if isinstance(prob, (int, float)) else "?"
    gerado = datetime.now(BRASILIA).isoformat(timespec="seconds")

    content = (
        f"# Copy: {video.name}\n\n"
        f"- Origem: {video.name}\n"
        f"- Idioma: {result.get('language_code', '?')} ({prob_str})\n"
        f"- Gerado: {gerado}\n\n"
        f"## Copy\n\n"
        f"{result['text']}\n"
    )
    doc_path.write_text(content, encoding="utf-8")
    return doc_path


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #
def _collect_videos(input_path: str) -> list:
    p = Path(input_path)
    if not p.exists():
        raise TranscribeError(f"Caminho nao encontrado: {input_path}")
    if p.is_file():
        if p.suffix.lower() not in VIDEO_EXTS:
            raise TranscribeError(
                f"Arquivo nao e um video suportado ({', '.join(sorted(VIDEO_EXTS))}): {p.name}"
            )
        return [p]
    videos = sorted(f for f in p.iterdir() if f.is_file() and f.suffix.lower() in VIDEO_EXTS)
    if not videos:
        raise TranscribeError(
            f"Nenhum video ({', '.join(sorted(VIDEO_EXTS))}) na pasta: {input_path}"
        )
    return videos


def _resolve_out_dir(input_path: str, out_arg) -> Path:
    """Default: pasta `3_Voz/` irma da pasta de entrada (ou da pasta-pai do arquivo)."""
    if out_arg:
        return Path(out_arg)
    p = Path(input_path)
    base = p if p.is_dir() else p.parent
    return base.parent / "3_Voz"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Transcreve video(s) via ElevenLabs Scribe e salva a copy em .md.",
    )
    parser.add_argument("input", help="Video ou pasta (ex: a 2_Final do dia).")
    parser.add_argument("--out", help="Diretorio de saida (default: 3_Voz irma da entrada).")
    parser.add_argument("--lang", help="language_code (ex 'por'). Default: auto-detect.")
    parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT,
                        help=f"Timeout da request em segundos (default {DEFAULT_TIMEOUT}).")
    args = parser.parse_args()

    try:
        api_key = load_api_key()
        videos = _collect_videos(args.input)
        out_dir = _resolve_out_dir(args.input, args.out)
    except TranscribeError as exc:
        print(f"[ERRO] {exc}", file=sys.stderr)
        sys.exit(1)

    total = len(videos)
    ok = 0
    fails = []
    print(f"Transcrevendo {total} video(s) -> {out_dir}")
    for i, video in enumerate(videos, start=1):
        print(f"[{i:02d}/{total:02d}] {video.name} ... ", end="", flush=True)
        try:
            result = transcribe_video(str(video), api_key, args.lang, args.timeout)
            doc = write_copy_doc(str(video), result, str(out_dir))
        except TranscribeError as exc:
            print(f"FALHA: {exc}")
            fails.append((video.name, str(exc)))
            continue
        print(f"OK ({result['language_code']}) -> {doc.name}")
        ok += 1

    print(f"\nResumo: {ok} transcritos, {len(fails)} falhas.")
    if fails:
        print("Videos com falha:")
        for name, err in fails:
            print(f"  [{name}] {err}")
    sys.exit(0 if not fails else 1)


if __name__ == "__main__":
    main()
