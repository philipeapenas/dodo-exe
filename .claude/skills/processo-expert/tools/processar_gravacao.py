#!/usr/bin/env python
"""
Pipeline completo de uma gravacao de processo.

Quatro estagios numa passada: limpa o audio, corta o tempo morto, junta os
planos e emite o relatorio de comunicacao comparado com as gravacoes anteriores.

Uso:
    python processar_gravacao.py --pasta "<projeto>/material/processo" [--titulo "Nome"]

A pasta deve conter os planos brutos (qualquer .mp4 sem "(editado)" no nome).
Entrega na mesma pasta: "<plano> (editado).mp4", "processo completo.mp4" e
"comunicacao.md".
"""
import argparse
import json
import pathlib
import re
import subprocess
import unicodedata
from datetime import date

import requests

# A chave do ElevenLabs e a mesma da voice-expert: tools/ -> processo-expert/ -> skills/
SECRETS = (pathlib.Path(__file__).resolve().parent.parent.parent
           / "voice-expert" / "tools" / "secrets.local.json")
HISTORICO = pathlib.Path(__file__).with_name("historico_comunicacao.json")

# --- parametros validados pelo fundador assistindo o resultado -----------------
FATIA_S = 120.0     # fatia de audio mandada por vez pro isolamento
GAP_FRASE = 0.55    # silencio maior que isso separa uma frase da outra
RESPIRO = 0.32      # pausa que fica entre frases no video cortado
PAD_INICIO = 0.12
PAD_FIM = 0.28
PAUSA_LONGA = 1.5   # a partir daqui e travada, nao respiro
VELOCIDADE = 1.4    # aceleracao do video final

VICIOS = {"tipo", "assim", "ne", "entao", "ai", "cara", "beleza", "certo", "ta"}
ARRASTADOS = re.compile(r"^(e{2,}|a{2,}|o{2,}|hu?m+|ah+|eh+)$")
INCERTEZA = ["acho que", "acredito que", "talvez", "sei la", "mais ou menos",
             "nao sei", "num sei", "meio que", "de repente", "eu diria",
             "se nao me engano", "por assim dizer", "eu acho"]
CORRECAO = ["na verdade", "ou melhor", "quer dizer", "desculpa", "deixa eu",
            "pera", "voltando", "mentira", "e o contrario"]

ROTULOS = {"recomeco": "Recomecos e gagueira",
           "incerteza": "Marcas de incerteza",
           "correcao": "Autocorrecoes",
           "travada": "Travadas procurando a palavra"}
EXPLICACAO = {
    "recomeco": "Comecou a frase, abortou e recomecou. E o mais visivel pra quem assiste.",
    "incerteza": "Enfraquecem a autoridade: voce sabe o processo, a fala precisa mostrar isso.",
    "correcao": "Se contradisse e voltou atras. Faltou decidir a ordem antes de gravar.",
    "travada": "Parou pra procurar a palavra. O corte tirou o silencio, mas o tropeco fica.",
}


def sh(cmd):
    subprocess.run(cmd, check=True)


def duracao(p):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "csv=p=0", str(p)], capture_output=True, text=True)
    return float(r.stdout.strip())


def duracao_stream(p, tipo):
    r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", tipo,
                        "-show_entries", "stream=duration", "-of", "csv=p=0", str(p)],
                       capture_output=True, text=True)
    try:
        return float(r.stdout.strip().split("\n")[0])
    except ValueError:
        return 0.0


def simples(txt):
    txt = unicodedata.normalize("NFD", txt.lower())
    return "".join(c for c in txt if unicodedata.category(c) != "Mn").strip(".,!?;:")


def mmss(t):
    return f"{int(t // 60)}:{t % 60:04.1f}"


# ------------------------------------------------------------ 1. audio ------

def limpar_audio(video, api_key, tmp):
    """Tira a cama de som vazada. Devolve wav do mesmo tamanho do audio original."""
    bruto = tmp / f"{video.stem}_bruto.wav"
    sh(["ffmpeg", "-y", "-hide_banner", "-v", "error", "-i", str(video),
        "-vn", "-ac", "1", "-ar", "44100", str(bruto)])

    v, a = duracao_stream(video, "v"), duracao_stream(video, "a")
    if abs(v - a) > 1.0:
        print(f"  AVISO: audio termina em {a:.0f}s mas a imagem vai ate {v:.0f}s "
              f"({v - a:.0f}s mudos)", flush=True)

    total, pedacos, inicio, i = duracao(bruto), [], 0.0, 0
    while inicio < total - 0.05:
        alvo = min(FATIA_S, total - inicio)
        fatia = tmp / f"_f{i}.wav"
        sh(["ffmpeg", "-y", "-hide_banner", "-v", "error", "-ss", f"{inicio:.3f}",
            "-t", f"{alvo:.3f}", "-i", str(bruto), "-ac", "1", "-ar", "44100", str(fatia)])
        with fatia.open("rb") as fh:
            r = requests.post("https://api.elevenlabs.io/v1/audio-isolation",
                              headers={"xi-api-key": api_key},
                              files={"audio": (fatia.name, fh, "audio/wav")}, timeout=1800)
        r.raise_for_status()
        limpa = tmp / f"_f{i}_limpa.mp3"
        limpa.write_bytes(r.content)
        # forca de volta a duracao exata, senao a diferenca acumula e desanda
        ok = tmp / f"_f{i}_ok.wav"
        sh(["ffmpeg", "-y", "-hide_banner", "-v", "error", "-i", str(limpa),
            "-af", "apad", "-t", f"{alvo:.3f}", "-ac", "1", "-ar", "44100", str(ok)])
        pedacos.append(ok)
        fatia.unlink()
        limpa.unlink()
        inicio += alvo
        i += 1

    lista = tmp / "_fatias.txt"
    lista.write_text("".join(f"file '{p.as_posix()}'\n" for p in pedacos), encoding="utf-8")
    limpo = tmp / f"{video.stem}_limpo.wav"
    sh(["ffmpeg", "-y", "-hide_banner", "-v", "error", "-f", "concat", "-safe", "0",
        "-i", str(lista), "-ac", "1", "-ar", "44100", str(limpo)])
    for p in pedacos:
        p.unlink()
    lista.unlink()

    if abs(duracao(limpo) - total) > 1.0:
        raise SystemExit(f"audio limpo com {duracao(limpo):.1f}s contra {total:.1f}s")

    com_audio = tmp / f"{video.stem}_com_audio.mp4"
    sh(["ffmpeg", "-y", "-hide_banner", "-v", "error", "-i", str(video), "-i", str(limpo),
        "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
        str(com_audio)])
    bruto.unlink()
    limpo.unlink()
    return com_audio


# ------------------------------------------------------ 2. transcricao ------

def transcrever(video, api_key, tmp):
    cache = tmp / f"{video.stem}_stt.json"
    if cache.exists():
        return json.loads(cache.read_text(encoding="utf-8"))
    wav = tmp / f"{video.stem}_stt.wav"
    sh(["ffmpeg", "-y", "-hide_banner", "-v", "error", "-i", str(video),
        "-vn", "-ac", "1", "-ar", "16000", str(wav)])
    with wav.open("rb") as fh:
        r = requests.post("https://api.elevenlabs.io/v1/speech-to-text",
                          headers={"xi-api-key": api_key},
                          files={"file": (wav.name, fh, "audio/wav")},
                          data={"model_id": "scribe_v1"}, timeout=1800)
    r.raise_for_status()
    palavras = [w for w in r.json().get("words", [])
                if w.get("type") == "word" and w.get("text", "").strip()]
    cache.write_text(json.dumps(palavras), encoding="utf-8")
    wav.unlink()
    return palavras


# ------------------------------------------------------------ 3. corte ------

def marcar_descarte(palavras):
    """Indices de palavras a excisar: vicio solto e comeco abortado.

    Fica de fora de proposito o que muda o sentido da frase - marca de incerteza
    e autocorrecao. Cortar "nao sei explicar" quebra a frase; isso vai pro
    relatorio pra ele corrigir o habito, nao pro corte.
    """
    texto = [simples(w["text"]) for w in palavras]
    fora = set()
    for i, p in enumerate(texto):
        if p in VICIOS or ARRASTADOS.match(p):
            fora.add(i)
        elif i and len(p) > 1:
            ant = texto[i - 1]
            # "esse esse" ou "aquel- aquele": descarta a tentativa abortada
            if p == ant or (ant != p and len(ant) >= 3
                            and (p.startswith(ant) or ant.startswith(p))):
                fora.add(i - 1)
    return fora


def trechos_mantidos(palavras, fim, descartar=frozenset()):
    """Trechos a manter. Palavra descartada quebra o trecho sem deixar respiro."""
    corridas, atual, cortou = [], [], False
    for i, w in enumerate(palavras):
        if i in descartar:
            if atual:
                corridas.append((atual, cortou))
                atual, cortou = [], True
            continue
        if atual and w["start"] - atual[-1]["end"] > GAP_FRASE:
            corridas.append((atual, cortou))
            atual, cortou = [], False
        atual.append(w)
    if atual:
        corridas.append((atual, cortou))

    saida = []
    for g, veio_de_corte in corridas:
        # junta apertado quando a quebra foi excisao; folgado quando foi pausa
        pad_i = 0.04 if veio_de_corte else PAD_INICIO
        ini, f = max(0.0, g[0]["start"] - pad_i), min(fim, g[-1]["end"] + PAD_FIM)
        if f - ini < 0.12:
            continue
        if saida and ini - saida[-1][1] <= 0.05:
            saida[-1] = (saida[-1][0], f)
        else:
            if saida and not veio_de_corte:
                saida[-1] = (saida[-1][0], saida[-1][1] + RESPIRO)
            saida.append((ini, f))
    return saida


def cortar(video, trechos, destino):
    sel = "+".join(f"between(t,{a:.3f},{b:.3f})" for a, b in trechos)
    sh(["ffmpeg", "-y", "-hide_banner", "-v", "error", "-i", str(video),
        "-filter_complex",
        f"[0:v]select='{sel}',setpts=N/FRAME_RATE/TB[v];"
        f"[0:a]aselect='{sel}',asetpts=N/SR/TB[a]",
        "-map", "[v]", "-map", "[a]",
        "-c:v", "libx264", "-crf", "20", "-preset", "medium", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "160k", str(destino)])


# ----------------------------------------------------------- 4. juntar ------

def juntar(partes, destino, tmp):
    """Preenche borda ate um quadro comum. NAO redimensiona: escalar borra o texto."""
    medidas = []
    for p in partes:
        r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v",
                            "-show_entries", "stream=width,height", "-of", "csv=p=0", str(p)],
                           capture_output=True, text=True)
        w, h = (int(x) for x in r.stdout.strip().split(",")[:2])
        medidas.append((p, w, h))
    larg = max(w for _, w, _ in medidas)
    alt = max(h for _, _, h in medidas)
    larg += larg % 2
    alt += alt % 2

    conformadas = []
    for i, (p, w, h) in enumerate(medidas):
        dst = tmp / f"_parte_{i}.mp4"
        sh(["ffmpeg", "-y", "-hide_banner", "-v", "error", "-i", str(p),
            "-vf", f"pad={larg}:{alt}:{(larg - w) // 2}:{(alt - h) // 2}:color=black,setsar=1",
            "-r", "30", "-c:v", "libx264", "-crf", "19", "-preset", "medium",
            "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k",
            "-ar", "48000", "-ac", "2", str(dst)])
        conformadas.append(dst)

    lista = tmp / "_partes.txt"
    lista.write_text("".join(f"file '{p.as_posix()}'\n" for p in conformadas), encoding="utf-8")
    sh(["ffmpeg", "-y", "-hide_banner", "-v", "error", "-f", "concat", "-safe", "0",
        "-i", str(lista), "-c", "copy", str(destino)])
    for p in conformadas:
        p.unlink()
    lista.unlink()
    return larg, alt


# -------------------------------------------------------- 5. relatorio ------

def achar(palavras):
    achados, contagem = [], {}
    texto = [simples(w["text"]) for w in palavras]
    for i, w in enumerate(palavras):
        p = texto[i]
        if p in VICIOS or ARRASTADOS.match(p):
            contagem[p] = contagem.get(p, 0) + 1
        if i and len(p) > 1:
            ant = texto[i - 1]
            if p == ant or (ant != p and len(ant) >= 3
                            and (p.startswith(ant) or ant.startswith(p))):
                ctx = " ".join(x["text"] for x in palavras[max(0, i - 3):i + 4])
                achados.append((w["start"], "recomeco", ctx))
        if i and w["start"] - palavras[i - 1]["end"] > PAUSA_LONGA:
            pausa = w["start"] - palavras[i - 1]["end"]
            ctx = " ".join(x["text"] for x in palavras[max(0, i - 4):i + 3])
            achados.append((palavras[i - 1]["end"], "travada", f"{ctx}  ({pausa:.1f}s)"))

    corrido, pos, acc = " ".join(texto), [], 0
    for i, p in enumerate(texto):
        pos.append((acc, i))
        acc += len(p) + 1
    for marcadores, rotulo in ((INCERTEZA, "incerteza"), (CORRECAO, "correcao")):
        for frase in marcadores:
            for m in re.finditer(rf"\b{re.escape(frase)}\b", corrido):
                idx = next((i for p_, i in pos if p_ >= m.start()), None)
                if idx is not None:
                    ctx = " ".join(x["text"] for x in palavras[max(0, idx - 3):idx + 6])
                    achados.append((palavras[idx]["start"], rotulo, ctx))
    return achados, contagem


def relatorio(titulo, total_s, palavras_total, por_tipo, contagem, destino):
    hist = json.loads(HISTORICO.read_text(encoding="utf-8")) if HISTORICO.exists() else []
    anterior = hist[-1] if hist else None

    por_mil = {p: round(1000 * n / palavras_total, 1) for p, n in contagem.items()}
    linhas = [f"# {titulo}", "",
              f"{mmss(total_s)} de video, {palavras_total} palavras faladas.", "",
              "Os tempos apontam pro video junto e ja cortado.", "",
              "## Vicios de linguagem", ""]

    recorrentes = sorted([(p, n) for p, n in contagem.items() if n >= 3],
                         key=lambda x: -x[1])
    if recorrentes:
        if anterior:
            linhas += ["| Vicio | Vezes | Por mil palavras | Gravacao anterior |",
                       "|---|---|---|---|"]
            for p, n in recorrentes:
                antes = anterior["por_mil"].get(p)
                if antes is None:
                    delta = "novo"
                else:
                    seta = "caiu" if por_mil[p] < antes else ("subiu" if por_mil[p] > antes else "igual")
                    delta = f"{antes} ({seta})"
                linhas.append(f"| {p} | {n}x | {por_mil[p]} | {delta} |")
        else:
            linhas += ["| Vicio | Vezes | Por mil palavras |", "|---|---|---|"]
            linhas += [f"| {p} | {n}x | {por_mil[p]} |" for p, n in recorrentes]
    else:
        linhas.append("Nenhum apareceu 3 vezes ou mais.")
    linhas.append("")

    if anterior:
        linhas += ["## Comparado com a gravacao anterior", "",
                   f"Anterior: {anterior['titulo']} ({anterior['data']}).", ""]
        for tipo in ROTULOS:
            agora = len(por_tipo.get(tipo, []))
            antes = anterior["por_tipo"].get(tipo, 0)
            if agora or antes:
                linhas.append(f"- {ROTULOS[tipo]}: {antes} -> **{agora}**")
        linhas.append("")

    for tipo in ["recomeco", "incerteza", "correcao", "travada"]:
        itens = por_tipo.get(tipo)
        if not itens:
            continue
        linhas += [f"## {ROTULOS[tipo]} ({len(itens)}x)", "", EXPLICACAO[tipo], "",
                   "| Tempo | Trecho |", "|---|---|"]
        linhas += [f"| {mmss(t)} | {c} |" for t, c in sorted(itens)]
        linhas.append("")

    destino.write_text("\n".join(linhas), encoding="utf-8")
    hist.append({"titulo": titulo, "data": date.today().isoformat(),
                 "palavras": palavras_total, "duracao_s": round(total_s, 1),
                 "por_mil": por_mil,
                 "por_tipo": {k: len(v) for k, v in por_tipo.items()}})
    HISTORICO.write_text(json.dumps(hist, indent=2, ensure_ascii=False), encoding="utf-8")


# -------------------------------------------------------------- main -------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pasta", required=True)
    ap.add_argument("--titulo", default=None)
    ap.add_argument("--entrega", default=None,
                    help="caminho completo de uma copia extra da versao final")
    args = ap.parse_args()

    pasta = pathlib.Path(args.pasta)
    titulo = args.titulo or f"Gravacao de processo {date.today():%d-%m-%y}"
    tmp = pasta / "_tmp"
    tmp.mkdir(exist_ok=True)
    api_key = json.loads(SECRETS.read_text(encoding="utf-8"))["elevenlabs_api_key"]

    # estrutura fixa da pasta de processo
    dir_bruto = pasta / "gravaçao"
    dir_editado = pasta / "editado"
    dir_completo = pasta / "completo"
    dir_final = pasta / "final"
    dir_com = pasta / "comunicacao"
    for d in (dir_bruto, dir_editado, dir_completo, dir_final, dir_com):
        d.mkdir(exist_ok=True)

    brutos = sorted(p for p in dir_bruto.glob("*.mp4") if "(editado)" not in p.name)
    if not brutos:
        raise SystemExit(f"nenhum plano bruto em {dir_bruto}")

    # Duas versoes da mesma gravacao:
    #   completo/ - registro inteiro, so sem tempo morto, na velocidade normal
    #   final/    - pra quem vai assistir: sem vicio de linguagem e acelerado
    partes_completo, partes_final = [], []
    por_tipo, contagem_geral, palavras_total, offset = {}, {}, 0, 0.0

    for bruto in brutos:
        print(f"\n=== {bruto.name} ===", flush=True)
        com_audio = limpar_audio(bruto, api_key, tmp)
        palavras = transcrever(com_audio, api_key, tmp)
        palavras_total += len(palavras)
        fim = palavras[-1]["end"] + 1

        trechos = trechos_mantidos(palavras, fim)
        descartar = marcar_descarte(palavras)
        trechos_limpos = trechos_mantidos(palavras, fim, descartar)
        print(f"  {len(palavras)} palavras | {len(descartar)} vicios excisados | "
              f"registro {sum(b - a for a, b in trechos):.0f}s | "
              f"final {sum(b - a for a, b in trechos_limpos):.0f}s "
              f"(bruto {duracao(bruto):.0f}s)", flush=True)

        editado = dir_editado / f"{bruto.stem} (editado).mp4"
        cortar(com_audio, trechos, editado)
        partes_completo.append(editado)

        sem_vicio = tmp / f"{bruto.stem}_final.mp4"
        cortar(com_audio, trechos_limpos, sem_vicio)
        partes_final.append(sem_vicio)

        achados, contagem = achar(palavras)
        for p, n in contagem.items():
            contagem_geral[p] = contagem_geral.get(p, 0) + n
        vistos = []
        for t, tipo, ctx in sorted(achados):
            acumulado = 0.0
            for ini, f_ in trechos:
                if t < ini:
                    break
                if t <= f_:
                    acumulado += t - ini
                    break
                acumulado += f_ - ini
            te = acumulado + offset
            if any(abs(te - v) < 1.0 for v in vistos):
                continue
            vistos.append(te)
            por_tipo.setdefault(tipo, []).append((te, ctx.strip()))
        offset += duracao(editado)
        com_audio.unlink()

    completo = dir_completo / "processo completo.mp4"
    if len(partes_completo) > 1:
        larg, alt = juntar(partes_completo, completo, tmp)
        print(f"\ncompleto: {larg}x{alt}, {duracao(completo):.0f}s", flush=True)
    else:
        completo.write_bytes(partes_completo[0].read_bytes())

    junto_final = tmp / "junto_final.mp4"
    if len(partes_final) > 1:
        juntar(partes_final, junto_final, tmp)
    else:
        junto_final.write_bytes(partes_final[0].read_bytes())

    # acelera por ultimo, depois de cortado e emendado. atempo preserva o tom da
    # voz - so mexer na taxa de quadros deixaria o audio agudo.
    final = dir_final / "processo final.mp4"
    sh(["ffmpeg", "-y", "-hide_banner", "-v", "error", "-i", str(junto_final),
        "-filter_complex",
        f"[0:v]setpts=PTS/{VELOCIDADE}[v];[0:a]atempo={VELOCIDADE}[a]",
        "-map", "[v]", "-map", "[a]",
        "-c:v", "libx264", "-crf", "19", "-preset", "medium", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "160k", str(final)])
    print(f"final: sem vicios e {VELOCIDADE}x -> {duracao(final):.0f}s", flush=True)

    if args.entrega:
        entrega = pathlib.Path(args.entrega)
        entrega.parent.mkdir(parents=True, exist_ok=True)
        entrega.write_bytes(final.read_bytes())
        print(f"entrega: {entrega}", flush=True)

    # o relatorio aponta pro registro completo, que e onde os tropecos existem
    relatorio(titulo, duracao(completo), palavras_total, por_tipo, contagem_geral,
              dir_com / "comunicacao.md")
    for f in tmp.glob("*"):
        f.unlink()
    tmp.rmdir()
    print("\npronto")


if __name__ == "__main__":
    main()
