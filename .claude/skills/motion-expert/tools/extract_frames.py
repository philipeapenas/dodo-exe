"""
extract_frames.py - Etapa 2 do processo Faceswap + Motion Control.

Extrai 1 frame (~t=1s por padrao) de cada video .mp4 de uma pasta de entrada
e salva como PNG (mesmo nome do video) na pasta de saida.

Semente do futuro CLI da skill faceswap-pipeline. Programacao defensiva:
- Ignora nao-videos (ex: desktop.ini).
- Se o video for mais curto que o timestamp pedido, cai para o meio do video
  (evita PNG preto/vazio do t=0 e evita falha do ffmpeg passando do fim).
- Idempotente: pula PNG ja existente, a menos que --overwrite.
- Loga geração, skip, fallback e erro; ao final imprime um resumo.

Uso:
    python extract_frames.py
    python extract_frames.py --input "<pasta_videos>" --output "<pasta_pngs>" --timestamp 1.0
    python extract_frames.py --overwrite
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path

DEFAULT_TIMESTAMP = 1.0

VIDEO_EXTS = {".mp4", ".mov", ".mkv", ".avi", ".webm"}


def probe_duration(video: Path):
    """Retorna a duracao do video em segundos (float) ou None se nao der pra medir."""
    try:
        out = subprocess.run(
            [
                "ffprobe", "-v", "error",
                "-show_entries", "format=duration",
                "-of", "json", str(video),
            ],
            capture_output=True, text=True, timeout=60,
        )
        if out.returncode != 0:
            return None
        dur = json.loads(out.stdout).get("format", {}).get("duration")
        return float(dur) if dur is not None else None
    except (subprocess.SubprocessError, ValueError, json.JSONDecodeError):
        return None


def extract_one(video: Path, dest: Path, timestamp: float):
    """
    Extrai 1 frame do video para dest (PNG).
    Retorna (status, seek_usado) onde status in {"ok", "fallback", "error"}.
    """
    duration = probe_duration(video)

    seek = timestamp
    status = "ok"
    # Se nao sabemos a duracao, tentamos o timestamp pedido mesmo assim.
    if duration is not None and duration <= timestamp:
        # Video curto demais: pega o meio (frame mais seguro que t=0).
        seek = round(duration / 2, 3)
        status = "fallback"

    try:
        run = subprocess.run(
            [
                "ffmpeg", "-y",
                "-ss", str(seek),
                "-i", str(video),
                "-frames:v", "1",
                str(dest),
            ],
            capture_output=True, text=True, timeout=120,
        )
    except subprocess.SubprocessError as exc:
        print(f"  [ERRO] {video.name}: subprocess falhou ({exc})")
        return "error", seek

    if run.returncode != 0 or not dest.exists() or dest.stat().st_size == 0:
        # Fallback final: tenta t=0 caso o seek tenha estourado o fim do video.
        if seek != 0:
            subprocess.run(
                ["ffmpeg", "-y", "-ss", "0", "-i", str(video),
                 "-frames:v", "1", str(dest)],
                capture_output=True, text=True, timeout=120,
            )
            if dest.exists() and dest.stat().st_size > 0:
                return "fallback", 0
        tail = (run.stderr or "").strip().splitlines()[-1:] or [""]
        print(f"  [ERRO] {video.name}: ffmpeg nao gerou frame valido -> {tail[0]}")
        return "error", seek

    return status, seek


def main():
    parser = argparse.ArgumentParser(description="Extrai 1 frame por video (Etapa 2 Faceswap).")
    parser.add_argument("--input", required=True, help="Pasta com os videos.")
    parser.add_argument("--output", required=True, help="Pasta destino dos PNGs.")
    parser.add_argument("--timestamp", type=float, default=DEFAULT_TIMESTAMP,
                        help="Segundo do frame a extrair (default 1.0).")
    parser.add_argument("--overwrite", action="store_true",
                        help="Reprocessa mesmo se o PNG ja existir.")
    args = parser.parse_args()

    in_dir = Path(args.input)
    out_dir = Path(args.output)

    if not in_dir.is_dir():
        print(f"[FATAL] Pasta de entrada nao existe: {in_dir}")
        sys.exit(1)
    out_dir.mkdir(parents=True, exist_ok=True)

    videos = sorted(p for p in in_dir.iterdir()
                    if p.is_file() and p.suffix.lower() in VIDEO_EXTS)
    if not videos:
        print(f"[FATAL] Nenhum video encontrado em: {in_dir}")
        sys.exit(1)

    print(f"Encontrados {len(videos)} videos. Frame em t={args.timestamp}s.\n")

    counts = {"ok": 0, "fallback": 0, "skip": 0, "error": 0}
    fallbacks, errors = [], []

    for video in videos:
        dest = out_dir / (video.stem + ".png")
        if dest.exists() and not args.overwrite:
            print(f"  [SKIP] {dest.name} ja existe")
            counts["skip"] += 1
            continue

        status, seek = extract_one(video, dest, args.timestamp)
        counts[status] += 1
        if status == "ok":
            print(f"  [OK]   {dest.name} (t={seek}s)")
        elif status == "fallback":
            print(f"  [FALL] {dest.name} (video curto -> t={seek}s)")
            fallbacks.append(video.name)
        else:
            errors.append(video.name)

    print("\n=== RESUMO ===")
    print(f"  Gerados OK : {counts['ok']}")
    print(f"  Fallback   : {counts['fallback']}  {fallbacks if fallbacks else ''}")
    print(f"  Pulados    : {counts['skip']}")
    print(f"  Erros      : {counts['error']}  {errors if errors else ''}")
    print(f"  Saida      : {out_dir}")

    sys.exit(1 if counts["error"] else 0)


if __name__ == "__main__":
    main()
