# -*- coding: utf-8 -*-
"""Fecha o dia: devolve as secoes pra nota da semana e arquiva os insights.

E a outra metade do `criar_autopsia.py`. De manha as secoes de trabalho se
mudam pra autopsia; aqui elas voltam pra semana, que volta a ter os sete dias
inteiros pra revisao de domingo. Desenho completo em `cofre.py`.

QUANDO RODA
Pela tarefa do Windows "Dodo.IA - Fechar o dia", agendada pra 30 minutos DEPOIS
do fim do dia dele - decisao dele em 07/09/2026: "01h21 e o final do dia de
hoje, as 01h51 ele deve rodar, e isso adaptado por dia". O horario nao e fixo:
sai da cascata do proprio bloco do dia e e reescrito pelo `agendar_fechamento.py`
toda vez que a cascata muda. Se o PC estiver desligado na hora, a tarefa roda
quando ele ligar, e o `criar_autopsia.py` da manha seguinte fecha o dia anterior
que tiver ficado aberto. Duas redes.

OS INSIGHTS NAO VOLTAM PRA SEMANA - VAO PRO ACERVO
Pedido dele: "insights devem ser levados pra nota de insights organizadamente".
Cada bloco `- DD/MM/YY <Tema>:` da autopsia e arquivado em `Insights/Insights
Geral.md`, embaixo do heading daquele tema e na data do dia, que e o formato que
a nota ja usa. Tema que nao casa com heading existente NAO e arquivado e NAO e
apagado: o script para, lista os temas validos e deixa o texto onde esta.
Inventar secao nova numa nota de acervo seria pior que nao arquivar.
Nasceu da pendencia de automatizar o arquivamento dos insights.

Uso:
  python fechar_dia.py --dry-run          # mostra o que faria
  python fechar_dia.py                    # fecha hoje
  python fechar_dia.py --dia 2026-09-07   # fecha um dia especifico
"""
import argparse
import io
import os
import re
import sys
import datetime as dt

import cofre

RX_BLOCO_INSIGHT = re.compile(r"^-\s+(\d{2}/\d{2}/\d{2})\s+(.+?)\s*:?\s*$")
RX_GRUPO_DATA = re.compile(r"^(\d{2}/\d{2}/\d{2})\s*:\s*$")


def temas_do_acervo(linhas):
    """Todos os headings de `Insights Geral.md`, na ordem em que aparecem."""
    achados = []
    for linha in linhas:
        m = cofre.RX_TITULO.match(linha)
        if m:
            achados.append(m.group(1).strip())
    return achados


def blocos_de_insight(corpo):
    """[(tema, [textos])] lidos da secao Insights da autopsia.

    Devolve tambem o que nao deu pra rotear, em `soltos`: linha de nivel 0 que
    nao e um cabecalho `- DD/MM/YY Tema:`. Isso NAO e erro do fundador, e so
    texto que o script nao sabe pra onde mandar - fica na autopsia.
    """
    blocos, soltos, atual = [], [], None
    for linha in corpo:
        if not linha.strip():
            continue
        if cofre.profundidade(linha) == 0:
            m = RX_BLOCO_INSIGHT.match(linha.strip())
            if m:
                atual = (m.group(2).strip(), [])
                blocos.append(atual)
                continue
            atual = None
            soltos.append(linha)
            continue
        if atual is None:
            soltos.append(linha)
            continue
        texto = linha.strip()
        atual[1].append(texto[2:].strip() if texto.startswith(u"- ") else texto)
    return [b for b in blocos if b[1]], soltos


def arquivar_no_acervo(linhas, tema, textos, dia):
    """Poe os textos embaixo do heading do tema, na data do dia.

    Reaproveita o grupo `DD/MM/YY:` se ele ja existir naquele tema; senao cria
    no FIM da secao, que e como a nota cresce (data mais nova embaixo).
    """
    ini, fim = cofre.limites_da_secao(linhas, tema)
    if ini is None:
        return None, u"tema '%s' nao existe no acervo" % tema

    carimbo = dia.strftime("%d/%m/%y")
    novas = [u"- %s" % t for t in textos]

    for i in range(ini, fim):
        m = RX_GRUPO_DATA.match(linhas[i].strip())
        if m and m.group(1) == carimbo:
            corte = i + 1
            while corte < fim and linhas[corte].strip():
                corte += 1
            return linhas[:corte] + novas + linhas[corte:], \
                u"%d item(ns) no grupo %s ja existente" % (len(novas), carimbo)

    corte = fim
    while corte > ini and not linhas[corte - 1].strip():
        corte -= 1
    bloco = [u"", u"%s:" % carimbo] + novas
    return linhas[:corte] + bloco + linhas[corte:], \
        u"%d item(ns) em grupo %s novo" % (len(novas), carimbo)


def arquivar_insights(dia, dry_run):
    """Move os insights da autopsia pro acervo. Devolve (codigo, relato)."""
    aut = cofre.autopsia_do_dia(dia)
    if not aut:
        return 1, [u"a autopsia de %s nao existe" % dia.strftime("%d/%m/%y")]
    if not os.path.isfile(cofre.INSIGHTS_GERAL):
        return 1, [u"acervo nao encontrado: %s" % cofre.INSIGHTS_GERAL]

    linhas_aut, fim_aut = cofre.ler(aut)
    corpo = cofre.corpo_da_secao(linhas_aut, u"Insights")
    if corpo is None:
        return 0, [u"a autopsia nao tem a secao Insights"]
    if cofre._vazia(corpo):
        return 0, [u"nenhum insight escrito hoje"]

    blocos, soltos = blocos_de_insight(corpo)
    if not blocos:
        return 0, [u"nada com o formato '- DD/MM/YY <Tema>:' - deixando como esta"]

    linhas_ac, fim_ac = cofre.ler(cofre.INSIGHTS_GERAL)
    antes_ac = list(linhas_ac)
    relato, arquivados, recusados = [], [], []

    for tema, textos in blocos:
        novas, nota = arquivar_no_acervo(linhas_ac, tema, textos, dia)
        if novas is None:
            relato.append(u"%-22s RECUSADO: %s" % (tema, nota))
            recusados.append((tema, textos))
            continue
        linhas_ac = novas
        relato.append(u"%-22s -> Insights Geral (%s)" % (tema, nota))
        arquivados.append(tema)

    if recusados:
        relato.append(u"")
        relato.append(u"Temas validos no acervo: %s"
                      % u", ".join(temas_do_acervo(antes_ac)))
        relato.append(u"O que foi recusado continua na autopsia, nada se perdeu.")

    if not arquivados:
        return 2, relato

    # o que sobra na autopsia: o que nao deu pra rotear, mais o rastro do resto
    resto = list(soltos)
    for tema, textos in recusados:
        resto.append(u"- %s %s:" % (dia.strftime("%d/%m/%y"), tema))
        resto += [u"\t- %s" % t for t in textos]
    resto.append(u"> Arquivado em [[Insights Geral]]: %s" % u", ".join(arquivados))
    linhas_aut = cofre.substituir_secao(linhas_aut, u"Insights", resto)

    if dry_run:
        cofre.mostrar_diff(antes_ac, linhas_ac, u"Insights Geral.md")
        return 0, relato
    cofre.gravar(cofre.INSIGHTS_GERAL, linhas_ac, fim_ac)
    cofre.gravar(aut, linhas_aut, fim_aut)
    return 0, relato


def registrar_log(dia, texto):
    """Uma linha por execucao, porque as 01h51 ninguem esta olhando a tela.

    Sem isso, um fechamento que falhou pela tarefa do Windows seria
    indistinguivel de um que nem rodou - e o rastro so apareceria dias depois,
    como texto que sumiu da nota da semana.
    """
    try:
        if not os.path.isdir(cofre.BACKUP):
            os.makedirs(cofre.BACKUP)
        alvo = os.path.join(cofre.BACKUP, "fechar_dia.log")
        with io.open(alvo, "a", encoding="utf-8") as fh:
            fh.write(u"%s  %s  %s\n" % (
                dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                dia.strftime("%d/%m/%y"), texto))
    except Exception:
        pass  # log e conveniencia: nunca pode derrubar o fechamento


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dia", help="AAAA-MM-DD (padrao: hoje)")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--sem-insights", action="store_true",
                    help="so devolve as secoes, nao arquiva insight")
    args = ap.parse_args()

    dia = dt.datetime.strptime(args.dia, "%Y-%m-%d").date() if args.dia else dt.date.today()

    print(u"fechando %s (%s)" % (dia.strftime("%d/%m/%y"), cofre.nome_do_dia(dia)))
    if not cofre.dia_esta_aberto(dia):
        print(u"O dia ja esta fechado - as secoes estao na nota da semana.")
        if not args.dry_run:
            registrar_log(dia, u"ja estava fechado")
        if args.sem_insights:
            return 0
    else:
        print(u"")
        print(u"Devolvendo as secoes pra nota da semana:")
        codigo, relato = cofre.devolver_posse(dia, dry_run=args.dry_run)
        for linha in relato:
            print(u"  %s" % linha)
        if codigo == 1:
            if not args.dry_run:
                registrar_log(dia, u"ERRO: %s" % u"; ".join(relato))
            return 1
        if codigo == 2:
            print(u"")
            print(u"ATENCAO: alguma secao ganhou conteudo na semana enquanto estava")
            print(u"         na autopsia. Existem dois textos e quem decide e voce.")
            print(u"         Nada foi sobrescrito. Compare os dois e junte a mao.")
        if not args.dry_run:
            registrar_log(dia, u"devolvido (codigo %d): %s" % (
                codigo, u"; ".join(l.strip() for l in relato if u"nada a devolver" not in l)))

    if args.sem_insights:
        return 0

    print(u"")
    print(u"Arquivando os insights:")
    codigo_i, relato_i = arquivar_insights(dia, args.dry_run)
    for linha in relato_i:
        print(u"  %s" % linha)

    if args.dry_run:
        print(u"")
        print(u"SIMULACAO: nada foi escrito.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
