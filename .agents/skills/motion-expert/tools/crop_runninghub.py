#!/usr/bin/env python3
"""
crop_runninghub.py - Ferramenta utilitaria para o motion-expert.

Remove a marca d'agua da RunningHub (canto superior) fazendo um crop 
proporcional que mantem a proporcao original do video (efeito de zoom limpo),
sem necessitar adicionar fundo musical (diferente do finalize_video.py).

Uso:
    py crop_runninghub.py <video>
    py crop_runninghub.py <video> --crop-top 0.08
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path

VIDEO_EXTS = {".mp4", ".mov", ".mkv", ".webm"}
DEFAULT_CROP_TOP = 0.08

class CropError(RuntimeError):
    pass

def _check_ffmpeg():
    try:
        subprocess.run(["ffmpeg", "-version"], capture_output=True, timeout=5)
    except FileNotFoundError:
        raise CropError("ffmpeg nao encontrado no PATH.")

def _get_dimensions(video_path: str) -> tuple:
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0",
         "-show_entries", "stream=width,height", "-of", "csv=p=0:s=x", video_path],
        capture_output=True, text=True, timeout=15,
    )
    out = result.stdout.strip()
    try:
        w_str, h_str = out.split("x")
        return int(w_str), int(h_str)
    except ValueError:
        raise CropError(f"Nao consegui ler dimensao de {video_path}")

def _even(n: int) -> int:
    n = int(n)
    return n - (n % 2)

def crop_video(video_path: str, out_path: str, crop_top: float) -> str:
    _check_ffmpeg()
    
    video = Path(video_path)
    if not video.exists() or not video.is_file():
        raise CropError(f"Video nao encontrado: {video_path}")
        
    w, h = _get_dimensions(str(video))
    
    factor = 1.0 - crop_top
    crop_w = _even(w * factor)
    crop_h = _even(h * factor)
    crop_x = _even((w - crop_w) / 2)
    crop_y = _even(h * crop_top)
    if crop_y + crop_h > h:
        crop_y = _even(h - crop_h)
        
    if crop_w <= 0 or crop_h <= 0:
        raise CropError("Crop resultou em dimensao zero.")

    # Crop e rescale para manter a resolucao original sem distorcer (zoom)
    filter_complex = f"[0:v]crop={crop_w}:{crop_h}:{crop_x}:{crop_y},scale={w}:{h}[v]"
    
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    
    # Manter audio original se existir
    cmd = [
        "ffmpeg", "-y",
        "-i", str(video),
        "-filter_complex", filter_complex,
        "-map", "[v]", "-map", "0:a?",
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "medium", "-crf", "18",
        "-c:a", "copy",
        str(out)
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise CropError(f"ffmpeg erro: {result.stderr[-500:]}")
        
    return str(out.resolve())

def main():
    parser = argparse.ArgumentParser(description="Crop da marca da RunningHub (topo).")
    parser.add_argument("input", help="Video a ser processado.")
    parser.add_argument("--crop-top", type=float, default=DEFAULT_CROP_TOP,
                        help=f"Fracao do topo cortada (default {DEFAULT_CROP_TOP}).")
    args = parser.parse_args()
    
    video = Path(args.input)
    if not video.exists():
        sys.exit(f"[ERRO] {args.input} nao encontrado.")
        
    out_dir = video.parent / "_limpo"
    out_path = out_dir / video.name
    
    print(f"Limpando {video.name} (top crop {args.crop_top})...")
    try:
        saved = crop_video(str(video), str(out_path), args.crop_top)
        print(f"Salvo com sucesso em: {saved}")
    except CropError as e:
        sys.exit(f"[ERRO] {e}")

if __name__ == "__main__":
    main()
