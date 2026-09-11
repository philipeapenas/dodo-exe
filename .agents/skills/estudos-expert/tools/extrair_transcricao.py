#!/usr/bin/env python3
"""
extrair_transcricao.py - Entrega a fala crua de um estudo (video ou audio) em .txt.

Ordem de tentativa (a mais barata primeiro):
  1. Link do YouTube -> faixa de legenda do proprio YouTube (youtube_transcript_api).
     Gratis e instantaneo. E a MESMA fonte que o NotebookLM le (verificado 29/07/2026),
     por isso o NotebookLM nao entra neste pipeline.
  2. Sem legenda, --forcar-scribe, arquivo local, ou link que NAO e do YouTube
     (ex: call gravada no Google Drive) -> ElevenLabs Scribe, REUSANDO
     .agents/skills/voice-expert/tools/transcribe_video.py (Regra de Ouro 6: nao
     reimplementar transcricao que ja existe e ja foi validada no ecossistema).
     O audio e baixado pelo yt-dlp, que ja fala Google Drive, Vimeo e afins.

Uso:
    py extrair_transcricao.py "https://youtu.be/XXXXXXXX"
    py extrair_transcricao.py "https://drive.google.com/file/d/XXXX/view"
    py extrair_transcricao.py "C:\\caminho\\aula.mp4"
    py extrair_transcricao.py "https://youtu.be/XXXXXXXX" --forcar-scribe
    py extrair_transcricao.py "<entrada>" --out "<pasta>" --lang por --timeout 1800

Saida: <out>/<slug>.txt  (default: pasta output/ ao lado deste script)
Imprime FONTE=legenda|scribe, o caminho do .txt e o total de caracteres.

Pre-requisitos ja instalados na maquina do fundador:
    youtube_transcript_api, yt-dlp, ffmpeg (o Scribe precisa dos dois ultimos).
"""

import argparse
import glob
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

TOOLS_DIR = Path(__file__).resolve().parent
WORKSPACE = TOOLS_DIR.parents[3]  # .agents/skills/estudos-expert/tools -> raiz do workspace
VOICE_TOOLS = WORKSPACE / ".agents" / "skills" / "voice-expert" / "tools"
DEFAULT_OUT = TOOLS_DIR / "output"

IDIOMAS_PREFERIDOS = ["pt", "pt-BR", "pt-PT"]
MIDIA_EXTS = {".mp4", ".mov", ".mkv", ".webm", ".mp3", ".m4a", ".wav", ".ogg", ".aac"}

# O YouTube bloqueia por IP a leitura de legenda do youtube_transcript_api (erro 429) e
# tambem o cliente web do yt-dlp. Os clientes de app continuam respondendo.
YTDLP_CLIENTES = "youtube:player_client=android,web"


class ExtracaoError(RuntimeError):
    """Erro com mensagem amigavel para o agente reportar ao fundador."""


# --------------------------------------------------------------------------- #
# Entrada
# --------------------------------------------------------------------------- #
def eh_url(entrada: str) -> bool:
    return entrada.strip().lower().startswith(("http://", "https://", "www."))


def eh_youtube(url: str) -> bool:
    """Apenas o YouTube tem faixa de legenda pra tentar antes do Scribe."""
    return re.search(r"(youtube\.com|youtu\.be)", url, re.IGNORECASE) is not None


def extrair_video_id(url: str) -> str:
    """Aceita youtu.be/ID, watch?v=ID, /shorts/ID e /embed/ID."""
    padroes = [
        r"youtu\.be/([A-Za-z0-9_-]{6,})",
        r"[?&]v=([A-Za-z0-9_-]{6,})",
        r"/shorts/([A-Za-z0-9_-]{6,})",
        r"/embed/([A-Za-z0-9_-]{6,})",
    ]
    for p in padroes:
        m = re.search(p, url)
        if m:
            return m.group(1)
    raise ExtracaoError(
        f"Nao consegui achar o ID do video nesta URL: {url}\n"
        "Formatos aceitos: youtu.be/ID, youtube.com/watch?v=ID, /shorts/ID, /embed/ID."
    )


def slugificar(texto: str) -> str:
    limpo = re.sub(r"[^A-Za-z0-9_-]+", "_", texto).strip("_")
    return limpo[:80] or "transcricao"


# --------------------------------------------------------------------------- #
# Caminho 1: legenda do YouTube (gratis)
# --------------------------------------------------------------------------- #
def buscar_legenda(video_id: str) -> str:
    """
    Devolve a fala crua da faixa de legenda. Tenta portugues; se nao houver,
    cai para a primeira faixa disponivel (o agente decide se serve).
    Levanta ExtracaoError quando o video nao tem legenda nenhuma.
    """
    try:
        from youtube_transcript_api import YouTubeTranscriptApi
    except ImportError:
        raise ExtracaoError(
            "Biblioteca youtube_transcript_api nao instalada. "
            "Rode: pip install youtube-transcript-api"
        )

    api = YouTubeTranscriptApi()

    # v1.x expoe metodos de instancia (fetch/list). v0.x expunha classmethods.
    if hasattr(api, "fetch"):
        try:
            trechos = api.fetch(video_id, languages=IDIOMAS_PREFERIDOS)
        except Exception:
            try:
                faixas = list(api.list(video_id))
            except Exception as exc:
                raise ExtracaoError(f"Video sem legenda disponivel ({exc}).")
            if not faixas:
                raise ExtracaoError("Video sem legenda disponivel.")
            trechos = faixas[0].fetch()
        return " ".join(t.text.replace("\n", " ") for t in trechos).strip()

    try:
        trechos = YouTubeTranscriptApi.get_transcript(
            video_id, languages=IDIOMAS_PREFERIDOS
        )
    except Exception as exc:
        raise ExtracaoError(f"Video sem legenda disponivel ({exc}).")
    return " ".join(t["text"].replace("\n", " ") for t in trechos).strip()


# --------------------------------------------------------------------------- #
# Caminho 1b: legenda pelo yt-dlp (gratis, quando a API cai por bloqueio de IP)
# --------------------------------------------------------------------------- #
def _texto_do_json3(caminho: Path) -> str:
    """Converte a legenda json3 do YouTube em fala corrida."""
    import json

    dados = json.loads(caminho.read_text(encoding="utf-8"))
    partes = []
    for evento in dados.get("events", []):
        trecho = "".join(seg.get("utf8", "") for seg in evento.get("segs", []))
        trecho = trecho.replace("\n", " ").strip()
        if trecho:
            partes.append(trecho)
    return " ".join(partes).strip()


def buscar_legenda_ytdlp(url: str) -> str:
    """
    Mesma faixa de legenda, baixada pelo yt-dlp em vez da API bloqueada.
    Prefere portugues; cai para ingles se o video nao tiver faixa em portugues.
    """
    with tempfile.TemporaryDirectory(prefix="dodo_legenda_") as tmp:
        pasta = Path(tmp)
        cmd = [
            sys.executable, "-m", "yt_dlp",
            "--skip-download", "--write-subs", "--write-auto-subs",
            "--sub-langs", "pt.*,en.*", "--sub-format", "json3",
            "--extractor-args", YTDLP_CLIENTES,
            "-o", str(pasta / "%(id)s"), url,
        ]
        subprocess.run(cmd, capture_output=True, text=True)
        arquivos = sorted(pasta.glob("*.json3"))
        if not arquivos:
            raise ExtracaoError("yt-dlp tambem nao trouxe faixa de legenda.")
        # 'pt-orig' e a fala original; qualquer 'pt' vem antes de 'en'.
        arquivos.sort(key=lambda p: (0 if ".pt" in p.name else 1, 0 if "orig" in p.name else 1))
        texto = _texto_do_json3(arquivos[0])
        if not texto:
            raise ExtracaoError("Faixa de legenda baixada veio vazia.")
        return texto


# --------------------------------------------------------------------------- #
# Caminho 2: Scribe (reuso da voice-expert)
# --------------------------------------------------------------------------- #
def baixar_audio(url: str, destino: Path) -> Path:
    """Baixa a melhor faixa de audio do video via yt-dlp. Devolve o arquivo baixado."""
    modelo = str(destino / "%(id)s.%(ext)s")
    cmd = [sys.executable, "-m", "yt_dlp", "-f", "bestaudio",
           "--extractor-args", YTDLP_CLIENTES, "-o", modelo, url]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        raise ExtracaoError(
            "Falha ao baixar o audio com yt-dlp.\n"
            f"Saida: {(proc.stderr or proc.stdout or '').strip()[:500]}"
        )
    baixados = [Path(p) for p in glob.glob(str(destino / "*")) if Path(p).is_file()]
    if not baixados:
        raise ExtracaoError("yt-dlp terminou sem erro, mas nao gerou arquivo de audio.")
    return max(baixados, key=lambda p: p.stat().st_size)


def transcrever_scribe(caminho_midia: Path, lang: str, timeout: int) -> str:
    """Transcreve via ElevenLabs Scribe reusando o tool da voice-expert."""
    if not VOICE_TOOLS.exists():
        raise ExtracaoError(
            f"Tools da voice-expert nao encontrados em {VOICE_TOOLS}. "
            "Sem eles nao ha fallback de transcricao."
        )
    sys.path.insert(0, str(VOICE_TOOLS))
    try:
        import transcribe_video as tv
    except ImportError as exc:
        raise ExtracaoError(f"Nao consegui importar o transcribe_video da voice-expert: {exc}")

    try:
        chave = tv.load_api_key()
        resultado = tv.transcribe_video(
            str(caminho_midia), chave, language_code=lang, timeout=timeout
        )
    except tv.TranscribeError as exc:
        raise ExtracaoError(str(exc))
    return (resultado.get("text") or "").strip()


# --------------------------------------------------------------------------- #
# Orquestracao
# --------------------------------------------------------------------------- #
def extrair(entrada: str, forcar_scribe: bool, lang: str, timeout: int) -> tuple:
    """Devolve (texto, fonte, slug). fonte = 'legenda' ou 'scribe'."""
    if eh_url(entrada):
        if eh_youtube(entrada) and not forcar_scribe:
            video_id = extrair_video_id(entrada)
            try:
                return buscar_legenda(video_id), "legenda", video_id
            except ExtracaoError as exc:
                print(f"[aviso] Legenda indisponivel pela API: {exc}", file=sys.stderr)
                print("[aviso] Tentando a mesma legenda pelo yt-dlp (ainda de graca).",
                      file=sys.stderr)
                try:
                    return buscar_legenda_ytdlp(entrada), "legenda", video_id
                except ExtracaoError as exc2:
                    print(f"[aviso] {exc2}", file=sys.stderr)
                print("[aviso] Caindo para o Scribe (consome credito ElevenLabs).",
                      file=sys.stderr)
        elif not eh_youtube(entrada):
            print("[aviso] Link fora do YouTube (sem legenda pra ler). "
                  "Vou baixar o audio e transcrever no Scribe (consome credito).",
                  file=sys.stderr)
        with tempfile.TemporaryDirectory(prefix="dodo_estudo_") as tmp:
            audio = baixar_audio(entrada, Path(tmp))
            return transcrever_scribe(audio, lang, timeout), "scribe", slugificar(audio.stem)

    midia = Path(entrada).expanduser()
    if not midia.exists():
        raise ExtracaoError(f"Arquivo nao encontrado: {midia}")
    if not midia.is_file():
        raise ExtracaoError(f"O caminho nao e um arquivo: {midia}")
    if midia.suffix.lower() not in MIDIA_EXTS:
        raise ExtracaoError(
            f"Extensao '{midia.suffix}' nao suportada. "
            f"Esta skill trata video e audio: {', '.join(sorted(MIDIA_EXTS))}"
        )
    return transcrever_scribe(midia, lang, timeout), "scribe", slugificar(midia.stem)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Extrai a fala crua de um estudo (link do YouTube ou arquivo local)."
    )
    parser.add_argument("entrada", help="Link do YouTube ou caminho de video/audio local")
    parser.add_argument("--forcar-scribe", action="store_true",
                        help="Ignora a legenda e transcreve via ElevenLabs Scribe")
    parser.add_argument("--out", default=str(DEFAULT_OUT),
                        help="Pasta de saida do .txt (default: tools/output/)")
    parser.add_argument("--lang", default="por",
                        help="Idioma para o Scribe em ISO-639-3 (default: por)")
    parser.add_argument("--timeout", type=int, default=1800,
                        help="Timeout da request ao Scribe em segundos (default: 1800). "
                             "Aula longa sobe um WAV grande e precisa de folga.")
    args = parser.parse_args()

    try:
        texto, fonte, slug = extrair(args.entrada, args.forcar_scribe, args.lang, args.timeout)
    except ExtracaoError as exc:
        print(f"ERRO: {exc}", file=sys.stderr)
        sys.exit(1)

    if not texto:
        print("ERRO: transcricao veio vazia.", file=sys.stderr)
        sys.exit(1)

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    destino = out_dir / f"{slug}.txt"
    destino.write_text(texto, encoding="utf-8")

    print(f"FONTE={fonte}")
    print(f"ARQUIVO={destino}")
    print(f"CARACTERES={len(texto)}")
    if fonte == "legenda":
        print("NOTA=legenda automatica erra palavra (nome proprio, termo tecnico). "
              "Limpe o erro obvio dentro da citacao, sem mudar o sentido.")


if __name__ == "__main__":
    main()
