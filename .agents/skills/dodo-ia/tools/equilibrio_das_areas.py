# -*- coding: utf-8 -*-
"""Cruza as 7 areas da vida com as tarefas da semana.

A autopsia do dia diz o PLACAR de cada area. A nota da semana diz onde o tempo
vai, pela tag de area em cada bloco de tarefa (#espiritual, #fisico, ...).
Este script poe os dois lado a lado e mostra a area fraca que a semana nao toca.

NOTA (30/08/2026): o checklist '#### <Area>: N/M' saiu da Autopsia (ver
`Tarefas/Agosto/Rotina Mestre - Rascunho 28-08-26.md`). A coluna "placar"
abaixo so enxerga autopsias ATE 29/08/2026 - a partir dai ela vai naturalmente
ficar sem dado novo, sem quebrar (`media=None` vira '-' na tabela). A coluna
"tarefas/feitas", que ja vinha so da Semana, continua 100% valida e e o
substituto de fato: ver `dissecar_autopsia.py`, que tem a nova secao
'Adesao por area pos-reestruturacao' derivada da mesma fonte.

Uso:
    python equilibrio_das_areas.py                 # semana que contem hoje
    python equilibrio_das_areas.py --dia 2026-08-19
"""
import io
import os
import re
import sys
import glob
import codecs
import argparse
import datetime as dt
import unicodedata
from collections import defaultdict

if sys.platform == "win32":
    try:
        sys.stdout = codecs.getwriter("utf-8")(sys.stdout.buffer, "replace")
    except AttributeError:
        pass

# tools/ -> dodo-ia/ -> skills/ -> .agents (ou .claude)/ -> raiz do workspace
RAIZ = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", ".."))
VAULT = os.path.join(RAIZ, "Vault")
PESSOAL = os.path.join(VAULT, "Vida Pessoal")
ROTINA = os.path.join(PESSOAL, "Rotina")
SEMANA = os.path.join(PESSOAL, "Semana")

RX_DATA = re.compile(r"(\d{2})-(\d{2})-(\d{2})")
RX_ITEM = re.compile(r"^([\t ]*)[-+*]\s+(?:\[( |x|X)\]\s*)?(.*)$")
RX_TAG = re.compile(r"#([A-Za-zÀ-ú][\w-]*)")
RX_AREA = re.compile(r"^#{2,4}\s+(Espiritual|Emocional|F[íi]sico|Intelectual|Relacionamento|Lazer|Financeiro)\s*:?\s*(\d+)\s*/\s*(\d+)")

AREAS = ("Espiritual", "Emocional", "Fisico", "Intelectual", "Relacionamento", "Lazer", "Financeiro")
DIAS = ("Segunda", "Terca", "Quarta", "Quinta", "Sexta", "Sabado", "Domingo")


def sem_acento(txt):
    txt = unicodedata.normalize("NFKD", txt)
    return "".join(c for c in txt if not unicodedata.combining(c))


def nome_area(bruto):
    b = sem_acento(bruto).lower()
    for a in AREAS:
        if sem_acento(a).lower() == b:
            return a
    return None


def achar_semana(alvo):
    for caminho in sorted(glob.glob(os.path.join(SEMANA, "*.md")), reverse=True):
        m = RX_DATA.search(os.path.basename(caminho))
        if not m:
            continue
        d, mes, ano = (int(x) for x in m.groups())
        try:
            segunda = dt.date(2000 + ano, mes, d)
        except ValueError:
            continue
        if 0 <= (alvo - segunda).days <= 6:
            return caminho, segunda
    return None, None


def tarefas_por_area(caminho):
    """{area: [(dia, bloco, tarefa, feita)]} lido das tags da nota da semana.

    Le a semana RECONSTITUIDA: desde 07/09/2026 o bloco do dia em andamento
    esta na autopsia, nao na semana (ver cofre.py). Lendo o arquivo cru, o dia
    de hoje sumiria da contagem e o placar sairia menor sem acusar nada.
    """
    import cofre
    linhas = cofre.semana_reconstituida(caminho)

    saida = defaultdict(list)
    sem_tag = []
    em_metas = False
    dia = None
    bloco = area = None
    ind_bloco = None

    for linha in linhas:
        if linha.startswith("#") and not linha.lstrip("#").startswith(" #"):
            nivel = len(linha) - len(linha.lstrip("#"))
            titulo = linha.strip("# ").strip()
            if nivel <= 3:
                em_metas = sem_acento(titulo).lower().startswith("metas")
                dia = bloco = area = None
                continue
            if nivel == 4:
                chave = sem_acento(titulo).lower()
                dia = titulo if em_metas and any(
                    chave.startswith(d.lower())
                    for d in [sem_acento(x).lower() for x in DIAS]) else None
                bloco = area = ind_bloco = None
                continue
            # nivel 5 ou mais e cabecalho de JANELA (`##### 09h-11h (...)`), que
            # vive DENTRO do bloco do dia. Ele nao troca de dia - tratar como
            # troca zerava `dia` na primeira janela e jogava o dia inteiro fora
            # da conta, devolvendo zero tarefa nas 7 areas sem erro nenhum.
            # Mordeu em 06/09/2026, quando o dia passou a ser agrupado por janela.
            # Zera so o contexto de bloco: tarefa-pai com tag nao atravessa janela.
            bloco = area = ind_bloco = None
            continue

        if not (em_metas and dia):
            continue

        m = RX_ITEM.match(linha)
        if not m:
            continue
        ind, marca, texto = len(m.group(1).replace("\t", "    ")), m.group(2), m.group(3).strip()
        if not texto:
            continue

        tags = RX_TAG.findall(texto)
        limpo = RX_TAG.sub("", texto).strip().strip("-").strip()
        if tags:
            achada = None
            for t in tags:
                achada = nome_area(t) or achada
            bloco, area, ind_bloco = limpo, achada, ind
            if marca is not None:  # o proprio bloco e uma tarefa
                (saida[area] if area else sem_tag).append(
                    (dia, limpo, limpo, marca.lower() == "x"))
            continue

        if bloco is None or ind <= (ind_bloco or 0):
            if marca is not None:
                sem_tag.append((dia, "-", texto, marca.lower() == "x"))
            continue

        if marca is not None:
            (saida[area] if area else sem_tag).append(
                (dia, bloco, texto, marca.lower() == "x"))

    return saida, sem_tag


def placares(ate, quantos=14):
    """{area: [(data, feito, total)]} das ultimas autopsias."""
    notas = []
    for caminho in glob.glob(os.path.join(ROTINA, "*", "*.md")):
        if os.path.basename(os.path.dirname(caminho)) == "Semana":
            continue
        m = RX_DATA.search(os.path.basename(caminho))
        if not m:
            continue
        d, mes, ano = (int(x) for x in m.groups())
        try:
            data = dt.date(2000 + ano, mes, d)
        except ValueError:
            continue
        if data <= ate:
            notas.append((data, caminho))
    notas.sort()
    notas = notas[-quantos:]

    saida = defaultdict(list)
    for data, caminho in notas:
        with io.open(caminho, encoding="utf-8", errors="replace") as fh:
            for linha in fh:
                ma = RX_AREA.match(linha.strip())
                if ma:
                    a = nome_area(ma.group(1))
                    if a:
                        saida[a].append((data, int(ma.group(2)), int(ma.group(3))))
    return saida, notas


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dia", help="AAAA-MM-DD (padrao: hoje)")
    ap.add_argument("--notas", type=int, default=14, help="autopsias olhadas pra tras")
    args = ap.parse_args()

    dia = dt.datetime.strptime(args.dia, "%Y-%m-%d").date() if args.dia else dt.date.today()
    caminho, segunda = achar_semana(dia)
    if not caminho:
        raise SystemExit("Nenhuma nota de semana cobre %s em %s" % (dia, SEMANA))

    tarefas, sem_tag = tarefas_por_area(caminho)
    placar, notas = placares(dia, args.notas)

    print("semana:   %s (abre em %s)" % (os.path.basename(caminho), segunda.strftime("%d/%m/%y")))
    print("placares: %d autopsias, de %s a %s" % (
        len(notas), notas[0][0].strftime("%d/%m") if notas else "-",
        notas[-1][0].strftime("%d/%m") if notas else "-"))
    print("")
    print("  %-15s %-9s %-8s %-8s %s" % ("area", "placar", "tarefas", "feitas", "dias da semana"))
    print("  " + "-" * 72)

    fracas = []
    for a in AREAS:
        p = placar.get(a, [])
        media = (sum(f for _, f, _ in p) / float(len(p))) if p else None
        teto = p[-1][2] if p else 10
        itens = tarefas.get(a, [])
        feitas = sum(1 for i in itens if i[3])
        dias = sorted(set(i[0] for i in itens), key=lambda d: DIAS.index(sem_acento(d).capitalize())
                      if sem_acento(d).capitalize() in DIAS else 99)
        print("  %-15s %-9s %-8s %-8s %s" % (
            a,
            ("%.1f/%d" % (media, teto)) if media is not None else "-",
            len(itens), feitas,
            ", ".join(d[:3] for d in dias) if dias else "nenhum"))
        if media is not None and not itens:
            fracas.append((a, media, teto))

    print("")
    if fracas:
        fracas.sort(key=lambda r: r[1])
        print("  Areas sem nenhuma tarefa nesta semana:")
        for a, media, teto in fracas:
            print("    - %-15s placar medio %.1f/%d" % (a, media, teto))
    else:
        print("  Todas as areas com placar tem pelo menos uma tarefa na semana.")

    if sem_tag:
        print("")
        print("  %d tarefas sem tag de area (nao entram na conta):" % len(sem_tag))
        for d, b, t, _ in sem_tag[:10]:
            print("    - %s > %s: %s" % (d, b, t))


if __name__ == "__main__":
    main()
