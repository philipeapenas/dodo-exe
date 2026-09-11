#!/usr/bin/env python3
"""
extract_audio.py: Extrai audio de video para clonagem de voz no ElevenLabs.

Uso:
    python extract_audio.py <video_path> [output.wav]

Saida:
    WAV mono, 44100 Hz, 16-bit PCM: formato otimo para ElevenLabs IVC.
"""

import os
import subprocess
import sys
from pathlib import Path


def _check_ffmpeg() -> None:
    try:
        subprocess.run(
            ["ffmpeg", "-version"],
            capture_output=True,
            timeout=5,
        )
    except FileNotFoundError:
        raise RuntimeError(
            "ffmpeg nao encontrado no PATH.\n"
            "Windows: baixe em https://www.gyan.dev/ffmpeg/builds/ e adicione ao PATH.\n"
            "Mac:     brew install ffmpeg\n"
            "Linux:   apt install ffmpeg"
        )


def _get_duration(audio_path: str) -> float:
    """Retorna duracao em segundos via ffprobe. Retorna 0.0 se ffprobe nao disponivel."""
    try:
        result = subprocess.run(
            [
                "ffprobe",
                "-v", "error",
                "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1",
                audio_path,
            ],
            capture_output=True,
            text=True,
            timeout=10,
        )
        return float(result.stdout.strip())
    except Exception:
        return 0.0


def _fmt_size(n_bytes: int) -> str:
    if n_bytes >= 1024 * 1024:
        return f"{n_bytes / (1024 * 1024):.1f} MB"
    return f"{n_bytes / 1024:.0f} KB"


def extract_audio(video_path: str, output_path=None) -> str:
    """
    Extrai audio de video no formato otimo para ElevenLabs Voice Cloning.

    Args:
        video_path:  Caminho do arquivo de video (mp4, mov, mkv, etc).
        output_path: Caminho de saida do WAV.
                     Default: mesmo diretorio do input, sufixo _voice.wav.

    Returns:
        Caminho absoluto do arquivo WAV gerado.

    Raises:
        FileNotFoundError: Se o video nao existir.
        RuntimeError: Se ffmpeg falhar ou nao estiver no PATH.
    """
    _check_ffmpeg()

    video = Path(video_path).resolve()
    if not video.exists():
        raise FileNotFoundError(f"Video nao encontrado: {video_path}")
    if not video.is_file():
        raise ValueError(f"O caminho nao e um arquivo: {video_path}")

    if output_path is None:
        output_path = str(video.parent / f"{video.stem}_voice.wav")

    output = Path(output_path).resolve()

    cmd = [
        "ffmpeg",
        "-i", str(video),
        "-vn",                # descarta stream de video
        "-ac", "1",           # converte para mono
        "-ar", "44100",       # sample rate 44.1 kHz
        "-sample_fmt", "s16", # 16-bit PCM
        str(output),
        "-y",                 # sobrescreve sem perguntar
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        tail = result.stderr[-600:] if result.stderr else "(sem saida)"
        raise RuntimeError(
            f"ffmpeg encerrou com codigo {result.returncode}:\n{tail}"
        )

    if not output.exists():
        raise RuntimeError(
            f"ffmpeg concluiu sem erros mas o arquivo nao foi criado: {output}"
        )

    return str(output)


def main() -> None:
    if len(sys.argv) < 2:
        print("Uso: python extract_audio.py <video_path> [output.wav]")
        print("Exemplo: python extract_audio.py modelo2.mp4")
        sys.exit(1)

    video_in = sys.argv[1]
    audio_out = sys.argv[2] if len(sys.argv) > 2 else None

    try:
        output = extract_audio(video_in, audio_out)
    except (FileNotFoundError, ValueError, RuntimeError) as exc:
        print(f"[ERRO] {exc}", file=sys.stderr)
        sys.exit(1)

    size_bytes = os.path.getsize(output)
    duration = _get_duration(output)

    print(f"[OK] {output}")
    print(f"     Duracao : {duration:.2f}s")
    print(f"     Tamanho : {_fmt_size(size_bytes)}")

    if 0 < duration < 60:
        print(
            f"\n[AVISO] Audio tem {duration:.0f}s: abaixo de 60s.\n"
            "         ElevenLabs aceita, mas 1min+ de audio limpo da resultados significativamente melhores.\n"
            "         Considere concatenar mais clips da mesma pessoa antes de subir."
        )


if __name__ == "__main__":
    main()
