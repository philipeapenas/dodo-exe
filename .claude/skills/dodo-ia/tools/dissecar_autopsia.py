# -*- coding: utf-8 -*-
"""Disseca as autopsias: principios, habitos, dons, talentos, proposito e adesao por area.

Saida: dissecacao.md (leitura humana) + dissecacao.json (insumo pra skill).
"""
import io
import os
import re
import sys
import glob
import json
import codecs
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
PESSOAL = os.path.join(RAIZ, "Vault", "Vida Pessoal")
ROTINA = os.path.join(PESSOAL, "Rotina")
SEMANA_DIR = os.path.join(PESSOAL, "Semana")
IDENTIDADE = os.path.join(PESSOAL, "Identidade.md")
BASE = os.path.dirname(os.path.abspath(__file__))
RX_DATA = re.compile(r"(\d{2})-(\d{2})-(\d{2})")
RX_H = re.compile(r"^(#{2,4})\s+(.+?)\s*$")
RX_ITEM = re.compile(r"^[-+*]\s+(?:\[( |x|X)\]\s*)?(.+?)\s*$")
RX_CHECK_DATA = re.compile(r"\s*(?:✅|✔)\s*\d{4}-\d{2}-\d{2}\s*$")
RX_AREA = re.compile(r"^(Espiritual|Emocional|F[íi]sico|Intelectual|Relacionamento|Lazer|Financeiro)\s*:?\s*(\d+)\s*/\s*(\d+)")

AREAS = ("Espiritual", "Emocional", "Fisico", "Intelectual", "Relacionamento", "Lazer", "Financeiro")
# secoes de inventario: listas que descrevem quem ele e
INVENTARIO = ("Dons", "Talentos", "Princípios", "Hábitos", "Recursos/Habilidades")


def dia_ord(nome):
    m = RX_DATA.search(nome)
    if not m:
        return "00-00-00"
    d, mes, a = m.groups()
    return "20%s-%s-%s" % (a, mes, d)


def limpar(txt):
    txt = RX_CHECK_DATA.sub("", txt)
    txt = re.sub(r"\*\*|__|\*|`", "", txt)
    return txt.strip().rstrip(":").strip()


def chave(txt):
    txt = limpar(txt).lower()
    txt = re.sub(r"[^0-9a-zà-ú ]+", " ", txt)
    return re.sub(r"\s+", " ", txt).strip()


# ---------- placar pos-reestruturacao (30/08/2026) ----------
# Ate 29/08/2026 o placar por area vinha do cabecalho '#### <Area>: N/M' da
# Autopsia (autoavaliacao subjetiva de 0 a M, M escolhido pelo fundador). Em
# 30/08/2026 esse checklist saiu da Autopsia (ver
# `Tarefas/Agosto/Rotina Mestre - Rascunho 28-08-26.md`) e o "placar" muda de
# natureza: passa a ser a fracao objetiva de tarefas marcadas '#area' que
# foram concluidas no bloco do dia da nota da Semana. E uma metrica DIFERENTE
# da antiga (fracao real de tarefas, nao nota subjetiva de 0 a 10) - por isso
# fica em secao propria no relatorio, nunca somada a "Placar das 7 areas".
DIAS_SEMANA = (u"Segunda", u"Terça", u"Quarta", u"Quinta", u"Sexta", u"Sábado", u"Domingo")
RX_DIA_HEAD = re.compile(u"^####\\s+(%s)\\s*$" % u"|".join(DIAS_SEMANA))
RX_FIM_BLOCO = re.compile(r"^#{3,4}\s+\S")
RX_ITEM_CHECK = re.compile(r"^[-+*]\s*\[( |x|X)\]\s*(.*)$")
RX_TAG = re.compile(r"#([A-Za-zÀ-ú][\w-]*)")


def sem_acento(t):
    return u"".join(c for c in unicodedata.normalize("NFD", t) if unicodedata.category(c) != "Mn").lower()


def nome_area_de_tag(bruto):
    b = sem_acento(bruto)
    for a in AREAS:
        if sem_acento(a) == b:
            return a
    return None


def chave_data_arquivo(caminho):
    """Ordena a nota pela DATA do nome, nao pelo texto.

    Alfabeticamente 'Semana 31-08-26' vem DEPOIS de 'Semana 07-09-26', porque a
    comparacao le o dia antes do mes. Numa serie historica isso embaralha a
    ordem cronologica em silencio.
    """
    m = RX_DATA.search(os.path.basename(caminho))
    if not m:
        return dt.date.min
    d, mes, a = (int(x) for x in m.groups())
    try:
        return dt.date(2000 + a, mes, d)
    except ValueError:
        return dt.date.min


def adesao_semana_pos_reestruturacao():
    """area -> [(data_iso, feitas, total)], uma entrada por dia com pelo menos
    uma tarefa marcada com aquela #area no bloco '#### <Dia>' da nota da
    Semana. So enxerga dado a partir de quando a nota da Semana comecar a
    trazer 7 areas nas tags - o formato antigo (sem tag em toda tarefa) conta
    zero e nao aparece."""
    placar = defaultdict(list)
    for caminho in sorted(glob.glob(os.path.join(SEMANA_DIR, "Semana *.md")),
                          key=chave_data_arquivo):
        m = RX_DATA.search(os.path.basename(caminho))
        if not m:
            continue
        d, mes, a = (int(x) for x in m.groups())
        try:
            segunda = dt.date(2000 + a, mes, d)
        except ValueError:
            continue

        # Semana RECONSTITUIDA: o dia em andamento mora na autopsia desde
        # 07/09/2026 (ver cofre.py). Lendo o arquivo cru, o dia de hoje nunca
        # entraria na dissecacao da identidade.
        import cofre
        linhas = cofre.semana_reconstituida(caminho)

        dia_atual, contagem = None, defaultdict(lambda: [0, 0])

        def fecha_dia():
            if dia_atual is None:
                return
            data_dia = segunda + dt.timedelta(days=DIAS_SEMANA.index(dia_atual))
            for area, (feitas, total) in contagem.items():
                if total:
                    placar[area].append((data_dia.strftime("%Y-%m-%d"), feitas, total))

        for ln in linhas:
            l = ln.strip()
            mh = RX_DIA_HEAD.match(l)
            if mh:
                fecha_dia()
                dia_atual, contagem = mh.group(1), defaultdict(lambda: [0, 0])
                continue
            if RX_FIM_BLOCO.match(l) and not mh:
                fecha_dia()
                dia_atual, contagem = None, defaultdict(lambda: [0, 0])
                continue
            if dia_atual is None:
                continue
            mi = RX_ITEM_CHECK.match(l)
            if not mi:
                continue
            marca, texto = mi.group(1), mi.group(2)
            for tag in RX_TAG.findall(texto):
                area = nome_area_de_tag(tag)
                if area:
                    contagem[area][1] += 1
                    if marca.lower() == "x":
                        contagem[area][0] += 1
        fecha_dia()
    return placar


arquivos = []
for pasta in os.listdir(ROTINA):
    caminho_pasta = os.path.join(ROTINA, pasta)
    if not os.path.isdir(caminho_pasta):
        continue
    for nome in os.listdir(caminho_pasta):
        caminho = os.path.join(caminho_pasta, nome)
        if nome.lower().endswith(".md") and RX_DATA.search(nome):
            arquivos.append(caminho)
arquivos.sort(key=lambda p: dia_ord(os.path.basename(p)))


def estado_atual(caminho):
    """Extrai o inventario vigente da nota unica de Identidade."""
    estado = {"proposito": [], "inventario": {secao: [] for secao in INVENTARIO}}
    if not os.path.isfile(caminho):
        return estado

    with io.open(caminho, encoding="utf-8", errors="replace") as fh:
        linhas = fh.read().splitlines()

    secao = None
    campo_aberto = None
    for linha in linhas:
        texto = linha.strip()
        mh = RX_H.match(texto)
        if mh:
            titulo = limpar(mh.group(2))
            secao = titulo if titulo in INVENTARIO else None
            continue

        if texto.startswith(">"):
            corpo = texto.lstrip("> ").strip()
            achou = False
            for campo in ("Propósito Definido", "Meta do propósito definido",
                          "Medalha da conquista", "Propósito Maior", "Propósito maior"):
                if corpo.lower().startswith(campo.lower()):
                    achou = True
                    valor = corpo[len(campo):].lstrip(": ").strip()
                    reg = {"campo": campo, "valor": valor}
                    estado["proposito"].append(reg)
                    campo_aberto = reg if not valor else None
                    break
            if not achou and campo_aberto is not None:
                # valor do campo continua nas linhas de lista logo abaixo
                item_cit = RX_ITEM.match(corpo)
                if item_cit:
                    v = limpar(item_cit.group(2))
                    if v:
                        campo_aberto["valor"] = (campo_aberto["valor"] + " | " + v).strip(" |")
                else:
                    campo_aberto = None
            continue
        campo_aberto = None

        item = RX_ITEM.match(texto)
        if item and secao:
            valor = limpar(item.group(2))
            if valor:
                estado["inventario"][secao].append(valor)
    return estado


# inventario -> {chave: {"texto":..., "dias":[...]}}
inventario = {s: {} for s in INVENTARIO}
# area -> {chave_item: {"texto":..., "vezes":n, "feitas":n}}
adesao = {a: {} for a in AREAS}
placar = defaultdict(list)   # area -> [(dia, feito, total)]
proposito = []               # (dia, campo, valor)

for caminho in arquivos:
    dia = dia_ord(os.path.basename(caminho))
    with io.open(caminho, encoding="utf-8", errors="replace") as fh:
        linhas = fh.read().splitlines()

    secao = None
    area_atual = None
    for ln in linhas:
        crua = ln.rstrip()
        semtab = crua.strip()

        mh = RX_H.match(semtab)
        if mh:
            titulo = limpar(mh.group(2))
            ma = RX_AREA.match(titulo)
            if ma:
                # so "Fisico" normaliza o acento; "Financeiro" tambem comeca com f
                bruto = ma.group(1)
                nome_area = "Fisico" if bruto.lower() in ("fisico", "físico") else bruto
                area_atual, secao = nome_area, None
                placar[nome_area].append((dia, int(ma.group(2)), int(ma.group(3))))
            else:
                area_atual = None
                secao = titulo if titulo in INVENTARIO else None
            continue

        if semtab.startswith(">"):
            corpo = semtab.lstrip("> ").strip()
            for campo in ("Propósito Definido", "Propósito definido", "Missão central",
                          "Meta do propósito definido", "Meta da conquista central",
                          "Medalha da conquista", "Propósito maior"):
                if corpo.lower().startswith(campo.lower()):
                    valor = corpo[len(campo):].lstrip(": ").strip()
                    if valor:
                        proposito.append((dia, campo, valor))
                    break
            continue

        mi = RX_ITEM.match(semtab)
        if not mi:
            continue
        marca, texto = mi.group(1), limpar(mi.group(2))
        if not texto:
            continue

        if secao in INVENTARIO:
            k = chave(texto)
            if k:
                reg = inventario[secao].setdefault(k, {"texto": texto, "dias": []})
                reg["dias"].append(dia)
        elif area_atual and marca is not None:
            k = chave(texto)
            if k:
                reg = adesao[area_atual].setdefault(k, {"texto": texto, "vezes": 0, "feitas": 0})
                reg["vezes"] += 1
                if marca.lower() == "x":
                    reg["feitas"] += 1

# ---------- saida ----------
atual = estado_atual(IDENTIDADE)
out = ["# Disseccao das %d autopsias das intencoes" % len(arquivos), "",
       "Fonte historica: `Vault/Vida Pessoal/Rotina/<Mes>/`. Estado vigente: `Vault/Vida Pessoal/Identidade.md`.", ""]

out.append("## Evolucao do proposito")
out.append("")
vistos = set()
for dia, campo, valor in proposito:
    k = (campo, valor)
    if k in vistos:
        continue
    vistos.add(k)
    out.append("- **%s** | %s: %s" % (dia, campo, valor))

out.append("")
out.append("## Estado atual (Identidade)")
out.append("")
for item in atual["proposito"]:
    out.append("- **%s:** %s" % (item["campo"], item["valor"]))
for secao in INVENTARIO:
    out.append("- **%s:** %d itens" % (secao, len(atual["inventario"][secao])))

out.append("")
out.append("## Placar das 7 areas da vida")
out.append("")
out.append("| area | primeiro placar | ultimo placar | variacao |")
out.append("|---|---|---|---|")
for a in AREAS:
    if not placar[a]:
        continue
    p = sorted(placar[a])
    ini, fim = p[0], p[-1]
    out.append("| %s | %d/%d (%s) | %d/%d (%s) | %+d |"
               % (a, ini[1], ini[2], ini[0], fim[1], fim[2], fim[0], fim[1] - ini[1]))

adesao_semana = adesao_semana_pos_reestruturacao()
out.append("")
out.append("## Adesao por area pos-reestruturacao (via Semana, desde 30/08/2026)")
out.append("")
out.append("Fracao real de tarefas '#area' concluidas no bloco do dia, NAO a mesma escala da")
out.append("nota subjetiva /10 acima - nao comparar as duas tabelas diretamente.")
out.append("")
out.append("| area | dias com dado | media do periodo |")
out.append("|---|---|---|")
for a in AREAS:
    p = adesao_semana.get(a, [])
    if not p:
        continue
    media = 100.0 * sum(f for _, f, _ in p) / sum(t for _, _, t in p)
    out.append("| %s | %d | %d%% |" % (a, len(p), round(media)))

for secao in INVENTARIO:
    itens = sorted(inventario[secao].values(), key=lambda r: (r["dias"][0], r["texto"].lower()))
    out.append("")
    out.append("## %s (%d itens)" % (secao, len(itens)))
    out.append("")
    out.append("| item | desde | aparece em N notas |")
    out.append("|---|---|---|")
    for r in itens:
        out.append("| %s | %s | %d |" % (r["texto"], r["dias"][0], len(r["dias"])))

out.append("")
out.append("## Adesao por habito das 7 areas (o que ele marca e o que nunca marca)")
for a in AREAS:
    itens = [r for r in adesao[a].values() if r["vezes"] >= 3]
    if not itens:
        continue
    itens.sort(key=lambda r: (r["feitas"] / float(r["vezes"]), -r["vezes"]))
    out.append("")
    out.append("### %s" % a)
    out.append("")
    out.append("| habito | cobrado | cumprido | taxa |")
    out.append("|---|---|---|---|")
    for r in itens:
        out.append("| %s | %d | %d | %d%% |"
                   % (r["texto"], r["vezes"], r["feitas"], round(100.0 * r["feitas"] / r["vezes"])))

with io.open(os.path.join(BASE, "dissecacao.md"), "w", encoding="utf-8") as fh:
    fh.write("\n".join(out))

with io.open(os.path.join(BASE, "dissecacao.json"), "w", encoding="utf-8") as fh:
    json.dump({
        "notas": len(arquivos),
        "proposito": proposito,
        "estado_atual": atual,
        "placar": {a: placar[a] for a in AREAS if placar[a]},
        "adesao_semana_pos_reestruturacao": {a: adesao_semana[a] for a in AREAS if adesao_semana.get(a)},
        "inventario": {s: list(inventario[s].values()) for s in INVENTARIO},
        "adesao": {a: list(adesao[a].values()) for a in AREAS},
    }, fh, ensure_ascii=False, indent=2)

print("notas:", len(arquivos))
for s in INVENTARIO:
    print("  %-22s %d itens" % (s, len(inventario[s])))
for a in AREAS:
    print("  adesao %-14s %d habitos" % (a, len(adesao[a])))
