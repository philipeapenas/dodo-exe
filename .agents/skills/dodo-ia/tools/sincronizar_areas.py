# -*- coding: utf-8 -*-
"""[APOSENTADO em 30/08/2026] Sincroniza o checklist das 7 areas da autopsia com o que foi concluido na nota da semana.

O checklist "Rotina nas 7 areas da vida" SAIU da Autopsia em 30/08/2026 (ver
`Tarefas/Agosto/Rotina Mestre - Rascunho 28-08-26.md` e `dissecar_autopsia.py`,
que ganhou a secao "Adesao por area pos-reestruturacao" como substituto). Sem
esse checklist na Autopsia, nao existe mais "irma" pra marcar - este script
nao tem mais o que fazer. Mantido no disco por historico (autopsias de ate
29/08/2026 ainda tem o checklist antigo e podem precisar dele), mas `main()`
detecta a ausencia do formato antigo e sai sem tentar sincronizar.

O desenho (fundador, 25/08/2026): toda tarefa concluida (`- [x]`) no bloco do
dia na nota da semana tem uma tarefa IRMA no checklist das 7 areas da
autopsia do mesmo dia - mesmo nome, organizada diferente (uma vive sob
`#### <Dia>` na semana, a outra sob `#### <Area>: X/Y` na autopsia). Quando
ele marca uma na semana, a irma na autopsia marca sozinha, sem ele ter que
marcar duas vezes.

NAO mexe no placar `X/Y` do cabecalho de cada area (`#### Emocional: 12/15`).
Testado em 25/08/2026: esse numero NAO e a contagem de checkboxes de topo da
secao - recalcular por contagem derrubou o placar de forma absurda (Espiritual
6/10 -> 2/8). O que ele representa de verdade fica pra ele confirmar antes de
qualquer automacao tocar nisso.

CASAMENTO: por NOME normalizado (sem acento, minusculo, cortado no primeiro
`(`, `[[` ou `:` - o que vier primeiro), dentro da secao da area certa (a
`#area` da tarefa na semana aponta pro `#### <Area>` da autopsia). So marca
quando existe EXATAMENTE UMA correspondencia. Tarefa da semana sem par na
autopsia, ou com mais de um par possivel, fica de fora e sai listada pro
fundador decidir a regra em vez do script adivinhar - por exemplo as 4
tarefas "1a/2a/3a/4a refeicao no dia" da semana viram um unico item "4
refeicoes no dia" na autopsia, e "Gerir ativos - Manha"/"- Tarde" viram um
unico "Gerir ativos"; o script nao sabe se isso e "qualquer uma marca" ou
"as duas juntas marcam".

NAO desmarca nada. So liga [ ] -> [x] quando a irma na semana esta [x].
Nunca mexe em item ja [x] na autopsia, mesmo que a irma na semana esteja [ ]
(perder o [x] apagaria dado de cumprimento que pode ter vindo de outro lugar).

Uso:
  python sincronizar_areas.py --dia Segunda --dry-run
  python sincronizar_areas.py --dia Segunda
  python sincronizar_areas.py --dia Segunda --semana "Semana 24-08-26" --autopsia "Autopsia das intencoes 24-08-26"
"""
import argparse
import codecs
import datetime as dt
import glob
import io
import os
import re
import sys
import unicodedata

if sys.platform == "win32":
    try:
        sys.stdout = codecs.getwriter("utf-8")(sys.stdout.buffer, "replace")
    except AttributeError:
        pass

# tools/ -> dodo-ia/ -> skills/ -> .agents (ou .claude)/ -> raiz do workspace
RAIZ = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", ".."))
VAULT = os.path.join(RAIZ, "Vault")
SEMANA_DIR = os.path.join(VAULT, "Vida Pessoal", "Semana")
ROTINA_DIR = os.path.join(VAULT, "Vida Pessoal", "Rotina")

AREAS = (u"espiritual", u"emocional", u"fisico", u"intelectual",
         u"relacionamento", u"lazer", u"financeiro")

# 'Semana 07-09-26.md' - a data e a identidade da nota, o titulo deriva.
RX_DATA_SEMANA = re.compile(u"Semana\\s+(\\d{2})-(\\d{2})-(\\d{2})")
RX_TAREFA_SEMANA = re.compile(
    u"^-\\s*\\[(?P<chk>[ xX])\\]\\s*(?P<rotulo>.+?)\\s*#(?P<area>%s)\\b" % u"|".join(AREAS),
    re.IGNORECASE)
RX_ITEM_AUTOPSIA = re.compile(u"^-\\s*\\[(?P<chk>[ xX])\\]\\s*(?P<rotulo>.+)$")
RX_HEADER_AREA = re.compile(u"^####\\s+(?P<area>[^:]+):\\s*(?P<x>\\d+)/(?P<y>\\d+)\\s*$")
DIAS = (u"Segunda", u"Ter\u00e7a", u"Quarta", u"Quinta", u"Sexta", u"S\u00e1bado", u"Domingo")


def sem_acento(t):
    return u"".join(c for c in unicodedata.normalize("NFD", t)
                    if unicodedata.category(c) != "Mn").lower()


def normaliza_rotulo(txt):
    """Corta no primeiro delimitador de duracao/link/rotulo e dobra acento+caixa."""
    txt = txt.strip()
    for sep in (u"(", u"[[", u":"):
        i = txt.find(sep)
        if i != -1:
            txt = txt[:i].strip()
    return sem_acento(txt)


def semana_mais_recente():
    """Nota da semana com a DATA mais recente no nome.

    Ordenar o nome como texto poe 'Semana 31-08-26' depois de 'Semana 07-09-26',
    porque compara o dia antes do mes. Em 07/09/2026 isso fez as ferramentas
    escreverem na semana PASSADA sem dar erro nenhum.
    """
    achados = []
    for caminho in glob.glob(os.path.join(SEMANA_DIR, "Semana *.md")):
        m = RX_DATA_SEMANA.search(os.path.basename(caminho))
        if not m:
            continue
        d, mes, ano = (int(x) for x in m.groups())
        try:
            achados.append((dt.date(2000 + ano, mes, d), caminho))
        except ValueError:
            continue
    if not achados:
        raise SystemExit(u"Nenhuma nota de semana com data no nome em %s" % SEMANA_DIR)
    return max(achados)[1]


def autopsia_do_dia(nome=None):
    if not os.path.isdir(ROTINA_DIR):
        raise SystemExit(u"Nao achei %s" % ROTINA_DIR)
    if nome:
        for mes in os.listdir(ROTINA_DIR):
            caminho = os.path.join(ROTINA_DIR, mes, nome + ".md")
            if os.path.isfile(caminho):
                return caminho
        raise SystemExit(u"Nao achei a autopsia '%s'" % nome)
    candidatos = []
    for mes in os.listdir(ROTINA_DIR):
        pasta = os.path.join(ROTINA_DIR, mes)
        if os.path.isdir(pasta):
            candidatos += glob.glob(os.path.join(pasta, "Autop*.md"))
    if not candidatos:
        raise SystemExit(u"Nenhuma autopsia encontrada em %s" % ROTINA_DIR)
    return max(candidatos, key=os.path.getmtime)


def tarefas_concluidas_da_semana(caminho, dia):
    linhas = io.open(caminho, encoding="utf-8").read().splitlines()
    try:
        ini = next(k for k, l in enumerate(linhas) if l.strip() == u"#### " + dia)
    except StopIteration:
        raise SystemExit(u"A nota da semana nao tem o bloco '#### %s'" % dia)
    fim = next((k for k, l in enumerate(linhas)
                if k > ini and (l.startswith(u"#### ") or l.startswith(u"### "))), len(linhas))

    concluidas = []
    for l in linhas[ini:fim]:
        m = RX_TAREFA_SEMANA.match(l.strip())
        if not m or m.group("chk").lower() != "x":
            continue
        concluidas.append((normaliza_rotulo(m.group("rotulo")), sem_acento(m.group("area"))))
    return concluidas


def mapeia_secoes(linhas):
    marcos = [(sem_acento(RX_HEADER_AREA.match(l.strip()).group("area")), k)
              for k, l in enumerate(linhas) if RX_HEADER_AREA.match(l.strip())]
    secoes = []
    for idx, (area, k) in enumerate(marcos):
        fim = marcos[idx + 1][1] if idx + 1 < len(marcos) else len(linhas)
        secoes.append((area, k, fim))
    return secoes


def itens_de_topo(linhas, ini_s, fim_s):
    """So os '- [ ]'/'- [x]' na coluna zero (sub-bullet com tab nao conta)."""
    for k in range(ini_s + 1, fim_s):
        l = linhas[k]
        if l.startswith(u"\t") or l.startswith(u"    ") or l.startswith(u" "):
            continue
        m = RX_ITEM_AUTOPSIA.match(l.strip())
        if m:
            yield k, m


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dia", required=True, help=u"Segunda, Terca, Quarta...")
    ap.add_argument("--semana", help=u"nome da nota da semana; padrao e a mais recente")
    ap.add_argument("--autopsia", help=u"nome da nota da autopsia; padrao e a mais recente")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    alvo = next((d for d in DIAS if sem_acento(d) == sem_acento(a.dia)), None)
    if not alvo:
        raise SystemExit(u"Dia invalido: %s. Use um de %s" % (a.dia, u", ".join(DIAS)))

    caminho_semana = os.path.join(SEMANA_DIR, a.semana + ".md") if a.semana else semana_mais_recente()
    if not os.path.isfile(caminho_semana):
        raise SystemExit(u"Nao achei %s" % caminho_semana)
    caminho_autopsia = autopsia_do_dia(a.autopsia)

    linhas = io.open(caminho_autopsia, encoding="utf-8").read().splitlines()
    secoes = mapeia_secoes(linhas)
    if not secoes:
        print(u"APOSENTADO: '%s' nao tem checklist de areas (formato pos-30/08/2026)."
              % os.path.basename(caminho_autopsia))
        print(u"Nao ha mais 'irma' pra sincronizar - ver o docstring deste script.")
        return 0

    concluidas = tarefas_concluidas_da_semana(caminho_semana, alvo)

    print(u"nota semana:   %s" % os.path.basename(caminho_semana))
    print(u"nota autopsia: %s" % os.path.basename(caminho_autopsia))
    print(u"dia:           %s\n" % alvo)

    marcadas, sem_par, ambiguas = 0, [], []
    for rotulo, area in concluidas:
        secao = next((s for s in secoes if s[0] == area), None)
        if secao is None:
            sem_par.append((rotulo, area, u"area '%s' nao existe na autopsia" % area))
            continue
        _, ini_s, fim_s = secao

        candidatos = [(k, m) for k, m in itens_de_topo(linhas, ini_s, fim_s)
                      if normaliza_rotulo(m.group("rotulo")) == rotulo]

        if not candidatos:
            sem_par.append((rotulo, area, u"nenhum item com esse nome na secao"))
            continue
        if len(candidatos) > 1:
            ambiguas.append((rotulo, area, len(candidatos)))
            continue

        k, m = candidatos[0]
        if m.group("chk").lower() == "x":
            continue
        linhas[k] = re.sub(u"\\[ \\]", u"[x]", linhas[k], count=1)
        print(u"  marcada: %s (#%s)" % (rotulo, area))
        marcadas += 1

    print(u"\n%d tarefa(s) marcada(s)." % marcadas)
    if sem_par:
        print(u"\nSEM PAR (nao mexi - decida a regra):")
        for rotulo, area, motivo in sem_par:
            print(u"  - %s [#%s]: %s" % (rotulo, area, motivo))
    if ambiguas:
        print(u"\nAMBIGUAS (mais de um item com esse nome - nao mexi):")
        for rotulo, area, n in ambiguas:
            print(u"  - %s [#%s]: %d candidatos" % (rotulo, area, n))

    if a.dry_run:
        print(u"\nSIMULACAO: nada foi escrito.")
        return 0
    io.open(caminho_autopsia, "w", encoding="utf-8", newline="\n").write(u"\n".join(linhas) + u"\n")
    print(u"\nAutopsia atualizada.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
