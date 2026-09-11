#!/usr/bin/env python3
"""
finalize_video.py: Estagio 8 do pipeline de motion content.

Pega o video do 4_LipSync (rosto+movimento+voz+lip-sync) e produz o ENTREGAVEL
no 5_Final, em UMA passada de ffmpeg:
  1. CROP da marca d'agua da RunningHub (canto superior): corta a faixa de cima,
     recorta a largura proporcional pra MANTER o 9:16 (sem distorcer) e reescala
     pra dimensao original (efeito de zoom limpo).
  2. SOM AMBIENTE: mixa um audio de fundo (ventilador) em volume baixo SOB a voz
     ja existente no video (normalize=0 pra a voz nao cair pela metade).

Uso:
    # Completo (Estagio 8): crop da marca + som ambiente
    py finalize_video.py <video_ou_pasta_4_LipSync> --fundo <audio>
    py finalize_video.py <pasta> --fundo fan.m4a --vol 0.15 --crop-top 0.08

    # So limpar a marca do motion CRU aprovado (sem voz/som): Conta N/output -> _limpo/
    py finalize_video.py "<...\\Conta 1\\output>" --crop-only
    py finalize_video.py "<...\\Conta 1\\output>" --crop-only --crop-top 0.10

Saida (default): `5_Final/` irma da entrada (completo); `_limpo/` dentro da entrada (--crop-only).
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path

VIDEO_EXTS = {".mp4", ".mov", ".mkv", ".webm"}
DEFAULT_VOL = 0.30   # som ambiente sob a voz (0.15 ficou baixo no teste); tunavel via --vol
DEFAULT_CROP_TOP = 0.08
DEFAULT_CROP_BOTTOM = 0.0


class FinalizeError(RuntimeError):
    """Erro de finalizacao com mensagem amigavel (capturavel por item no lote)."""


# --------------------------------------------------------------------------- #
# Helpers ffmpeg/ffprobe
# --------------------------------------------------------------------------- #
def _check_ffmpeg() -> None:
    try:
        subprocess.run(["ffmpeg", "-version"], capture_output=True, timeout=5)
    except FileNotFoundError:
        raise FinalizeError(
            "ffmpeg nao encontrado no PATH.\n"
            "Windows: baixe em https://www.gyan.dev/ffmpeg/builds/ e adicione ao PATH."
        )


def _get_dimensions(video_path: str) -> tuple:
    """Retorna (width, height) do primeiro stream de video via ffprobe."""
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0",
         "-show_entries", "stream=width,height", "-of", "csv=p=0:s=x", video_path],
        capture_output=True, text=True, timeout=15,
    )
    out = result.stdout.strip()
    try:
        w_str, h_str = out.split("x")
        return int(w_str), int(h_str)
    except (ValueError, AttributeError):
        raise FinalizeError(f"Nao consegui ler a dimensao do video (ffprobe='{out}').")


def _has_audio(video_path: str) -> bool:
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "a",
         "-show_entries", "stream=index", "-of", "csv=p=0", video_path],
        capture_output=True, text=True, timeout=15,
    )
    return bool(result.stdout.strip())


def _get_duration(path: str) -> float:
    try:
        result = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "default=noprint_wrappers=1:nokey=1", path],
            capture_output=True, text=True, timeout=10,
        )
        return float(result.stdout.strip())
    except Exception:
        return 0.0


def _even(n: int) -> int:
    """Arredonda para baixo no inteiro par mais proximo (libx264 exige dimensoes pares)."""
    n = int(n)
    return n - (n % 2)


def _fmt_size(n_bytes: int) -> str:
    if n_bytes >= 1024 * 1024:
        return f"{n_bytes / (1024 * 1024):.1f} MB"
    return f"{n_bytes / 1024:.0f} KB"


# --------------------------------------------------------------------------- #
# Core
# --------------------------------------------------------------------------- #
def _crop_geometry(w: int, h: int, crop_top: float, crop_bottom: float) -> tuple:
    """
    Geometria do crop anti-marca preservando o aspecto (9:16): largura e altura
    encolhem pelo MESMO fator, cortando a faixa do topo (onde fica a marca) e
    centralizando na horizontal. Retorna (crop_w, crop_h, crop_x, crop_y) pares.
    """
    factor = 1.0 - crop_top - crop_bottom
    crop_w = _even(w * factor)
    crop_h = _even(h * factor)
    crop_x = _even((w - crop_w) / 2)
    crop_y = _even(h * crop_top)
    if crop_y + crop_h > h:               # clamp defensivo
        crop_y = _even(h - crop_h)
    if crop_w <= 0 or crop_h <= 0:
        raise FinalizeError("Crop resultou em dimensao zero; reduza --crop-top/--crop-bottom.")
    return crop_w, crop_h, crop_x, crop_y


def finalize(video_path: str, fundo_path: str, out_path: str,
             vol: float = DEFAULT_VOL, crop_top: float = DEFAULT_CROP_TOP,
             crop_bottom: float = DEFAULT_CROP_BOTTOM) -> str:
    """
    Aplica crop (anti-marca-d'agua, preservando aspecto) + mix de som ambiente.

    Args:
        video_path:  Video do 4_LipSync (precisa ter faixa de audio = a voz).
        fundo_path:  Audio ambiente (ex: ventilador). Loopado se mais curto que o video.
        out_path:    Caminho de saida do .mp4.
        vol:         Volume do fundo (0.0-1.0, default 0.15).
        crop_top:    Fracao da altura cortada do TOPO (default 0.08).
        crop_bottom: Fracao cortada de baixo (default 0.0).

    Returns:
        Caminho absoluto do .mp4 gerado.

    Raises:
        FinalizeError: ffmpeg ausente, arquivos invalidos, crop invalido, falha de encode.
    """
    _check_ffmpeg()

    video = Path(video_path)
    if not video.exists() or not video.is_file():
        raise FinalizeError(f"Video nao encontrado: {video_path}")
    fundo = Path(fundo_path)
    if not fundo.exists() or not fundo.is_file():
        raise FinalizeError(f"Audio de fundo nao encontrado: {fundo_path}")

    if crop_top < 0 or crop_bottom < 0 or (crop_top + crop_bottom) >= 1:
        raise FinalizeError(
            f"Crop invalido: top({crop_top}) + bottom({crop_bottom}) deve ser < 1 e nao negativo."
        )
    if not 0 <= vol <= 4:
        raise FinalizeError(f"Volume invalido: {vol} (use algo entre 0.0 e ~1.0).")
    if not _has_audio(str(video)):
        raise FinalizeError(
            f"'{video.name}' nao tem faixa de audio (a voz). O 4_LipSync deveria ter."
        )

    w, h = _get_dimensions(str(video))
    crop_w, crop_h, crop_x, crop_y = _crop_geometry(w, h, crop_top, crop_bottom)

    filter_complex = (
        f"[0:v]crop={crop_w}:{crop_h}:{crop_x}:{crop_y},scale={w}:{h}[v];"
        f"[1:a]volume={vol}[bg];"
        f"[0:a][bg]amix=inputs=2:duration=first:normalize=0[a]"
    )

    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)

    cmd = [
        "ffmpeg", "-y",
        "-i", str(video),
        "-stream_loop", "-1", "-i", str(fundo),   # loopa o fundo se for mais curto
        "-filter_complex", filter_complex,
        "-map", "[v]", "-map", "[a]",
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "medium", "-crf", "18",
        "-c:a", "aac", "-b:a", "192k",
        "-shortest",
        str(out),
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        tail = result.stderr[-800:] if result.stderr else "(sem saida)"
        raise FinalizeError(f"ffmpeg encerrou com codigo {result.returncode}:\n{tail}")
    if not out.exists():
        raise FinalizeError(f"ffmpeg concluiu sem erro mas o arquivo nao foi criado: {out}")

    return str(out.resolve())


def crop_watermark(video_path: str, out_path: str,
                   crop_top: float = DEFAULT_CROP_TOP,
                   crop_bottom: float = DEFAULT_CROP_BOTTOM) -> str:
    """
    Remove SO a marca d'agua do RunningHub (faixa do topo), preservando o 9:16.
    Nao mistura som ambiente nem exige voz: copia a faixa de audio original (a voz
    errada da referencia, que sera trocada nas etapas de voz). Usado pra dar uma
    limpada rapida no motion CRU aprovado, antes de seguir pro pipeline de voz.

    Args:
        video_path:  Video cru do motion (Conta N/output).
        out_path:    Caminho de saida do .mp4.
        crop_top:    Fracao da altura cortada do TOPO (default 0.08).
        crop_bottom: Fracao cortada de baixo (default 0.0).

    Returns:
        Caminho absoluto do .mp4 gerado.

    Raises:
        FinalizeError: ffmpeg ausente, arquivo invalido, crop invalido, falha de encode.
    """
    _check_ffmpeg()

    video = Path(video_path)
    if not video.exists() or not video.is_file():
        raise FinalizeError(f"Video nao encontrado: {video_path}")
    if crop_top < 0 or crop_bottom < 0 or (crop_top + crop_bottom) >= 1:
        raise FinalizeError(
            f"Crop invalido: top({crop_top}) + bottom({crop_bottom}) deve ser < 1 e nao negativo."
        )

    w, h = _get_dimensions(str(video))
    crop_w, crop_h, crop_x, crop_y = _crop_geometry(w, h, crop_top, crop_bottom)

    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)

    cmd = [
        "ffmpeg", "-y", "-i", str(video),
        "-vf", f"crop={crop_w}:{crop_h}:{crop_x}:{crop_y},scale={w}:{h}",
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "medium", "-crf", "18",
    ]
    cmd += ["-c:a", "copy"] if _has_audio(str(video)) else ["-an"]
    cmd.append(str(out))

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        tail = result.stderr[-800:] if result.stderr else "(sem saida)"
        raise FinalizeError(f"ffmpeg encerrou com codigo {result.returncode}:\n{tail}")
    if not out.exists():
        raise FinalizeError(f"ffmpeg concluiu sem erro mas o arquivo nao foi criado: {out}")

    return str(out.resolve())


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #
def _collect_videos(input_path: str) -> list:
    p = Path(input_path)
    if not p.exists():
        raise FinalizeError(f"Caminho nao encontrado: {input_path}")
    if p.is_file():
        if p.suffix.lower() not in VIDEO_EXTS:
            raise FinalizeError(
                f"Arquivo nao e video suportado ({', '.join(sorted(VIDEO_EXTS))}): {p.name}"
            )
        return [p]
    videos = sorted(f for f in p.iterdir() if f.is_file() and f.suffix.lower() in VIDEO_EXTS)
    if not videos:
        raise FinalizeError(
            f"Nenhum video ({', '.join(sorted(VIDEO_EXTS))}) na pasta: {input_path}"
        )
    return videos


def _resolve_out_dir(input_path: str, out_arg, crop_only: bool = False) -> Path:
    """
    Default no modo completo: pasta `5_Final/` irma da entrada.
    Default no modo --crop-only: subpasta `_limpo/` dentro da propria entrada.
    """
    if out_arg:
        return Path(out_arg)
    p = Path(input_path)
    base = p if p.is_dir() else p.parent
    return (base / "_limpo") if crop_only else (base.parent / "5_Final")


def _out_name(video: Path, crop_only: bool = False) -> str:
    stem = video.stem
    if crop_only:
        return f"{stem}_limpo.mp4"
    if stem.endswith("_lipsync"):
        stem = stem[: -len("_lipsync")]
    return f"{stem}_final.mp4"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Crop da marca d'agua RunningHub (+ som ambiente no modo completo).",
    )
    parser.add_argument("input", help="Video ou pasta (4_LipSync no modo completo; Conta N/output no --crop-only).")
    parser.add_argument("--crop-only", action="store_true",
                        help="So remove a marca d'agua do topo (crop 9:16), sem voz/som ambiente. "
                             "Pra limpar o motion CRU aprovado. Nao precisa de --fundo.")
    parser.add_argument("--fundo", help="Audio ambiente (ex: ventilador .m4a). Obrigatorio no modo completo.")
    parser.add_argument("--out", help="Diretorio de saida (default: 5_Final; ou _limpo/ no --crop-only).")
    parser.add_argument("--vol", type=float, default=DEFAULT_VOL,
                        help=f"Volume do fundo (default {DEFAULT_VOL}).")
    parser.add_argument("--crop-top", type=float, default=DEFAULT_CROP_TOP,
                        help=f"Fracao cortada do topo (default {DEFAULT_CROP_TOP}).")
    parser.add_argument("--crop-bottom", type=float, default=DEFAULT_CROP_BOTTOM,
                        help=f"Fracao cortada de baixo (default {DEFAULT_CROP_BOTTOM}).")
    args = parser.parse_args()

    if not args.crop_only and not args.fundo:
        parser.error("--fundo e obrigatorio no modo completo. Use --crop-only pra so tirar a marca.")

    try:
        videos = _collect_videos(args.input)
        out_dir = _resolve_out_dir(args.input, args.out, args.crop_only)
    except FinalizeError as exc:
        print(f"[ERRO] {exc}", file=sys.stderr)
        sys.exit(1)

    total = len(videos)
    ok = 0
    fails = []
    modo = "Limpando marca (crop-only)" if args.crop_only else "Finalizando"
    print(f"{modo} {total} video(s) -> {out_dir}")
    for i, video in enumerate(videos, start=1):
        print(f"[{i:02d}/{total:02d}] {video.name} ... ", end="", flush=True)
        out_path = out_dir / _out_name(video, args.crop_only)
        try:
            if args.crop_only:
                saved = crop_watermark(str(video), str(out_path),
                                       args.crop_top, args.crop_bottom)
            else:
                saved = finalize(str(video), args.fundo, str(out_path),
                                 args.vol, args.crop_top, args.crop_bottom)
        except FinalizeError as exc:
            print(f"FALHA: {exc}")
            fails.append((video.name, str(exc)))
            continue
        dur = _get_duration(saved)
        print(f"OK ({dur:.1f}s, {_fmt_size(os.path.getsize(saved))}) -> {Path(saved).name}")
        ok += 1

    verbo = "limpos" if args.crop_only else "finalizados"
    print(f"\nResumo: {ok} {verbo}, {len(fails)} falhas.")
    if fails:
        print("Videos com falha:")
        for name, err in fails:
            print(f"  [{name}] {err}")
    sys.exit(0 if not fails else 1)


if __name__ == "__main__":
    main()
