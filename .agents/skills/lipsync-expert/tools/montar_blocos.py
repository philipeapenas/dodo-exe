#!/usr/bin/env python
"""
Monta os pares audio+video que entram no lip sync.

Recebe as falas soltas (uma por take) e a base de motion control, e devolve,
por bloco, um .wav com as falas emendadas e um .mp4 com a mesma duracao.

Regra central: o VIDEO se ajusta ao AUDIO, nunca o contrario. A fala e o
produto; a imagem e material de cobertura. Ver memory/pareamento_playbook.md.

Configuracao vem de um JSON de trabalho (--job), pra skill nao ter caminho de
cliente escrito no codigo. Formato:

{
  "material": "<caminho da pasta material do criativo>",
  "falas": "audio/falas_v3",
  "base": "motion/base_35s_motion.mp4",
  "base_util_s": 25.0,
  "respiro": 0.35,
  "pausas": {"3B": 0.80},
  "blocos": [
    {"nome": "bloco1", "takes": ["2A","2B","3A","3B","3C","4A"]},
    {"nome": "bloco2", "takes": ["6A","7A","7B","7C"], "aproximacao": 0.88}
  ],
  "avulsos": [{"nome": "1A", "take": "1A", "video": "video/take1.mp4"}]
}
"""
import argparse
import json
import pathlib
import subprocess

TAIL = 0.30  # sobra de video no fim, pro lip sync nao ficar sem imagem


def duracao(p):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "csv=p=0", str(p)], capture_output=True, text=True)
    return float(r.stdout.strip())


def montar_audio(falas_dir, takes, respiro, pausas, destino):
    """Emenda os takes com silencio entre eles."""
    partes, filtros, n = [], [], 0
    for i, take in enumerate(takes):
        partes += ["-i", str(falas_dir / f"{take}.mp3")]
        filtros.append(f"[{n}:a]aresample=44100,"
                       f"aformat=sample_fmts=s16:channel_layouts=mono[a{n}]")
        n += 1
        if i < len(takes) - 1:
            gap = pausas.get(takes[i + 1], respiro)
            partes += ["-f", "lavfi", "-t", str(gap), "-i", "anullsrc=r=44100:cl=mono"]
            filtros.append(f"[{n}:a]aformat=sample_fmts=s16:channel_layouts=mono[a{n}]")
            n += 1
    cadeia = "".join(f"[a{i}]" for i in range(n)) + f"concat=n={n}:v=0:a=1[out]"
    subprocess.run(["ffmpeg", "-y", "-hide_banner", "-v", "error"] + partes +
                   ["-filter_complex", ";".join(filtros) + ";" + cadeia,
                    "-map", "[out]", str(destino)], check=True)
    return duracao(destino)


def montar_video_dobrado(base, alvo, util, destino, aproximacao=None):
    """Base tocada pra frente e, se faltar, o resto tocado de tras.

    A emenda e invisivel por construcao: o quadro que encosta e o mesmo.
    Exige trecho SEM gesto direcional, senao a volta denuncia (mao descendo
    quando devia subir).
    """
    volta = round(alvo + TAIL - util, 2)
    corte = f"trim=0:{util},setpts=PTS-STARTPTS"
    punch = ""
    if aproximacao:
        largura = int(544 * aproximacao) // 2 * 2
        altura = int(960 * aproximacao) // 2 * 2
        punch = (f",crop={largura}:{altura}:{(544 - largura) // 2}:"
                 f"{(960 - altura) // 2},scale=544:960:flags=lanczos")
    if volta <= 0:
        fc = f"[0:v]{corte}{punch},trim=0:{alvo + TAIL}[out]"
    else:
        fc = (f"[0:v]{corte}{punch},split=2[f][r];"
              f"[r]reverse,trim=0:{volta},setpts=PTS-STARTPTS[rv];"
              f"[f][rv]concat=n=2:v=1:a=0[out]")
    subprocess.run(["ffmpeg", "-y", "-hide_banner", "-v", "error", "-i", str(base),
                    "-filter_complex", fc, "-map", "[out]", "-an",
                    "-c:v", "libx264", "-crf", "16", "-preset", "medium",
                    "-pix_fmt", "yuv420p", "-r", "30", str(destino)], check=True)
    return volta


def ajustar_avulso(video_src, alvo, destino):
    """Clipe pronto (Veo) reajustado pra bater exato com a fala.

    Diferenca de fracao de segundo se resolve no tempo do video: cortar o audio
    comeria o fim da palavra.
    """
    fator = alvo / duracao(video_src)
    subprocess.run(["ffmpeg", "-y", "-hide_banner", "-v", "error", "-i", str(video_src),
                    "-filter:v", f"setpts={fator:.6f}*PTS", "-an",
                    "-c:v", "libx264", "-crf", "16", "-preset", "medium",
                    "-pix_fmt", "yuv420p", str(destino)], check=True)
    return fator


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--job", required=True, help="JSON de trabalho")
    args = ap.parse_args()

    cfg = json.loads(pathlib.Path(args.job).read_text(encoding="utf-8"))
    mat = pathlib.Path(cfg["material"])
    falas = mat / cfg["falas"]
    saida = mat / "lipsync_input"
    saida.mkdir(parents=True, exist_ok=True)
    respiro = cfg.get("respiro", 0.35)
    pausas = cfg.get("pausas", {})

    for av in cfg.get("avulsos", []):
        nome = av["nome"]
        d = montar_audio(falas, [av["take"]], respiro, pausas,
                         saida / f"{nome}_audio.wav")
        fator = ajustar_avulso(mat / av["video"], d, saida / f"{nome}_video.mp4")
        print(f"{nome:<8} {d:6.2f}s | video reajustado em {fator:.3f}x")

    base = mat / cfg["base"]
    util = cfg.get("base_util_s", 25.0)
    for bloco in cfg["blocos"]:
        nome = bloco["nome"]
        d = montar_audio(falas, bloco["takes"], respiro, pausas,
                         saida / f"{nome}_audio.wav")
        volta = montar_video_dobrado(base, d, util, saida / f"{nome}_video.mp4",
                                     bloco.get("aproximacao"))
        dobra = f"dobra de {volta:.2f}s" if volta > 0 else "sem dobra"
        print(f"{nome:<8} {d:6.2f}s | {dobra}")

    print(f"\npares prontos em {saida}")


if __name__ == "__main__":
    main()
