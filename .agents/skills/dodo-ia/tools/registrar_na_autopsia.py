# -*- coding: utf-8 -*-
"""Escreve insight e pendencia na autopsia das intencoes do dia.

Fase 2 do projeto Dodo.IA. Ataca os habitos de registro do fundador, que estao em
11% e 12% de cumprimento ("anotar insights no caderno" e "no obsidian"): o que sai
de uma sessao de trabalho passa a ser registrado sem ele digitar.

Regras de seguranca (a autopsia e nota viva, sincroniza pro celular):
  - Escreve SO dentro da secao alvo. O resto do arquivo nao e tocado.
  - Faz backup antes de qualquer escrita.
  - NAO cria a autopsia do dia. Escrever a nota e ritual dele; se nao existe, para.
  - Preserva tabulacao e final de linha do arquivo original.

Uso:
  python registrar_na_autopsia.py --dry-run --tema Dev --insight "texto"
  python registrar_na_autopsia.py --tema Dev --insight "um" --insight "dois"
  python registrar_na_autopsia.py --sob "Ativos > OP Loja > Site" --pendencia "texto"
"""
import argparse
import datetime as dt
import glob
import io
import os
import re
import shutil
import sys

# tools/ -> dodo-ia/ -> skills/ -> .agents (ou .claude)/ -> raiz do workspace
RAIZ = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", ".."))
VAULT = os.path.join(RAIZ, "Vault")
PESSOAL = os.path.join(VAULT, "Vida Pessoal")
ROTINA = os.path.join(PESSOAL, "Rotina")
SEMANA = os.path.join(PESSOAL, "Semana")
BACKUP = os.path.join(RAIZ, ".backups", "autopsia")
RX_DATA_ARQ = re.compile(r"(\d{2})-(\d{2})-(\d{2})")
RX_TITULO = re.compile(r"^#{2,4}\s+(.+?)\s*:?\s*$")


def autopsia_de_hoje(dia):
    """Caminho da autopsia daquele dia, ou None. A data esta no NOME do arquivo."""
    for caminho in glob.glob(os.path.join(ROTINA, "*", "*.md")):
        if os.path.basename(os.path.dirname(caminho)) == "Semana":
            continue  # nota de semana nao e autopsia
        m = RX_DATA_ARQ.search(os.path.basename(caminho))
        if not m:
            continue
        d, mes, ano = (int(x) for x in m.groups())
        try:
            if dt.date(2000 + ano, mes, d) == dia:
                return caminho
        except ValueError:
            continue
    return None


def semana_do_dia(dia):
    """Nota da semana que cobre o dia. O nome carrega a segunda que abre a semana."""
    for caminho in sorted(glob.glob(os.path.join(SEMANA, "*.md")), reverse=True):
        m = RX_DATA_ARQ.search(os.path.basename(caminho))
        if not m:
            continue
        d, mes, ano = (int(x) for x in m.groups())
        try:
            segunda = dt.date(2000 + ano, mes, d)
        except ValueError:
            continue
        if 0 <= (dia - segunda).days <= 6:
            return caminho
    return None


def ler(caminho):
    with io.open(caminho, encoding="utf-8", newline="") as fh:
        bruto = fh.read()
    fim = "\r\n" if "\r\n" in bruto else "\n"
    return bruto.replace("\r\n", "\n").split("\n"), fim


def limites_da_secao(linhas, nomes):
    """(inicio, fim) das linhas de conteudo da secao. inicio = linha apos o titulo."""
    for i, linha in enumerate(linhas):
        m = RX_TITULO.match(linha)
        if not m:
            continue
        if m.group(1).strip().lower() in [n.lower() for n in nomes]:
            for j in range(i + 1, len(linhas)):
                if RX_TITULO.match(linhas[j]):
                    return i + 1, j
            return i + 1, len(linhas)
    return None, None


def profundidade(linha):
    return len(linha) - len(linha.lstrip("\t"))


def fim_do_bloco(linhas, pos, ini_secao, fim_secao):
    """Ultima linha da subarvore que comeca em `pos` (exclusivo)."""
    base = profundidade(linhas[pos])
    fim = pos + 1
    while fim < fim_secao:
        linha = linhas[fim]
        if linha.strip() and profundidade(linha) <= base:
            break
        fim += 1
    while fim > pos + 1 and not linhas[fim - 1].strip():
        fim -= 1  # nao engole a linha em branco que separa blocos
    return fim


def inserir_insight(linhas, tema, textos, dia):
    ini, fim = limites_da_secao(linhas, ["Insights"])
    if ini is None:
        raise SystemExit("Secao '### Insights' nao encontrada na autopsia.")

    carimbo = "%s %s" % (dia.strftime("%d/%m/%y"), tema)
    alvo = None
    for i in range(ini, fim):
        texto = linhas[i].strip()
        if texto.startswith("- ") and texto[2:].rstrip().rstrip(":").strip() == carimbo:
            alvo = i
            break

    novas = ["\t- " + t for t in textos]
    if alvo is not None:
        corte = fim_do_bloco(linhas, alvo, ini, fim)
        return linhas[:corte] + novas + linhas[corte:], "acrescentado ao bloco '%s'" % carimbo

    corte = fim
    while corte > ini and not linhas[corte - 1].strip():
        corte -= 1
    bloco = ["- %s: " % carimbo] + novas
    if corte > ini and linhas[corte - 1].strip():
        bloco = [""] + bloco
    return linhas[:corte] + bloco + linhas[corte:], "bloco novo '%s' criado" % carimbo


def inserir_pendencia(linhas, caminho_txt, textos):
    ini, fim = limites_da_secao(linhas, ["Pendencias", "Pendências"])
    if ini is None:
        raise SystemExit("Secao '### Pendencias' nao encontrada na autopsia.")

    partes = [p.strip() for p in caminho_txt.split(">") if p.strip()]
    if not partes:
        raise SystemExit("Informe o caminho com --sob, ex: --sob \"Ativos > OP Loja\"")

    linhas = list(linhas)
    bloco_ini, bloco_fim = ini, fim
    criados = []
    for nivel, parte in enumerate(partes):
        achou = None
        for i in range(bloco_ini, bloco_fim):
            texto = linhas[i].strip()
            if not texto.startswith("- "):
                continue
            if profundidade(linhas[i]) != nivel:
                continue
            if texto[2:].rstrip().rstrip(":").strip().lower() == parte.lower():
                achou = i
                break
        if achou is None:
            corte = bloco_fim
            nova = "\t" * nivel + "- %s: " % parte
            prefixo = [""] if nivel == 0 and corte > bloco_ini and linhas[corte - 1].strip() else []
            linhas = linhas[:corte] + prefixo + [nova] + linhas[corte:]
            deslocou = len(prefixo) + 1
            fim += deslocou
            achou = corte + len(prefixo)
            bloco_fim = fim
            criados.append(parte)
        bloco_ini = achou + 1
        bloco_fim = fim_do_bloco(linhas, achou, ini, fim)

    novas = ["\t" * len(partes) + "- [ ] " + t for t in textos]
    linhas = linhas[:bloco_fim] + novas + linhas[bloco_fim:]
    nota = "sob %s" % " > ".join(partes)
    if criados:
        nota += " (criado: %s)" % ", ".join(criados)
    return linhas, nota


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--insight", action="append", default=[], help="pode repetir")
    ap.add_argument("--tema", help="Dev, Mente, Fisico, Auto Conhecimento, Operacao...")
    ap.add_argument("--pendencia", action="append", default=[], help="pode repetir")
    ap.add_argument("--sob", help='caminho, ex: "Ativos > OP Loja > Site"')
    ap.add_argument("--dia", help="AAAA-MM-DD (padrao: hoje)")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    if args.insight and not args.tema:
        raise SystemExit("--insight exige --tema")
    if args.pendencia and not args.sob:
        raise SystemExit("--pendencia exige --sob")
    if not args.insight and not args.pendencia:
        raise SystemExit("Nada a registrar. Use --insight ou --pendencia.")

    dia = dt.datetime.strptime(args.dia, "%Y-%m-%d").date() if args.dia else dt.date.today()

    # o insight vive na autopsia do dia; a pendencia vive na nota da semana
    alvos = []
    if args.insight:
        caminho = autopsia_de_hoje(dia)
        if not caminho:
            print("A autopsia de %s nao existe ainda." % dia.strftime("%d/%m/%y"))
            print("Escrever a autopsia do dia e ritual do fundador - este script nao cria.")
            return 1
        alvos.append((caminho, "insight"))
    if args.pendencia:
        # Desde 07/09/2026 Pendencias nao mora sempre na semana: durante o dia
        # ela esta na autopsia (ver cofre.py). Escrever na semana com a secao
        # fora colocaria a pendencia num buraco - e ela sumiria na devolucao,
        # ou pior, viraria conflito e travaria o fechamento inteiro.
        import cofre
        caminho = cofre.dono_da_secao(u"Pendências", dia)[0]
        if not caminho:
            print("Nao achei a secao Pendencias nem na autopsia de %s nem na semana."
                  % dia.strftime("%d/%m/%y"))
            print("Crie a nota da semana (nome: Semana DD-MM-AA, data da segunda) e rode de novo.")
            return 1
        alvos.append((caminho, "pendencia"))

    import difflib
    gravar = []
    for caminho, tipo in alvos:
        linhas, fim_linha = ler(caminho)
        original = list(linhas)
        if tipo == "insight":
            linhas, nota = inserir_insight(linhas, args.tema, args.insight, dia)
        else:
            linhas, nota = inserir_pendencia(linhas, args.sob, args.pendencia)

        print("%s: %s" % (tipo, os.path.basename(caminho)))
        print("  %s" % nota)
        for linha in difflib.unified_diff(original, linhas, lineterm="", n=1):
            if linha.startswith("+") and not linha.startswith("+++"):
                print("  + %s" % linha[1:].replace("	", "    "))
            elif linha.startswith("@@"):
                print("  %s" % linha)
        print()
        gravar.append((caminho, linhas, fim_linha))

    if args.dry_run:
        print("SIMULACAO: o arquivo nao foi alterado.")
        return 0

    if not os.path.isdir(BACKUP):
        os.makedirs(BACKUP)
    for caminho, linhas, fim_linha in gravar:
        copia = os.path.join(BACKUP, "%s_%s" % (
            dt.datetime.now().strftime("%Y%m%d-%H%M%S"), os.path.basename(caminho)))
        shutil.copy2(caminho, copia)
        with io.open(caminho, "w", encoding="utf-8", newline="") as fh:
            fh.write(fim_linha.join(linhas))
        print("gravado: %s | backup em %s" % (os.path.basename(caminho), copia))
    return 0


if __name__ == "__main__":
    sys.exit(main())
