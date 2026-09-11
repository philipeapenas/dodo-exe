#!/usr/bin/env python3
"""
box_overlay.py - Compoe a caixinha de pergunta (replica IG) sobre um video de motion.

Pipeline: renderiza o PNG transparente a partir de question_box.html (Chrome headless)
e sobrepoe via ffmpeg, cobrindo a caixinha ORIGINAL distorcida pelo motion control.

Passo OPCIONAL do estagio final (so quando o reel e formato "Faca uma pergunta").
Tamanho/posicao AJUSTAVEIS (o fundador vai limpar a caixa original no futuro e ai a
caixa de codigo fica menor / posicionada livre) -> nada de full-width hardcoded.

Por padrao, DETECTA a caixa antiga em um frame (upper ~40%) e dimensiona a nova pra
cobri-la. --box-y / --minh / --w / --box-x sobrescrevem a auto-deteccao.

Uso:
  # 1 video (cobrir a caixa antiga, full-width auto):
  py box_overlay.py <video.mp4> --pergunta "texto" [--w 544 --minh 120 --box-y 95]
  # sticker fiel ao reel (compacto, fonte reduzida): render_w > w
  py box_overlay.py <video.mp4> --pergunta "texto" --render-w 494 --w 373 --box-x 85 --box-y 133 --minh 70
  # lote (pasta) com mapa JSON {arquivo: {"pergunta": "...", "render_w": 494, "w": 373, "box_x": 85, "box_y": 133}}:
  py box_overlay.py <pasta> --map mapa.json [--out <pasta_saida>]

Emoji: --emoji apple|native (default apple). Requer rede (fonte Inter + emojicdn) no
render; vendorizacao local e follow-up (ver README_render.md).

Deps: Chrome ou Edge instalado; Pillow; ffmpeg no PATH.
"""

import argparse
import json
import os
import subprocess
import sys
import tempfile
import urllib.parse
import urllib.request
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    sys.exit("[FATAL] Falta Pillow. Rode: pip install pillow")

HERE = Path(__file__).resolve().parent
TEMPLATE = HERE / "question_box.html"
ASSETS_EMOJI = HERE / "assets" / "emoji"
VIDEO_EXTS = {".mp4", ".mov", ".mkv", ".webm"}
DSF = 2  # device scale factor (nitidez); o PNG sai 2x e e reduzido no overlay.

CHROME_CANDIDATES = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
]


class BoxError(RuntimeError):
    """Erro de composicao, capturavel por item no lote."""


# --------------------------------------------------------------------------- #
# Descoberta de ferramentas
# --------------------------------------------------------------------------- #
def _find_browser() -> str:
    for c in CHROME_CANDIDATES:
        if Path(c).is_file():
            return c
    raise BoxError("Chrome/Edge nao encontrado. Instale um Chromium ou ajuste CHROME_CANDIDATES.")


def _emoji_chars(text: str) -> list:
    """Code points pictograficos do texto (cobre os ranges de emoji comuns)."""
    out = []
    for ch in text:
        cp = ord(ch)
        if cp == 0xFE0F:
            continue
        if cp >= 0x1F000 or 0x2600 <= cp <= 0x27BF or 0x2B00 <= cp <= 0x2BFF or 0x2190 <= cp <= 0x21FF:
            out.append(ch)
    return out


def ensure_emojis_cached(text: str) -> None:
    """
    Garante que os emojis do texto existam em assets/emoji/<hex>.png (estilo Apple).
    Baixa do emojicdn os que faltam -> render local/offline. Falha silenciosa (o
    template tem fallback pra CDN em runtime). Simplificacao: 1 code point = 1 emoji
    (ZWJ exotico cai no fallback do template).
    """
    ASSETS_EMOJI.mkdir(parents=True, exist_ok=True)
    for e in _emoji_chars(text):
        hexname = f"{ord(e):x}"
        dst = ASSETS_EMOJI / f"{hexname}.png"
        if dst.exists():
            continue
        try:
            url = "https://emojicdn.elk.sh/" + urllib.parse.quote(e) + "?style=apple"
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            dst.write_bytes(urllib.request.urlopen(req, timeout=30).read())
        except Exception:
            pass


def _check_ffmpeg() -> None:
    try:
        subprocess.run(["ffmpeg", "-version"], capture_output=True, timeout=5)
    except FileNotFoundError:
        raise BoxError("ffmpeg nao encontrado no PATH.")


def _dimensions(video: str) -> tuple:
    r = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0",
         "-show_entries", "stream=width,height", "-of", "csv=p=0:s=x", video],
        capture_output=True, text=True, timeout=15)
    try:
        w, h = r.stdout.strip().split("x")
        return int(w), int(h)
    except (ValueError, AttributeError):
        raise BoxError(f"Nao li a dimensao de {video} (ffprobe='{r.stdout.strip()}').")


# --------------------------------------------------------------------------- #
# Deteccao da caixa antiga (pra cobrir com margem)
# --------------------------------------------------------------------------- #
def detect_old_box(video: str, w: int, h: int) -> tuple:
    """
    Extrai um frame (~1.5s) e acha a faixa vertical da caixa antiga no topo ~45%:
    barra escura (header) + corpo branco. Retorna (top_y, bottom_y) em px.
    Fallback (0.10*h, 0.30*h) se nao achar.
    """
    fallback = (int(0.10 * h), int(0.30 * h))
    try:
        with tempfile.TemporaryDirectory() as td:
            fpath = os.path.join(td, "f.png")
            r = subprocess.run(
                ["ffmpeg", "-y", "-ss", "1.5", "-i", video, "-frames:v", "1", fpath],
                capture_output=True, timeout=30)
            if r.returncode != 0 or not os.path.exists(fpath):
                return fallback
            im = Image.open(fpath).convert("RGB")
            iw, ih = im.size
            px = im.load()
            top_scan = int(ih * 0.45)
            thr_w = iw * 0.40  # >=40% da largura na linha

            def dark(y):
                return sum(1 for x in range(iw)
                           if px[x, y][0] < 70 and px[x, y][1] < 70 and px[x, y][2] < 70)

            def white(y):
                return sum(1 for x in range(iw)
                           if px[x, y][0] > 225 and px[x, y][1] > 225 and px[x, y][2] > 225)

            dark_rows = [y for y in range(top_scan) if dark(y) > thr_w]
            white_rows = [y for y in range(top_scan) if white(y) > thr_w]
            ys = dark_rows + white_rows
            if not ys:
                return fallback
            top_i, bot_i = min(ys), max(ys)
            # escala do frame (iw,ih) pro espaco do video (w,h) - normalmente iguais
            top_y = int(top_i * h / ih)
            bot_y = int(bot_i * h / ih)
            if bot_y - top_y < 20:            # deteccao fraca
                return fallback
            return top_y, bot_y
    except Exception:
        return fallback


# --------------------------------------------------------------------------- #
# Render do PNG (Chrome headless -> transparente)
# --------------------------------------------------------------------------- #
def render_box_png(text: str, out_png: str, render_w: int, minh: int,
                   emoji: str = "apple", win_h: int = 700) -> str:
    """
    Renderiza a caixa (largura de LAYOUT = render_w) num PNG transparente (2x). Esse
    render_w define a quebra de linha e o tamanho aparente da fonte; no overlay o PNG
    e reescalado pra largura de EXIBICAO (box_w). render_w > box_w = fonte menor/fiel.
    """
    browser = _find_browser()
    if not TEMPLATE.is_file():
        raise BoxError(f"Template nao encontrado: {TEMPLATE}")
    q = urllib.parse.quote(text)
    url = (TEMPLATE.as_uri() +
           f"?export=1&w={render_w}&minh={minh}&emoji={emoji}&q={q}")
    cmd = [
        browser, "--headless=new", "--disable-gpu", "--hide-scrollbars",
        f"--force-device-scale-factor={DSF}",
        "--default-background-color=00000000",     # fundo transparente
        "--virtual-time-budget=6000",              # espera fonte+emoji (rede) carregar
        f"--window-size={render_w},{win_h}",
        f"--screenshot={out_png}", url,
    ]
    r = subprocess.run(cmd, capture_output=True, timeout=90)
    if not os.path.exists(out_png):
        tail = (r.stderr[-400:].decode("utf-8", "replace") if r.stderr else "")
        raise BoxError(f"Chrome nao gerou o PNG da caixa.\n{tail}")
    return out_png


# --------------------------------------------------------------------------- #
# Composicao final
# --------------------------------------------------------------------------- #
def compose(video: str, out_path: str, pergunta: str, *,
            box_w=None, box_x=0, box_y=None, minh=None, emoji="apple",
            render_w=None) -> str:
    """
    Renderiza a caixa e sobrepoe no video. Auto-detecta posicao/altura pra cobrir a
    caixa antiga, salvo overrides.

    box_w  = largura de EXIBICAO no video (default: largura do video = cobre a antiga).
    render_w = largura de LAYOUT (design). Se > box_w, a fonte fica menor/fiel ao reel
               original (ex: reel 720px -> render_w=494 e box_w=373 no video 544px).
               Default: render_w = box_w (sem reescala).
    """
    _check_ffmpeg()
    vid = Path(video)
    if not vid.is_file():
        raise BoxError(f"Video nao encontrado: {video}")
    if not pergunta or not pergunta.strip():
        raise BoxError("Pergunta vazia.")

    w, h = _dimensions(str(vid))
    box_w = int(box_w) if box_w else w                 # exibicao; default full-width (cobre a antiga)
    if box_w <= 0 or box_w > w:
        box_w = w
    render_w = int(render_w) if render_w else box_w    # layout; > box_w = fonte menor/fiel
    if render_w <= 0:
        render_w = box_w

    if box_y is None or minh is None:
        top_y, bot_y = detect_old_box(str(vid), w, h)
        if box_y is None:
            box_y = max(0, top_y - 10)                 # 10px de folga acima
        if minh is None:
            # corpo alto o suficiente pra caixa cobrir ate ~15px abaixo da antiga.
            # altura do header (~62px @1x) ja soma; minh cobre o resto.
            minh = max(80, (bot_y - int(box_y)) - 47 + 15)
    box_x, box_y, minh = int(box_x), int(box_y), int(minh)

    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)

    if emoji == "apple":
        ensure_emojis_cached(pergunta)   # vendoriza emojis novos -> render offline
    with tempfile.TemporaryDirectory() as td:
        png = os.path.join(td, "box.png")
        render_box_png(pergunta, png, render_w, minh, emoji)
        has_audio = _has_audio(str(vid))
        # PNG renderizado em render_w (2x) -> reduz pra box_w (exibicao) no overlay.
        fc = f"[1:v]scale={box_w}:-1[bx];[0:v][bx]overlay={box_x}:{box_y}[v]"
        cmd = ["ffmpeg", "-y", "-i", str(vid), "-i", png,
               "-filter_complex", fc, "-map", "[v]"]
        if has_audio:
            cmd += ["-map", "0:a"]
        cmd += ["-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "medium",
                "-crf", "18", "-c:a", "copy", str(out)]
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode != 0 or not out.exists():
            raise BoxError(f"ffmpeg falhou ({r.returncode}):\n{r.stderr[-600:]}")
    return str(out.resolve())


def _has_audio(video: str) -> bool:
    r = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "a", "-show_entries",
         "stream=index", "-of", "csv=p=0", video],
        capture_output=True, text=True, timeout=15)
    return bool(r.stdout.strip())


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #
def _collect(inp: str) -> list:
    p = Path(inp)
    if p.is_file():
        return [p]
    if p.is_dir():
        vids = sorted(f for f in p.iterdir()
                      if f.is_file() and f.suffix.lower() in VIDEO_EXTS)
        if not vids:
            raise BoxError(f"Nenhum video em {inp}")
        return vids
    raise BoxError(f"Caminho nao encontrado: {inp}")


def main() -> None:
    ap = argparse.ArgumentParser(description="Overlay da caixinha de pergunta (replica IG).")
    ap.add_argument("input", help="Video ou pasta.")
    ap.add_argument("--pergunta", help="Texto (modo 1 video).")
    ap.add_argument("--map", help="JSON {arquivo: {pergunta, box_y?, minh?, w?}} (modo lote).")
    ap.add_argument("--out", help="Pasta de saida (default: <entrada>/_caixinha).")
    ap.add_argument("--emoji", default="apple", choices=["apple", "native"])
    ap.add_argument("--w", type=int, help="Largura de EXIBICAO da caixa no video (default: largura do video).")
    ap.add_argument("--render-w", type=int,
                    help="Largura de LAYOUT/design (default: = --w). Maior que --w = fonte menor/fiel ao reel.")
    ap.add_argument("--minh", type=int, help="Altura min do corpo (default: auto-detecta).")
    ap.add_argument("--box-x", type=int, default=0, help="X do overlay (default 0).")
    ap.add_argument("--box-y", type=int, help="Y do overlay (default: auto-detecta).")
    args = ap.parse_args()

    try:
        videos = _collect(args.input)
    except BoxError as e:
        print(f"[ERRO] {e}", file=sys.stderr); sys.exit(1)

    mapping = {}
    if args.map:
        try:
            mapping = json.loads(Path(args.map).read_text(encoding="utf-8"))
        except Exception as e:
            print(f"[ERRO] mapa invalido: {e}", file=sys.stderr); sys.exit(1)

    base = Path(args.input) if Path(args.input).is_dir() else Path(args.input).parent
    out_dir = Path(args.out) if args.out else base / "_caixinha"

    ok, fails = 0, []
    print(f"Compondo caixinha em {len(videos)} video(s) -> {out_dir}")
    for i, v in enumerate(videos, 1):
        entry = mapping.get(v.name, {})
        pergunta = entry.get("pergunta") if entry else args.pergunta
        if not pergunta:
            print(f"[{i:02d}] {v.name} PULADO (sem pergunta)"); continue
        out_path = out_dir / f"{v.stem}_box.mp4"
        print(f"[{i:02d}/{len(videos)}] {v.name} ... ", end="", flush=True)
        try:
            compose(str(v), str(out_path), pergunta,
                    box_w=entry.get("w", args.w),
                    render_w=entry.get("render_w", args.render_w),
                    box_x=entry.get("box_x", args.box_x),
                    box_y=entry.get("box_y", args.box_y),
                    minh=entry.get("minh", args.minh),
                    emoji=entry.get("emoji", args.emoji))
            print(f"OK -> {out_path.name}"); ok += 1
        except BoxError as e:
            print(f"FALHA: {e}"); fails.append((v.name, str(e)))

    print(f"\nResumo: {ok} ok, {len(fails)} falhas.")
    for n, e in fails:
        print(f"  [{n}] {e}")
    sys.exit(0 if not fails else 1)


if __name__ == "__main__":
    main()
