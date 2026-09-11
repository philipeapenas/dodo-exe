# -*- coding: utf-8 -*-
"""Cria a autopsia das intencoes do dia e TRAZ as secoes do dia pra dentro dela.

Roda de madrugada pela tarefa do Windows "Dodo.IA - Criar autopsia do dia": ele
acorda e a nota do dia ja existe, ja preenchida.

MUDANCA DE FUNDO (07/09/2026) - FIM DOS EMBEDS DAS SECOES DE TRABALHO
Ate aqui a autopsia era so uma vitrine: `![[Semana#Segunda]]` e companhia.
Embed do Obsidian e SO LEITURA, entao pra marcar um checkbox ou preencher o
tempo real ele tinha que abrir a nota da semana, editar la e voltar. Decisao
dele: "queria que fosse um so lugar a fonte de verdade e um painel otimizado
somente com as informacoes necessarias".

A saida NAO foi copiar (duas copias vivas = merge = linha perdida). A secao
MUDA DE CASA, e o motor `cofre.py` faz o transporte:

  aqui, de manha    recorta da nota da semana e cola na autopsia
  `fechar_dia.py`   devolve pra semana no fim do dia

Em qualquer instante um arquivo so e dono do texto. Detalhe do desenho em
`cofre.py`.

O QUE CONTINUA EMBED, E POR QUE
Proposito, Ano, Mes e Semana por prioridade. Ele LE essas secoes, nao edita
elas durante o dia. Materializar a meta do mes na autopsia criaria 30 copias
por mes, e marcar "MVP apresentado" numa quarta deixaria as outras 29
mentindo. Regra: materializa o que ele edita naquele dia, compoe na hora o
que ele so le. Quando o painel HTML do Dodo.IA existir, ele compoe essas
secoes lendo os dois arquivos e o embed some sozinho.

HISTORICO DAS SECOES (o que ja foi decidido e desfeito aqui)
  * 30/08: o checklist "Rotina nas 7 areas" saiu; virou a Rotina mestre em
    `Identidade.md > Habitos`, e quem marca cumprido e o checkbox do bloco do dia.
  * 31/08: "Metas deve conter somente a semana por prioridade" - o que ele
    cortou foi o arrasto do `### Metas:` inteiro, nao o conteudo.
  * 07/09: Mes e Ano voltam como embeds proprios, do horizonte mais longo pro
    mais curto, como ele escreveu a mao naquele dia (msg_007).
  * 01/09: volta a secao "Rotina e tarefas de hoje".
  * 02/09: 'Resolucao de Problemas' SAI da autopsia, porque espalhada em sete
    notas escondia o que ficou resolvido.
  * 07/09: 'Resolucao de Problemas' VOLTA, agora sem esconder nada - ela nao e
    copia, e a propria linha `- <Dia>:` da semana, que viaja e volta pro lugar.
    A decisao de 02/09 esta revertida de proposito, nao e regressao.
  * 07/09: entra 'Ideias', que ja existia na semana e nunca tinha chegado no
    painel do dia.

E IDEMPOTENTE em duas camadas: nao reescreve a nota se ela ja existe, e o
transporte pula qualquer secao que ja tenha conteudo no destino. E isso que
impede escrever por cima do que ele digitou no celular antes de sincronizar.
"""
import io
import os
import sys
import argparse
import datetime as dt

import cofre

VAULT = cofre.VAULT
ROTINA = cofre.ROTINA
SEMANA = cofre.SEMANA
MESES = cofre.MESES
DIAS = cofre.DIAS

CAB_METAS = u"### Metas:"
CAB_ROTINA = u"### Rotina e tarefas de hoje:"
CAB_PENDENCIAS = u"### Pendências:"
CAB_PERGUNTAS = u"### Perguntas:"
CAB_DESEJOS = u"### Desejos:"
CAB_IDEIAS = u"### Ideias:"
CAB_RESOLUCAO = u"### Resolução de Problemas:"
CAB_INSIGHTS = u"### Insights:"

# Embeds que SOBRAM: horizonte que ele le, nunca edita no dia. Ordem do mais
# longo pro mais curto, como ele mesmo escreveu a mao em 07/09/2026.
SEC_METAS = (u"Ano", u"Mês", u"Semana - por prioridade")

# Secoes que nascem VAZIAS aqui e sao preenchidas pelo transporte do cofre.
# A ordem e a que ele ja conhecia (Pendencias, Perguntas, Desejos), com Ideias
# e Resolucao de Problemas entrando depois, antes dos Insights.
CAB_TRANSPORTADAS = (CAB_ROTINA, CAB_PENDENCIAS, CAB_PERGUNTAS, CAB_DESEJOS,
                     CAB_IDEIAS, CAB_RESOLUCAO)


def nota_da_semana(alvo):
    """(nome_sem_extensao, existe) da nota da semana que cobre o dia alvo."""
    segunda = alvo - dt.timedelta(days=alvo.weekday())
    esperado = u"Semana %s" % segunda.strftime("%d-%m-%y")
    return esperado, os.path.isfile(os.path.join(SEMANA, esperado + u".md"))


def tem_heading(caminho_semana, heading):
    """True se a nota da semana tem esse heading.

    Embed pra heading que nao existe nao da erro no Obsidian: aparece vazio.
    Por isso a checagem vira aviso no console, nunca excecao.
    """
    if not os.path.isfile(caminho_semana):
        return False
    with io.open(caminho_semana, encoding="utf-8", errors="replace") as fh:
        for linha in fh:
            if cofre.normalizar(linha.strip().lstrip(u"#")) == cofre.normalizar(heading):
                return True
    return False


def montar(dia):
    """Esqueleto da nota. As secoes de trabalho nascem vazias, de proposito."""
    nome_dia = DIAS[dia.weekday()]
    semana, tem_semana = nota_da_semana(dia)

    corpo = [
        u"# Tarefa: Autópsia das intenções",
        u"",
        u"### Data: %s - %s" % (nome_dia, dia.strftime("%d/%m/%y")),
        u"",
        u"[[Identidade]] · [[Ativos]] · [[%s]] · [[Insights Geral]]" % semana,
        u"",
        u"![[Identidade#Propósito]]",
        u"",
        CAB_METAS,
    ]
    # Um embed por horizonte, separados por linha em branco. Sem o branco o
    # Obsidian cola os tres blocos num paragrafo so.
    for sec in SEC_METAS:
        corpo.append(u"![[%s#%s]]" % (semana, sec))
        corpo.append(u"")
    for cabecalho in CAB_TRANSPORTADAS:
        corpo += [cabecalho, u""]
    corpo += [CAB_INSIGHTS, u""]

    caminho_semana = os.path.join(SEMANA, semana + u".md")
    faltando = [h for h in SEC_METAS if not tem_heading(caminho_semana, h)]
    return u"\n".join(corpo), semana, tem_semana, faltando


def completar_secoes(dia, dry_run):
    """Poe na autopsia JA EXISTENTE as secoes que o novo formato exige.

    Uma autopsia escrita antes de 07/09/2026 nao tem 'Ideias' nem 'Resolucao de
    Problemas', e sem elas o transporte pula essas secoes calado. Insere so o que
    falta, na posicao certa, sem encostar no que ja esta escrito. Idempotente.
    """
    caminho = cofre.autopsia_do_dia(dia)
    if not caminho:
        return
    linhas, fim_linha = cofre.ler(caminho)
    faltando = [c for c in CAB_TRANSPORTADAS + (CAB_INSIGHTS,)
                if cofre.indice_do_titulo(linhas, c.strip(u"# :")) is None]
    if not faltando:
        return

    print(u"")
    print(u"Secoes que faltavam no formato novo: %s"
          % u", ".join(c.strip(u"# :") for c in faltando))
    ordem = list(CAB_TRANSPORTADAS) + [CAB_INSIGHTS]
    for cabecalho in faltando:
        # entra antes da primeira secao seguinte que ja existe; se nenhuma
        # existe, vai pro fim da nota
        posterior = ordem[ordem.index(cabecalho) + 1:]
        destino = len(linhas)
        for seguinte in posterior:
            k = cofre.indice_do_titulo(linhas, seguinte.strip(u"# :"))
            if k is not None:
                destino = k
                break
        while destino > 0 and not linhas[destino - 1].strip():
            destino -= 1
        linhas = linhas[:destino] + [u"", cabecalho, u""] + linhas[destino:]

    if dry_run:
        print(u"  (simulacao: a nota nao foi alterada)")
        return
    cofre.gravar(caminho, linhas, fim_linha)
    print(u"  secoes acrescentadas.")


def fechar_ontem_se_aberto(dia, dry_run):
    """Segunda rede do fechamento: se a tarefa das 01h51 nao rodou, fecha aqui.

    O PC pode ter sido desligado antes da hora. Sem isso o texto de ontem ficaria
    preso na autopsia de ontem e a semana passaria o dia com um buraco.
    """
    ontem = dia - dt.timedelta(days=1)
    if not cofre.dia_esta_aberto(ontem):
        return
    print(u"")
    print(u"O dia %s ficou aberto. Devolvendo antes de comecar hoje." %
          ontem.strftime("%d/%m/%y"))
    codigo, relato = cofre.devolver_posse(ontem, dry_run=dry_run)
    for linha in relato:
        print(u"  %s" % linha)
    if codigo == 2:
        print(u"  ATENCAO: houve conflito no fechamento de ontem. Resolva a mao.")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dia", help="AAAA-MM-DD (padrao: hoje)")
    ap.add_argument("--dry-run", action="store_true", help="mostra sem escrever")
    ap.add_argument("--sem-transporte", action="store_true",
                    help="so cria a nota, nao traz as secoes da semana")
    args = ap.parse_args()

    dia = dt.datetime.strptime(args.dia, "%Y-%m-%d").date() if args.dia else dt.date.today()

    pasta = os.path.join(ROTINA, MESES[dia.month - 1])
    destino = os.path.join(pasta, u"Autopsia das intencoes %s.md" % dia.strftime("%d-%m-%y"))
    ja_existe = cofre.autopsia_do_dia(dia)

    texto, semana, tem_semana, faltando = montar(dia)

    print(u"dia:     %s (%s)" % (dia.strftime("%d/%m/%y"), DIAS[dia.weekday()]))
    print(u"semana:  %s%s" % (semana, u"" if tem_semana else u"   <-- NAO EXISTE"))
    print(u"destino: %s" % (ja_existe or destino))

    if ja_existe:
        print(u"A nota do dia ja existe - nao vou reescreve-la.")

    if not tem_semana:
        print(u"")
        print(u"AVISO: a nota da semana ainda nao foi escrita.")
        print(u"       A nota do dia sai com as secoes VAZIAS e o link apontando pra ela.")
        print(u"       Rode de novo depois de planejar a semana pra trazer as secoes.")

    if tem_semana and faltando:
        print(u"")
        print(u"AVISO: a nota da semana nao tem o(s) heading(s): %s." % u", ".join(faltando))
        print(u"       O embed correspondente aparece VAZIO no Obsidian, sem erro nenhum.")

    if args.dry_run and not ja_existe:
        print(u"")
        print(u"SIMULACAO: nada foi escrito.")
        print(u"-" * 60)
        print(texto)

    if not ja_existe and not args.dry_run:
        if not os.path.isdir(pasta):
            os.makedirs(pasta)
            print(u"pasta do mes criada: %s" % pasta)
        with io.open(destino, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(texto)
        print(u"")
        print(u"Autopsia criada.")

    if ja_existe:
        completar_secoes(dia, args.dry_run)

    fechar_ontem_se_aberto(dia, args.dry_run)

    if args.sem_transporte:
        print(u"")
        print(u"--sem-transporte: as secoes ficaram na nota da semana.")
        return 0
    if args.dry_run and not ja_existe:
        print(u"")
        print(u"(o transporte so pode ser simulado depois que a nota existir)")
        return 0

    print(u"")
    print(u"Trazendo as secoes do dia pra autopsia:")
    codigo, relato = cofre.tomar_posse(dia, dry_run=args.dry_run)
    for linha in relato:
        print(u"  %s" % linha)
    return codigo


if __name__ == "__main__":
    sys.exit(main())
