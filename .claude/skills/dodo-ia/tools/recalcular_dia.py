# -*- coding: utf-8 -*-
"""Recalcula as horas de um dia da nota da semana a partir do horario REAL de acordar.

O desenho (fundador, 24/08/2026): na nota da semana toda tarefa e

    - [ ] Nome da tarefa (duracao -> real): HORA #area

e toda HORA e um deslocamento fixo desde o `> Acordar:` do cabecalho do dia.
Acordou fora da meta? Move a ancora e o dia inteiro desliza junto.

NAO desliza: tarefa com hora marcada com outra pessoa (reuniao, compromisso).
Elas sao reconhecidas pela linha `> Hora marcada` logo abaixo do bloco e ficam
onde estao - o mundo nao remarca porque ele dormiu demais.

SEGUNDO MODO - `--apartir-de` (fundador, 24/08/2026)
---------------------------------------------------
O acordar nao e a unica ancora que escorrega. Quando ele abre um bloco de
operacao fora da hora - "comecei as 15h45, e a meta continua sendo 6h" - o que
desliza e so o RESTO do dia, nao o dia todo: o que ja foi feito ficou na hora
que foi feito, e mexer nisso apagaria o dado de cumprimento.

Entao este modo pega a tarefa em andamento, soma a duracao declarada dela, e
empurra dai pra frente **apenas as tarefas nao concluidas** (`- [ ]`),
preservando o espacamento que ele mesmo escreveu entre elas.

TERCEIRO MODO - `--realinhar` (fundador, 25/08/2026)
-----------------------------------------------------
Os dois modos acima preservam o espacamento ORIGINAL entre as tarefas - so
deslocam tudo por um delta constante. Este modo e diferente: ele RECALCULA
cada horario do zero, andando pela nota na ordem em que as tarefas aparecem
(que e a ordem em que ele as executa e marca), somando cumulativamente:

  - a duracao REAL (o numero DEPOIS da seta, `(estimado -> real)`) de quem
    ja esta concluida (`- [x]`) - e o dado de verdade, uma vez que existe;
  - a duracao ESTIMADA (o numero ANTES da seta) de quem ainda esta pendente
    (`- [ ]`), porque a real ainda nao existe.

Cada horario resultante e arredondado pro multiplo de 5 minutos mais
proximo antes de escrever na linha - o pedido dele foi "a cada 5m organizado
a sequencia em que as tarefas foram concluidas".

**A JANELA E A ANCORA, nao a tarefa anterior** (02/09/2026). Ao cruzar um
cabecalho `##### HHhMM-HHhMM (...)` o cursor volta pro inicio daquela janela.
Sem isso, a Inercia - que declara 3h30 de itens numa janela de 2h - empurrava o
dia inteiro, e as tarefas apareciam sob cabecalhos que nao continham a hora
delas. Janela que nao comporta os proprios itens vira AVISO 'ESTOUROU', com
quantos minutos passou, em vez de vazar em silencio pra janela seguinte.

Tarefa-ancora (`> Hora marcada` embaixo, compromisso com outra pessoa) nunca
tem o horario dela sobrescrito - mas a soma cumulativa RESSINCRONIZA pro
horario escrito dela antes de continuar, senao um atraso ou adiantamento
acumulado nas tarefas anteriores vazaria por cima de um horario que e fixo.

MODO PELO ACORDAR - `--pelo-acordar` (fundador, 02/09/2026)
-----------------------------------------------------------
"quero que o ajuste dos horarios seja baseado automaticamente no '> Acordar:'
aonde eu possa ajustar somente o valor ali e ja recalcular o resto".

Ele edita a linha na nota e roda o comando sem repetir a hora. A ancora VELHA
nao esta escrita em lugar nenhum, entao vem da primeira tarefa do bloco, que
por desenho fica no offset zero. Desliza tarefas e cabecalhos de janela.

Uso:
  python recalcular_dia.py --dia Quarta --pelo-acordar --dry-run
  python recalcular_dia.py --dia Quarta --pelo-acordar

  python recalcular_dia.py --dia Segunda --acordar 08:30 --dry-run
  python recalcular_dia.py --dia Segunda --acordar 08:30
  python recalcular_dia.py --dia Segunda --acordar 08:30 --semana "Semana 24-08-26"

  python recalcular_dia.py --dia Segunda --apartir-de "Gerir ativos - Tarde" --dry-run
  python recalcular_dia.py --dia Segunda --apartir-de "Gerir ativos - Tarde" --inicio 15:45

  python recalcular_dia.py --dia Segunda --realinhar --dry-run
  python recalcular_dia.py --dia Segunda --realinhar
"""
import argparse
import codecs
import datetime as dt
import io
import os
import re
import sys

import cofre

if sys.platform == "win32":
    try:
        sys.stdout = codecs.getwriter("utf-8")(sys.stdout.buffer, "replace")
    except AttributeError:
        pass

# tools/ -> dodo-ia/ -> skills/ -> .agents (ou .claude)/ -> raiz do workspace
RAIZ = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", ".."))
VAULT = os.path.join(RAIZ, "Vault")
SEMANA = os.path.join(VAULT, "Vida Pessoal", "Semana")

# A faixa de cada janela e dado DERIVADO do acordar (offset fixo declarado na
# Rotina mestre). Reconstruir da fonte e o unico jeito idempotente de consertar
# cabecalho - ver sincroniza_janelas(). O import e tolerante de proposito: se o
# parser da Identidade quebrar, o recalculo de HORA continua funcionando.
try:
    from montar_esqueleto_dia import ler_rotina_mestre, cabecalho_janela
except ImportError:
    ler_rotina_mestre = cabecalho_janela = None

# `- [ ] Nome (dur -> real): 14h30 #area`  ou  `- [ ] Nome: 5h #area`
RX_TAREFA = re.compile(
    u"^(?P<ini>\\s*-\\s*\\[[ xX]\\]\\s*.*?):\\s*(?P<hora>\\d{1,2}h(?:\\d{2})?)(?P<fim>.*)$")
RX_ACORDAR = re.compile(u"^>\\s*Acordar:\\s*(\\d{1,2})h(\\d{2})?", re.IGNORECASE)
# `##### 07h-11h (Janela de Ouro) - Foco: ...` - o cabecalho de janela do bloco
# do dia. A faixa e hora de relogio contada do acordar, entao desliza junto.
RX_JANELA = re.compile(
    u"^(?P<pre>\\s*#{3,6}\\s+)(?P<de>\\d{1,2}h(?:\\d{2})?)-(?P<ate>\\d{1,2}h(?:\\d{2})?)(?P<resto>.*)$")
RX_MARCADA = re.compile(u"^\\s*>\\s*Hora marcada", re.IGNORECASE)
# A duracao declarada vive SEMPRE dentro do parentese, antes da seta:
# `(6h -> )`, `(1h30 -> )`, `(1h30m -> 1h30 )`, `(15m -> )`.
RX_DUR = re.compile(
    u"\\(\\s*(?:(?P<h>\\d{1,2})h(?P<hm>\\d{1,2})?m?|(?P<m>\\d{1,3})m)\\s*(?:\u2192|->)")
RX_CONCLUIDA = re.compile(u"^\\s*-\\s*\\[[xX]\\]")
DIAS = (u"Segunda", u"Ter\u00e7a", u"Quarta", u"Quinta", u"Sexta", u"S\u00e1bado", u"Domingo")


def le_acordar(linhas, ini, fim, dia):
    """Minutos do '> Acordar: HHhMM' do bloco. E a unica ancora de horario do dia."""
    for l in linhas[ini:fim]:
        m = RX_ACORDAR.match(l.strip())
        if m:
            return int(m.group(1)) * 60 + int(m.group(2) or 0)
    raise SystemExit(u"O bloco de %s nao tem a linha '> Acordar: HHhMM'." % dia)


def sincroniza_janelas(linhas, ini, fim, acordar_min):
    """Reescreve os cabecalhos de janela do bloco a partir da Rotina mestre.

    A faixa de uma janela nao e escolha: e offset fixo desde o acordar, declarado
    em `Identidade.md > Rotina mestre` (decisao dele em 02/09/2026). Por isso ela
    e RECONSTRUIDA da fonte, nunca deslizada por delta. Em 07/09/2026 ele moveu os
    dois primeiros cabecalhos a mao e parou; o bloco ficou com metade dos
    cabecalhos numa grade e metade na outra, e nenhum delta unico consertava os
    dois lados. Reconstruir e idempotente e nao depende do estado anterior.

    Nao encosta em nada quando a Identidade nao pode ser lida ou quando a
    quantidade de cabecalhos do bloco nao bate com a de janelas da Rotina mestre:
    ali o pareamento por ordem viraria chute, e cabecalho errado mente sem dar
    erro - que e o pior tipo de erro.
    """
    if ler_rotina_mestre is None or cabecalho_janela is None:
        print(u"AVISO: nao consegui carregar o leitor da Rotina mestre. "
              u"Cabecalhos de janela intocados.")
        return 0
    try:
        janelas, _ = ler_rotina_mestre()
    except SystemExit as erro:
        print(u"AVISO: %s Cabecalhos de janela intocados." % erro)
        return 0

    cabecalhos = [k for k in range(ini, fim) if RX_JANELA.match(linhas[k])]
    if not cabecalhos:
        return 0
    if len(cabecalhos) != len(janelas):
        print(u"AVISO: o bloco tem %d cabecalho(s) de janela e a Rotina mestre declara %d. "
              u"Parear por ordem seria chute - cabecalhos intocados."
              % (len(cabecalhos), len(janelas)))
        return 0

    n = 0
    for k, j in zip(cabecalhos, janelas):
        novo = cabecalho_janela(j, acordar_min)
        if linhas[k].rstrip() == novo:
            continue
        print(u"  JANELA   %s" % linhas[k].strip())
        print(u"        -> %s" % novo.strip())
        linhas[k] = novo
        n += 1
    return n


def sem_acento(t):
    import unicodedata
    return u"".join(c for c in unicodedata.normalize("NFD", t)
                    if unicodedata.category(c) != "Mn").lower()


def em_minutos(txt):
    m = re.match(u"^(\\d{1,2})h(\\d{2})?$", txt)
    return int(m.group(1)) * 60 + int(m.group(2) or 0)


def duracao_em_minutos(linha):
    """Minutos declarados no parentese da tarefa, ou None se a linha nao declara."""
    m = RX_DUR.search(linha)
    if not m:
        return None
    if m.group("m") is not None:
        return int(m.group("m"))
    return int(m.group("h")) * 60 + int(m.group("hm") or 0)


# Usados so pelo modo --realinhar, que precisa dos DOIS lados do parentese
# (estimado E real), nao so o estimado que RX_DUR/duracao_em_minutos ja
# servem pros outros dois modos.
RX_QTD = re.compile(u"^(?:(?P<h>\\d{1,2})h(?P<hm>\\d{1,2})?m?|(?P<m>\\d{1,3})m)$")
RX_PARENTESE = re.compile(
    u"\\((?P<est>[^()\u2192]*?)\\s*(?:\u2192|->)\\s*(?P<real>[^()]*?)\\)")


def _minutos_de_qtd(txt):
    """Converte um token de duracao ('1h30', '45m', '1h') em minutos, ou None se vazio/invalido."""
    txt = (txt or u"").strip()
    if not txt:
        return None
    m = RX_QTD.match(txt)
    if not m:
        return None
    if m.group("m") is not None:
        return int(m.group("m"))
    return int(m.group("h")) * 60 + int(m.group("hm") or 0)


def duracoes(linha):
    """Retorna (estimado_min, real_min) declarados no parentese da tarefa.

    real_min e None quando a tarefa ainda nao declarou o valor real
    (`(15m -> )`) - inclusive quando ela ja esta marcada [x] mas o
    fundador ainda nao anotou quanto levou de verdade.
    """
    m = RX_PARENTESE.search(linha)
    if not m:
        return None, None
    return _minutos_de_qtd(m.group("est")), _minutos_de_qtd(m.group("real"))


def arredonda_5min(minutos):
    """Arredonda pro multiplo de 5 minutos mais proximo. Nao aplica modulo
    24h - isso e trabalho do texto_hora na hora de exibir/escrever."""
    return int(round(minutos / 5.0)) * 5


def texto_hora(minutos):
    """'05h' e '07h30', com zero a esquerda: e como ele escreve a mao,
    e e o que o montar_esqueleto_dia.py gera. Formato unico na mesma nota.
    """
    minutos %= 24 * 60
    h, m = divmod(minutos, 60)
    return u"%02dh%02d" % (h, m) if m else u"%02dh" % h


# A localizacao da semana (e o defeito de ordenar 'DD-MM-AA' como texto) mora
# agora em `cofre.semana_mais_recente`. Uma copia por ferramenta era exatamente
# o que fez o mesmo defeito aparecer em tres arquivos em 07/09/2026.


def localizar_bloco(a, alvo):
    """(caminho, linhas, ini, fim) do bloco do dia, ONDE ELE ESTIVER AGORA.

    Desde 07/09/2026 o bloco do dia nao mora mais sempre na nota da semana: de
    manha ele se muda pra autopsia do dia (`### Rotina e tarefas de hoje`) e so
    volta pra semana (`#### Segunda`) no fechamento. Assumir a semana aqui era
    o que amarrava a ferramenta ao modelo antigo - e o recalculo escreveria num
    bloco que ele nem esta olhando. Ver `cofre.py`.

    `--semana` continua mandando: e a saida manual pra mexer numa semana antiga.
    """
    caminho_semana = os.path.join(SEMANA, a.semana + ".md") if a.semana else None
    if caminho_semana and not os.path.isfile(caminho_semana):
        raise SystemExit(u"Nao achei %s" % caminho_semana)

    caminho = None
    if not caminho_semana:
        data = cofre.data_do_dia(alvo)
        if data is not None:
            caminho = cofre.bloco_do_dia(data)[0]
    if caminho is None:
        caminho = caminho_semana or cofre.semana_mais_recente()
    if not caminho or not os.path.isfile(caminho):
        raise SystemExit(u"Nao achei a nota que tem o bloco de %s" % alvo)

    linhas = io.open(caminho, encoding="utf-8").read().splitlines()
    nome = cofre.nome_da_secao_no_arquivo(caminho, cofre.data_do_dia(alvo) or dt.date.today())
    # `ini` e a linha do TITULO, nao a de baixo: e o contrato que os quatro modos
    # ja assumiam quando isso aqui era um `next(... == "#### " + alvo)`.
    ini = cofre.indice_do_titulo(linhas, nome)
    if ini is None:
        raise SystemExit(u"%s nao tem a secao '%s'" % (os.path.basename(caminho), nome))
    _, fim = cofre.limites_da_secao(linhas, nome)
    print(u"bloco em: %s > %s" % (os.path.basename(caminho), nome))
    return caminho, linhas, ini, fim


def reagendar_fechamento(caminho, alvo):
    """A cascata mudou, entao o fim do dia mudou: reescreve a tarefa do Windows.

    Silencioso de proposito quando falha - nao ter agendamento nao pode impedir
    o recalculo de gravar. O `criar_autopsia.py` da manha seguinte fecha o dia
    de qualquer jeito.
    """
    data = cofre.data_do_dia(alvo)
    if data is None:
        return
    try:
        import agendar_fechamento
        disparo, nota = agendar_fechamento.quando_fechar(data)
        if disparo is None:
            print(u"fechamento nao reagendado: %s" % nota)
            return
        codigo, _ = agendar_fechamento.agendar(disparo, data)
        print(u"fechamento reagendado pra %s%s" % (
            disparo.strftime("%d/%m as %H:%M"),
            u"" if codigo == 0 else u"  <-- FALHOU ao gravar a tarefa"))
    except Exception as erro:
        print(u"fechamento nao reagendado (%s)" % erro)


def eh_ancora(linhas, k, fim):
    """Bloco seguido de '> Hora marcada' nao desliza: o mundo nao remarca por ele."""
    return any(RX_MARCADA.match(linhas[x]) for x in range(k + 1, min(k + 8, fim))
               if not RX_TAREFA.match(linhas[x]))


def acha_ultima_concluida(linhas, ini, fim):
    """Indice da ULTIMA tarefa concluida do bloco que declara hora E duracao.

    E a ancora do modo --empurrar: o ponto ate onde o dia ja aconteceu de
    verdade. Item sem duracao declarada (oracao, alongamento) nao serve de
    ancora porque nao da pra saber a que horas ele terminou.
    """
    achado = None
    for k in range(ini, fim):
        if not RX_TAREFA.match(linhas[k]) or not RX_CONCLUIDA.match(linhas[k]):
            continue
        est, real = duracoes(linhas[k])
        if est is None and real is None:
            continue
        achado = k
    return achado


def grava(a, caminho, linhas, mudou):
    """Ponto UNICO de escrita da nota. Os quatro modos passam por aqui pra que
    'nao mudou nada' e '--dry-run' se comportem igual em todos eles."""
    if a.dry_run:
        print(u"SIMULACAO: nada foi escrito.")
        return 0
    if not mudou:
        print(u"Nada mudou - nota intocada.")
        return 0
    io.open(caminho, "w", encoding="utf-8", newline="\n").write(u"\n".join(linhas) + u"\n")
    print(u"Nota atualizada.")
    reagendar_fechamento(caminho, a.dia)
    return 0


def modo_apartir(a, caminho, linhas, ini, fim):
    """Empurra as tarefas NAO concluidas a partir do fim da tarefa em andamento.

    Desloca todas por um delta constante, de proposito: o espacamento entre elas
    foi escrito por ele e nao e nosso pra reescrever. Recascatear coladinho
    apagaria as folgas que ele deixou entre uma tarefa e outra.
    """
    if getattr(a, "empurrar", False):
        k_origem = acha_ultima_concluida(linhas, ini, fim)
        if k_origem is None:
            print(u"nota:    %s" % os.path.basename(caminho))
            print(u"Nenhuma tarefa concluida com hora e duracao no bloco de %s - "
                  u"nada pra empurrar." % a.dia)
            janelas = sincroniza_janelas(linhas, ini, fim, le_acordar(linhas, ini, fim, a.dia))
            return grava(a, caminho, linhas, janelas)
    else:
        procurado = sem_acento(a.apartir_de)
        k_origem = next((k for k in range(ini, fim)
                         if RX_TAREFA.match(linhas[k])
                         and procurado in sem_acento(RX_TAREFA.match(linhas[k]).group("ini"))), None)
        if k_origem is None:
            raise SystemExit(u"Nao achei tarefa com '%s' no bloco de %s. Confira o nome na nota."
                             % (a.apartir_de, a.dia))

    m = RX_TAREFA.match(linhas[k_origem])
    rotulo = m.group("ini").strip()
    # Duracao REAL quando a ancora ja esta concluida e ele preencheu o valor: e o
    # dado de verdade. Estimada so enquanto a real nao existe.
    est, real = duracoes(linhas[k_origem])
    dur = real if (real is not None and RX_CONCLUIDA.match(linhas[k_origem])) else est
    if dur is None:
        dur = duracao_em_minutos(linhas[k_origem])
    if dur is None:
        raise SystemExit(u"'%s' nao declara duracao entre parenteses - sem ela nao da pra "
                         u"saber a que horas ela acaba." % rotulo)

    if a.inicio:
        try:
            h, mi = (int(x) for x in a.inicio.split(":"))
        except ValueError:
            raise SystemExit(u"--inicio precisa ser HH:MM. Recebi: %s" % a.inicio)
        comeco = h * 60 + mi
    else:
        comeco = em_minutos(m.group("hora"))
    termina = comeco + dur

    print(u"nota:    %s" % os.path.basename(caminho))
    print(u"tarefa:  %s" % rotulo)
    print(u"janela:  %s + %s  ->  termina %s\n"
          % (texto_hora(comeco), texto_hora(dur), texto_hora(termina)))

    janelas = sincroniza_janelas(linhas, ini, fim, le_acordar(linhas, ini, fim, a.dia))

    if a.inicio:
        linhas[k_origem] = u"%s: %s%s" % (m.group("ini"), texto_hora(comeco), m.group("fim"))

    pendentes = [k for k in range(k_origem + 1, fim)
                 if RX_TAREFA.match(linhas[k]) and not RX_CONCLUIDA.match(linhas[k])]
    delta = 0 if not pendentes else (
        termina - em_minutos(RX_TAREFA.match(linhas[pendentes[0]]).group("hora")))

    mexidas, travadas = 0, 0
    if not pendentes:
        print(u"Nenhuma tarefa pendente depois dela. Nada a deslizar.")
    elif delta == 0:
        print(u"A proxima pendente ja comeca no fim desta. Nada a deslizar.")
    else:
        for k in pendentes:
            m2 = RX_TAREFA.match(linhas[k])
            antes = em_minutos(m2.group("hora"))
            if eh_ancora(linhas, k, fim):
                print(u"  TRAVADA  %-44s %s" % (m2.group("ini").strip()[:44], texto_hora(antes)))
                travadas += 1
                continue
            linhas[k] = u"%s: %s%s" % (m2.group("ini"), texto_hora(antes + delta), m2.group("fim"))
            print(u"  %-46s %s -> %s"
                  % (m2.group("ini").strip()[:46], texto_hora(antes), texto_hora(antes + delta)))
            mexidas += 1

        concluidas = sum(1 for k in range(k_origem + 1, fim)
                         if RX_TAREFA.match(linhas[k]) and RX_CONCLUIDA.match(linhas[k]))
        print(u"\ndelta: %s%s   |   %d deslizada(s), %d travada(s), %d ja concluida(s) intocada(s)."
              % (u"+" if delta >= 0 else u"-", texto_hora(abs(delta)),
                 mexidas, travadas, concluidas))

    print(u"%d cabecalho(s) de janela reconstruido(s)." % janelas)
    return grava(a, caminho, linhas, mexidas or janelas or bool(a.inicio))


def modo_realinhar(a, caminho, linhas, ini, fim):
    """Recalcula do zero o horario de TODAS as tarefas do dia, a partir do
    Acordar, andando na ordem em que aparecem na nota. Ver o docstring do
    modulo (secao TERCEIRO MODO) pra regra completa.
    """
    velho = le_acordar(linhas, ini, fim, a.dia)

    print(u"nota:    %s" % os.path.basename(caminho))
    print(u"dia:     %s" % a.dia)
    print(u"acordar: %s\n" % texto_hora(velho))

    # ANTES do laco, de proposito: a janela e a ancora do cursor, entao um
    # cabecalho fora da grade jogaria as tarefas todas pro horario errado.
    janelas = sincroniza_janelas(linhas, ini, fim, velho)

    cursor = velho
    mexidas, ancoradas, avisos = 0, 0, 0
    janela = None          # (nome, inicio, fim) da janela corrente
    for k in range(ini, fim):
        l = linhas[k]

        # A JANELA E A ANCORA. Ao cruzar um cabecalho, o cursor volta pro
        # inicio dela: atraso de uma janela nao contamina a seguinte.
        mj = RX_JANELA.match(l)
        if mj:
            if janela and cursor > janela[2]:
                print(u"  ESTOUROU %-44s passou %dmin do fim da janela"
                      % (janela[0][:44], cursor - janela[2]))
                avisos += 1
            de = em_minutos(mj.group("de"))
            ate = em_minutos(mj.group("ate"))
            if ate <= de:
                ate += 24 * 60
            janela = (l.strip().lstrip(u"#").strip(), de, ate)
            cursor = de
            continue

        m = RX_TAREFA.match(l)
        if not m:
            continue

        antes = em_minutos(m.group("hora"))
        est, real = duracoes(l)
        concluida = bool(RX_CONCLUIDA.match(l))
        dur = real if (concluida and real is not None) else est

        if dur is None:
            print(u"  AVISO    %-44s sem duracao declarada, horario mantido em %s"
                  % (m.group("ini").strip()[:44], texto_hora(antes)))
            avisos += 1
            cursor = antes
            continue
        if concluida and real is None and est is not None:
            print(u"  AVISO    %-44s concluida sem 'real' preenchido, usando estimado (%s)"
                  % (m.group("ini").strip()[:44], texto_hora(est)))
            avisos += 1

        if eh_ancora(linhas, k, fim):
            print(u"  ANCORA   %-44s %s (fixo)" % (m.group("ini").strip()[:44], texto_hora(antes)))
            ancoradas += 1
            cursor = antes + dur
            continue

        novo_bruto = arredonda_5min(cursor)
        novo = novo_bruto % (24 * 60)
        if novo != antes:
            linhas[k] = u"%s: %s%s" % (m.group("ini"), texto_hora(novo_bruto), m.group("fim"))
            print(u"  %-46s %s -> %s" % (m.group("ini").strip()[:46], texto_hora(antes), texto_hora(novo)))
            mexidas += 1
        else:
            print(u"  %-46s %s (sem mudanca)" % (m.group("ini").strip()[:46], texto_hora(antes)))
        cursor = novo_bruto + dur

    if janela and cursor > janela[2]:
        print(u"  ESTOUROU %-44s passou %dmin do fim da janela"
              % (janela[0][:44], cursor - janela[2]))
        avisos += 1
    print(u"\n%d tarefa(s) realinhada(s), %d ancora(s) preservada(s), "
          u"%d cabecalho(s) de janela reconstruido(s), %d aviso(s)."
          % (mexidas, ancoradas, janelas, avisos))
    return grava(a, caminho, linhas, mexidas or janelas)


def modo_pelo_acordar(a, caminho, linhas, ini, fim):
    """Recalcula o dia usando o '> Acordar:' que ja esta escrito na nota.

    Ele edita SO aquela linha e roda; nao precisa repetir a hora no comando.
    A ancora velha nao esta escrita em lugar nenhum, entao e deduzida da
    PRIMEIRA tarefa do bloco, que por desenho fica no offset zero do acordar.
    """
    acordar = le_acordar(linhas, ini, fim, a.dia)

    primeira = next((RX_TAREFA.match(linhas[k]) for k in range(ini, fim)
                     if RX_TAREFA.match(linhas[k])), None)
    if primeira is None:
        raise SystemExit(u"O bloco de %s nao tem nenhuma tarefa pra ancorar." % a.dia)
    base = em_minutos(primeira.group("hora"))
    delta = acordar - base

    print(u"nota:    %s" % os.path.basename(caminho))
    print(u"dia:     %s" % a.dia)
    print(u"acordar: %s   (1a tarefa estava em %s, delta %s%dmin)\n"
          % (texto_hora(acordar), texto_hora(base), u"+" if delta >= 0 else u"", delta))

    janelas = sincroniza_janelas(linhas, ini, fim, acordar)

    mexidas, travadas = 0, 0
    if delta == 0:
        print(u"Tarefas ja ancoradas no acordar escrito - nenhuma deslizada.")
    else:
        for k in range(ini, fim):
            m = RX_TAREFA.match(linhas[k])
            if not m:
                continue
            antes = em_minutos(m.group("hora"))
            if eh_ancora(linhas, k, fim):
                print(u"  TRAVADA  %-44s %s" % (m.group("ini").strip()[:44], texto_hora(antes)))
                travadas += 1
                continue
            linhas[k] = u"%s: %s%s" % (m.group("ini"), texto_hora(antes + delta), m.group("fim"))
            print(u"  %-46s %s -> %s" % (m.group("ini").strip()[:46],
                                         texto_hora(antes), texto_hora(antes + delta)))
            mexidas += 1

    print(u"\n%d tarefa(s) deslizada(s), %d travada(s), %d cabecalho(s) de janela reconstruido(s)."
          % (mexidas, travadas, janelas))
    return grava(a, caminho, linhas, mexidas or janelas)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dia", required=True, help=u"Segunda, Terca, Quarta...")
    ap.add_argument("--acordar", help="HH:MM - a hora REAL que ele acordou")
    ap.add_argument("--pelo-acordar", dest="pelo_acordar", action="store_true",
                    help=u"le o '> Acordar:' ja escrito na nota e recalcula o dia por ele")
    ap.add_argument("--apartir-de", dest="apartir_de",
                    help=u"nome (ou pedaco do nome) da tarefa em andamento")
    ap.add_argument("--empurrar", action="store_true",
                    help=u"como --apartir-de, mas achando sozinho a ultima tarefa concluida. "
                         u"E o modo que o vigia_rotina.py usa")
    ap.add_argument("--inicio", help=u"HH:MM - inicio REAL dessa tarefa; padrao e a hora ja escrita nela")
    ap.add_argument("--realinhar", action="store_true",
                    help=u"recalcula todos os horarios do dia por duracao real (concluida) ou "
                         u"estimada (pendente), arredondado pro multiplo de 5min mais proximo")
    ap.add_argument("--semana", help=u"nome da nota; padrao e a mais recente")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    if sum([bool(a.acordar), bool(a.apartir_de), bool(a.realinhar),
            bool(a.pelo_acordar), bool(a.empurrar)]) != 1:
        raise SystemExit(u"Escolha UM modo: --acordar HH:MM, --pelo-acordar, "
                         u"--apartir-de \"Nome da tarefa\", --empurrar ou --realinhar.")
    if a.inicio and not a.apartir_de:
        raise SystemExit(u"--inicio so faz sentido junto de --apartir-de.")

    alvo = next((d for d in DIAS if sem_acento(d) == sem_acento(a.dia)), None)
    if not alvo:
        raise SystemExit(u"Dia invalido: %s. Use um de %s" % (a.dia, u", ".join(DIAS)))

    caminho, linhas, ini, fim = localizar_bloco(a, alvo)

    if a.apartir_de or a.empurrar:
        return modo_apartir(a, caminho, linhas, ini, fim)
    if a.realinhar:
        return modo_realinhar(a, caminho, linhas, ini, fim)
    if a.pelo_acordar:
        return modo_pelo_acordar(a, caminho, linhas, ini, fim)

    velho = le_acordar(linhas, ini, fim, alvo)

    try:
        h, mi = (int(x) for x in a.acordar.split(":"))
    except ValueError:
        raise SystemExit(u"--acordar precisa ser HH:MM. Recebi: %s" % a.acordar)
    novo = h * 60 + mi
    delta = novo - velho

    print(u"nota:    %s" % os.path.basename(caminho))
    print(u"dia:     %s" % alvo)
    print(u"acordar: %s -> %s   (%s%dmin)\n" % (
        texto_hora(velho), texto_hora(novo), u"+" if delta >= 0 else u"", delta))

    mexidas, travadas = 0, 0
    if delta == 0:
        print(u"Acordou no horario da meta - nenhuma tarefa deslizada.")
    else:
        for k in range(ini, fim):
            l = linhas[k]
            if RX_ACORDAR.match(l.strip()):
                linhas[k] = re.sub(u"Acordar:\\s*\\d{1,2}h(?:\\d{2})?",
                                   u"Acordar: %s" % texto_hora(novo), l)
                continue
            m = RX_TAREFA.match(l)
            if not m:
                continue
            antes = em_minutos(m.group("hora"))
            if eh_ancora(linhas, k, fim):
                print(u"  TRAVADA  %-44s %s" % (m.group("ini").strip()[:44], texto_hora(antes)))
                travadas += 1
                continue
            depois = antes + delta
            linhas[k] = u"%s: %s%s" % (m.group("ini"), texto_hora(depois), m.group("fim"))
            print(u"  %-46s %s -> %s"
                  % (m.group("ini").strip()[:46], texto_hora(antes), texto_hora(depois)))
            mexidas += 1

    # Depois do laco: os cabecalhos derivam do acordar NOVO, ja escrito acima.
    janelas = sincroniza_janelas(linhas, ini, fim, novo)
    print(u"\n%d tarefa(s) deslizada(s), %d travada(s) por hora marcada, "
          u"%d cabecalho(s) de janela reconstruido(s)." % (mexidas, travadas, janelas))
    return grava(a, caminho, linhas, mexidas or janelas or delta != 0)


if __name__ == "__main__":
    sys.exit(main())
