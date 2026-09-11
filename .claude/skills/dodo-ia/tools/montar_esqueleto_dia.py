# -*- coding: utf-8 -*-
"""Monta o esqueleto de um dia da nota da Semana a partir da Rotina mestre.

Ate 29/08/2026 o bloco de cada dia (`#### <Dia>`) era digitado a mao toda
semana. Em 30/08/2026 a rotina virou dado estruturado em
`Identidade.md > Habitos > Rotina mestre (com horario)` (ver
`Tarefas/Agosto/Rotina Mestre - Rascunho 28-08-26.md` pro desenho completo) -
este script le esse dado e gera o esqueleto do dia, no MESMO formato que
`recalcular_dia.py` sabe reler depois (`- [ ] Nome (dur -> ): HORA #area`).

O QUE E AUTOMATICO: os itens "Todo dia" das 7 janelas biologicas, com horario
calculado como offset puro a partir do `--acordar`.

ITEM SEM DURACAO NAO GANHA HORA (02/09/2026). Ele sai como `- [ ] Nome #area`,
sem `(dur -> ): HORA`, e nao move o cursor. Sao os itens que, na palavra dele,
"realmente nao existem tempo definido e nem horario fixo pra serem feitas":
oracao, poder do agora, olhar a vista, alongamento. Antes cada um ganhava 5m e
um horario inventados, o que somava tempo fantasma e enchia a janela de
compromisso inexistente. Como o `recalcular_dia.py` acha tarefa pelo `: HORA`,
esses itens ficam de fora dos recalculos - que e o certo.

FORMATO (02/09/2026): o bloco sai AGRUPADO PELAS JANELAS, nao como lista
corrida. Cada janela vira um cabecalho de nivel 5 com a faixa ja convertida
pra hora de relogio, o nome da janela e o foco declarado:

    ##### 07h-11h (Janela de Ouro) - Foco: Espiritual, Fisico, Financeiro

Pedido do fundador: ele le o dia pela janela em que esta, nao pela posicao do
item na lista. O cabecalho e nivel 5 de proposito - `criar_autopsia.py` e
`recalcular_dia.py` delimitam o bloco do dia por `#### ` e `### `, e `##### `
nao casa com nenhum dos dois, entao o embed e o recalculo seguem inteiros.

O QUE NAO E: os itens "Por dia da semana" (grupo muscular do treino, blocos
extras de sabado/domingo, etc). Esse texto e bem menos estruturado - tentar
parsear e encaixar sozinho arrisca botar um compromisso com hora marcada no
lugar errado. O script imprime esse texto como lembrete pro fundador ajustar
a mao, igual o `sincronizar_areas.py` lista "SEM PAR" em vez de adivinhar.

NAO SOBRESCREVE um bloco '#### <Dia>' que ja existe na nota - so cria quando
o dia ainda nao tem bloco, a nao ser que `--forcar` seja passado.

Uso:
  python montar_esqueleto_dia.py --dia Segunda --acordar 05:40 --dry-run
  python montar_esqueleto_dia.py --dia Segunda --acordar 05:40 \
      --meta-operacional "Loja: fechar os ajustes" \
      --meta-operacional "Consultoria: subir no dominio" \
      --meta-pessoal "Dormir cedo"
  python montar_esqueleto_dia.py --dia Segunda --acordar 05:40 --semana "Semana 07-09-26" --forcar
"""
import io
import os
import re
import sys
import codecs
import argparse
import datetime as dt

import cofre

if sys.platform == "win32":
    try:
        sys.stdout = codecs.getwriter("utf-8")(sys.stdout.buffer, "replace")
    except AttributeError:
        pass

# tools/ -> dodo-ia/ -> skills/ -> .agents (ou .claude)/ -> raiz do workspace
RAIZ = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", ".."))
VAULT = os.path.join(RAIZ, "Vault")
IDENTIDADE = os.path.join(VAULT, "Vida Pessoal", "Identidade.md")
SEMANA_DIR = os.path.join(VAULT, "Vida Pessoal", "Semana")

DIAS = (u"Segunda", u"Ter\u00e7a", u"Quarta", u"Quinta", u"Sexta", u"S\u00e1bado", u"Domingo")

CAB_ROTINA_MESTRE = u"#### Rotina mestre (com hor\u00e1rio)"
CAB_PRINCIPIOS = u"#### Princ\u00edpios de conduta"
CAB_POR_DIA = u"Por dia da semana"

RX_JANELA = re.compile(
    u"^Todo dia - Hora ([^(]+?)\\s*\\(([^)]+)\\)(?:\\s*-\\s*Foco:\\s*([^:]*))?:\\s*$")
RX_ITEM = re.compile(u"^-\\s+(.+)$")
RX_HORA_TOKEN = re.compile(u"^(\\d{1,2})h?(\\d{2})?$")
RX_DUR_H = re.compile(u"^~?(\\d{1,3})h(\\d{1,2})?m?$")
RX_DUR_M = re.compile(u"^~?(\\d{1,3})m$")
# Formato novo da Identidade (07/09/2026): '- Nome (5m) #espiritual'.
RX_TAG_FINAL = re.compile(u"\\s+#([^\\s#]+)\\s*$")
RX_PARENTESE_FINAL = re.compile(u"\\s*\\(([^()]*)\\)\\s*$")
# 'Semana 07-09-26.md' - a data e a identidade da nota, o titulo deriva.
RX_DATA_SEMANA = re.compile(u"Semana\\s+(\\d{2})-(\\d{2})-(\\d{2})")
# Lidos de VOLTA da nota da semana, pelo modo --janela.
RX_JANELA_NOTA = re.compile(
    u"^\\s*#{5}\\s+\\d{1,2}h(?:\\d{2})?(?:-\\d{1,2}h(?:\\d{2})?)?\\s*\\(([^)]+)\\)")
RX_ACORDAR_NOTA = re.compile(u"^>\\s*Acordar:\\s*(\\d{1,2})h(\\d{2})?", re.IGNORECASE)
RX_TAREFA_NOTA = re.compile(u"^-\\s*\\[[ xX]\\]")


def hora_token_em_min(tok):
    m = RX_HORA_TOKEN.match(tok.strip())
    if not m:
        return None
    return int(m.group(1)) * 60 + int(m.group(2) or 0)


def duracao_em_min(txt):
    primeiro = (txt.split() or [u""])[0].rstrip(u".,;")
    m = RX_DUR_M.match(primeiro)
    if m:
        return int(m.group(1))
    m = RX_DUR_H.match(primeiro)
    if m:
        return int(m.group(1)) * 60 + int(m.group(2) or 0)
    return None


def fmt_dur(minutos):
    h, m = divmod(minutos, 60)
    if h and m:
        return u"%dh%d" % (h, m)
    if h:
        return u"%dh" % h
    return u"%dm" % m


def fmt_hora(minutos):
    """'05h' e '07h50', com zero a esquerda: e como ele escreve a mao."""
    minutos %= 24 * 60
    h, m = divmod(minutos, 60)
    return u"%02dh%02d" % (h, m) if m else u"%02dh" % h


def split_respeitando_parenteses(txt, sep=u" - "):
    """Como str.split(sep), mas nunca quebra um separador que esta dentro de
    parenteses - 'Ambiente (2a rodada - lixo) - 6m' vira 2 partes, nao 3."""
    partes, atual, profundidade, i, n = [], [], 0, 0, len(txt)
    while i < n:
        if txt[i] == u"(":
            profundidade += 1
        elif txt[i] == u")":
            profundidade = max(0, profundidade - 1)
        if profundidade == 0 and txt[i:i + len(sep)] == sep:
            partes.append(u"".join(atual))
            atual = []
            i += len(sep)
            continue
        atual.append(txt[i])
        i += 1
    partes.append(u"".join(atual))
    return partes


def solta_tag_final(p):
    """('texto sem a tag', 'area'_ou_None) pra 'Poder do agora #espiritual'.

    So a tag GRUDADA no fim conta. Tag no meio de um comentario
    ('#fisico (grupo muscular varia por dia)') ja e tratada pelo ramo que testa
    `p.startswith('#')`, e nao pode ser arrancada daqui.
    """
    m = RX_TAG_FINAL.search(p)
    if not m:
        return p, None
    return p[:m.start()].strip(), m.group(1)


def solta_duracao_final(p):
    """('texto sem a duracao', minutos_ou_None) pra 'Auto Cuidado (higiene) (15m)'.

    Aceita apenas parentese final cujo conteudo e SO um token de duracao. Isso e
    o que separa '(15m)' de '(higiene, cuidado de pele)' e de '(2a rodada - lixo)':
    conteudo com espaco ou virgula e nome, nao duracao, e continua no titulo.
    """
    m = RX_PARENTESE_FINAL.search(p)
    if not m:
        return p, None
    dentro = m.group(1).strip()
    if u" " in dentro or u"," in dentro:
        return p, None
    d = duracao_em_min(dentro)
    if d is None:
        return p, None
    return p[:m.start()].strip(), d


def parse_item(resto):
    """('nome', duracao_min_ou_None, 'area'_ou_None) a partir do texto apos o '- '.

    O nome e TUDO que nao e duracao e nao e tag de area, remontado com o mesmo
    ' - ' que separava. Pegar so a primeira parte apagava o qualificador que
    distingue duas tarefas irmas: 'Gerir ativos - parte logica' e 'Gerir ativos
    - parte criativa' viravam as duas 'Gerir ativos', e o dia ficava com dois
    itens de nome identico que o recalcular_dia.py nao consegue diferenciar.

    DOIS FORMATOS convivem na Identidade, e os dois valem (07/09/2026):

        - Treino fisico - 1h30 - #fisico          (campos separados por ' - ')
        - Reprogramacao mental ao acordar (5m) #espiritual   (parentese + tag colada)

    O segundo entrou quando ele reescreveu a Inercia e a Janela de Ouro. O parser
    so conhecia o primeiro e devolvia o item INTEIRO como nome, com duracao e area
    None - o dia saia sem hora e sem tag, sem erro nenhum. Por isso os dois sao
    tratados aqui, por parte, e nao por deteccao de formato do bloco todo: o
    arquivo esta metade em cada um.
    """
    partes = [p.strip() for p in split_respeitando_parenteses(resto)]
    nome_partes = []
    duracao = None
    area = None
    for p in partes:
        if p.startswith(u"#"):
            area = area or (p[1:].split()[0] if p[1:].split() else None)
            continue
        p, tag = solta_tag_final(p)
        if tag and area is None:
            area = tag
        p, dur_parentese = solta_duracao_final(p)
        if dur_parentese is not None and duracao is None:
            duracao = dur_parentese
        if not p:
            continue
        d = duracao_em_min(p)
        if d is not None:
            if duracao is None:
                duracao = d
            continue
        nome_partes.append(p)
    return u" - ".join(nome_partes), duracao, area


def ler_rotina_mestre():
    """[{offset, offset_fim, nome, foco, itens: [(nome, duracao_ou_None, area_ou_None)]}],
    {dia: texto_cru} do bloco 'Por dia da semana'."""
    if not os.path.isfile(IDENTIDADE):
        raise SystemExit(u"Nao achei %s" % IDENTIDADE)
    with io.open(IDENTIDADE, encoding="utf-8", errors="replace") as fh:
        linhas = fh.read().splitlines()

    try:
        ini = next(i for i, l in enumerate(linhas) if l.strip() == CAB_ROTINA_MESTRE)
    except StopIteration:
        raise SystemExit(u"Identidade.md nao tem a secao '%s' - rode a reestruturacao antes."
                         % CAB_ROTINA_MESTRE)
    fim = next((i for i, l in enumerate(linhas) if i > ini and l.strip() == CAB_PRINCIPIOS),
               len(linhas))

    janelas = []
    por_dia_bruto = []
    em_por_dia = False
    janela_atual = None
    for l in linhas[ini + 1:fim]:
        # Tolera a janela escrita como cabecalho ('##### Todo dia - Hora ...')
        # ou como linha crua ('Todo dia - Hora ...'). Ele promoveu as janelas a
        # heading em 02/09/2026 e o parser antigo passou a nao achar nenhuma,
        # abortando o script inteiro. O nivel do heading nao e dado: e formatacao.
        s = l.strip().lstrip(u"#").strip()
        if not s:
            continue
        if s.startswith(u">"):
            continue
        if sem_acento(s).startswith(sem_acento(CAB_POR_DIA)):
            em_por_dia = True
            janela_atual = None
            continue
        if s.lower().startswith(u"fora da rotina mestre"):
            em_por_dia = False
            janela_atual = None
            continue
        if em_por_dia:
            por_dia_bruto.append(l)
            continue

        mj = RX_JANELA.match(s)
        if mj:
            faixa, nome_janela, foco = mj.groups()
            a, _, b = faixa.partition(u"-")
            offset = hora_token_em_min(a)
            if offset is None:
                print(u"AVISO: nao entendi o offset de '%s' - janela ignorada." % s)
                janela_atual = None
                continue
            janela_atual = {"offset": offset, "offset_fim": hora_token_em_min(b),
                            "nome": nome_janela.strip(),
                            "foco": (foco or u"").strip(), "itens": []}
            janelas.append(janela_atual)
            continue

        mi = RX_ITEM.match(s)
        if mi and janela_atual is not None:
            nome, duracao, area = parse_item(mi.group(1))
            janela_atual["itens"].append((nome, duracao, area))

    janelas.sort(key=lambda j: j["offset"])
    return janelas, u"\n".join(por_dia_bruto)


def sem_acento(t):
    import unicodedata
    return u"".join(c for c in unicodedata.normalize("NFD", t) if unicodedata.category(c) != "Mn").lower()


def cabecalho_janela(j, acordar_min):
    """'##### 07h-11h (Janela de Ouro) - Foco: ...' pra uma janela.

    A faixa sai em hora de relogio, contada a partir do acordar: e assim que
    ele le o dia. Janela sem fim declarado em Identidade.md sai so com o
    comeco, em vez de inventar uma hora que ninguem escreveu.
    """
    ini = fmt_hora(acordar_min + j["offset"])
    faixa = ini if j.get("offset_fim") is None else (
        u"%s-%s" % (ini, fmt_hora(acordar_min + j["offset_fim"])))
    cab = u"##### %s (%s)" % (faixa, j["nome"])
    if j["foco"]:
        cab += u" - Foco: %s" % j["foco"]
    return cab


def montar_bloco(janelas, acordar_min, dia, operacional=None, pessoal=None):
    # Cabecalho no formato que ele fixou em 02/09/2026: a meta operacional e
    # uma LISTA, com um sub-item por operacao que o dia toca; a meta pessoal e
    # uma linha so. O 'Acordar' fica isolado embaixo.
    linhas = [u"#### %s" % dia]
    linhas.append(u"- Meta operacional:")
    # `==preencher==` e nao `<preencher>`: o Obsidian le `<preencher>` como
    # abertura de tag HTML que nunca fecha e engole o RESTO da secao como
    # conteudo dela - a rotina inteira aparece como texto puro, sem checkbox e
    # sem cabecalho de janela, e sem nenhum erro. Mordeu em 07/09/2026, quando o
    # bloco do dia passou a viver dentro da autopsia. `==...==` e destaque
    # nativo do Obsidian: fica igualmente visivel e nao e HTML.
    for item in (operacional or [u"==preencher=="]):
        linhas.append(u"\t- %s" % item)
    linhas.append(u"")
    linhas.append(u"- Meta pessoal: %s" % (pessoal or u"==preencher=="))
    linhas.append(u"")
    linhas.append(u"> Acordar: %s" % fmt_hora(acordar_min))
    linhas.append(u"")

    sem_duracao, sem_area = [], []
    cursor = acordar_min
    for j in janelas:
        base = acordar_min + j["offset"]
        cursor = max(cursor, base)
        linhas.append(cabecalho_janela(j, acordar_min))
        linhas.append(u"")
        for nome, duracao, area in j["itens"]:
            if area is None:
                sem_area.append(nome)
            tag = u" #%s" % area if area else u""
            if duracao is None:
                # Sem tempo definido e sem horario fixo: entra na janela, mas
                # nao ocupa slot nem move o cursor. Inventar 5m aqui enchia o
                # dia de compromisso que nao existe.
                sem_duracao.append(nome)
                linhas.append(u"- [ ] %s%s" % (nome, tag))
                continue
            linhas.append(u"- [ ] %s (%s \u2192 ): %s%s"
                          % (nome, fmt_dur(duracao), fmt_hora(cursor), tag))
            cursor += duracao
        # Tarefas coladas dentro da janela; o branco so cerca o cabecalho.
        linhas.append(u"")

    while linhas and not linhas[-1].strip():
        linhas.pop()
    return u"\n".join(linhas), sem_duracao, sem_area


def linhas_da_janela(j, acordar_min):
    """Cabecalho + itens de UMA janela, no formato da nota.

    O cursor nasce no inicio da propria janela, nao no fim da anterior: aqui
    esta se regerando uma janela isolada, e as horas das outras ja estao
    escritas na nota (muitas vezes com o tempo REAL do dia). Herdar cursor de
    fora empurraria horario que o fundador ja mediu.
    """
    linhas = [cabecalho_janela(j, acordar_min), u""]
    cursor = acordar_min + j["offset"]
    for nome, duracao, area in j["itens"]:
        tag = u" #%s" % area if area else u""
        if duracao is None:
            linhas.append(u"- [ ] %s%s" % (nome, tag))
            continue
        linhas.append(u"- [ ] %s (%s → ): %s%s"
                      % (nome, fmt_dur(duracao), fmt_hora(cursor), tag))
        cursor += duracao
    return linhas


def regenera_janela(linhas, ini, fim, janelas, nome_alvo, forcar):
    """Troca UMA janela do bloco do dia pela versao vigente da Rotina mestre.

    Existe porque editar a Rotina mestre no meio da semana deixa os dias JA
    escritos em silencio na ordem velha (aconteceu em 07/09/2026: ele reordenou
    a Inercia e so a segunda foi corrigida a mao). Regerar o dia inteiro nao
    servia: apagaria o alvo da operacao, o grupo muscular do treino, os links de
    Ativos e os blocos com hora marcada que ele escreveu item a item.

    Devolve a quantidade de linhas escritas, ou None quando abortou.
    """
    acordar = None
    for l in linhas[ini:fim]:
        m = RX_ACORDAR_NOTA.match(l.strip())
        if m:
            acordar = int(m.group(1)) * 60 + int(m.group(2) or 0)
            break
    if acordar is None:
        raise SystemExit(u"O bloco do dia nao tem a linha '> Acordar: HHhMM'.")

    alvo = next((j for j in janelas if sem_acento(nome_alvo) in sem_acento(j["nome"])), None)
    if alvo is None:
        raise SystemExit(u"Nao achei a janela '%s' na Rotina mestre. Existem: %s"
                         % (nome_alvo, u", ".join(j["nome"] for j in janelas)))

    k_cab = None
    for k in range(ini, fim):
        m = RX_JANELA_NOTA.match(linhas[k])
        if m and sem_acento(nome_alvo) in sem_acento(m.group(1)):
            k_cab = k
            break
    if k_cab is None:
        raise SystemExit(u"O bloco do dia nao tem cabecalho da janela '%s'." % nome_alvo)

    k_fim = next((k for k in range(k_cab + 1, fim) if RX_JANELA_NOTA.match(linhas[k])), fim)

    # Tudo que nao for tarefa de topo seria apagado pela troca: sub-item com o
    # alvo da operacao, link de Ativos, linha '> Hora marcada'. Nao apago isso em
    # silencio - listo e paro, porque e texto que ele escreveu a mao.
    estranhas = []
    for k in range(k_cab + 1, k_fim):
        bruta = linhas[k]
        if not bruta.strip():
            continue
        if bruta[:1] in (u"\t", u" ") or not RX_TAREFA_NOTA.match(bruta):
            estranhas.append(bruta)
    if estranhas and not forcar:
        print(u"ABORTADO: a janela '%s' tem %d linha(s) escritas a mao que a troca "
              u"apagaria. Rode com --forcar se for pra perder:" % (alvo["nome"], len(estranhas)))
        for l in estranhas:
            print(u"  %s" % l.rstrip())
        return None

    novas = linhas_da_janela(alvo, acordar)
    linhas[k_cab:k_fim] = novas + [u""]
    for l in novas:
        print(u"  %s" % l)
    return len(novas)


def onde_esta_o_bloco(a, alvo):
    """(caminho, nome da secao) do bloco do dia AGORA - autopsia ou semana.

    Ate 07/09/2026 o bloco morava sempre na nota da semana. Hoje ele se muda pra
    autopsia durante o dia (ver `cofre.py`), e regenerar uma janela lendo a
    semana escreveria num bloco que ele nem tem aberto - sem erro nenhum.
    `--semana` continua mandando, pra mexer numa semana antiga de proposito.
    """
    if a.semana:
        return os.path.join(SEMANA_DIR, a.semana + u".md"), alvo
    data = cofre.data_do_dia(alvo)
    caminho = cofre.bloco_do_dia(data)[0] if data else None
    if caminho:
        return caminho, cofre.nome_da_secao_no_arquivo(caminho, data)
    return semana_mais_recente_caminho(), alvo


def executa_modo_janela(a, alvo, janelas):
    """Regenera UMA janela de um dia que ja existe, esteja ele onde estiver."""
    caminho, nome_secao = onde_esta_o_bloco(a, alvo)
    if not os.path.isfile(caminho):
        raise SystemExit(u"Nao achei a nota: %s" % caminho)

    linhas = io.open(caminho, encoding="utf-8").read().splitlines()
    ini = cofre.indice_do_titulo(linhas, nome_secao)
    if ini is None:
        raise SystemExit(u"'%s' nao tem a secao '%s'. Gere o dia inteiro antes "
                         u"(sem --janela)." % (os.path.basename(caminho), nome_secao))
    _, fim = cofre.limites_da_secao(linhas, nome_secao)

    print(u"nota:    %s > %s" % (os.path.basename(caminho), nome_secao))
    print(u"dia:     %s" % alvo)
    print(u"janela:  %s\n" % a.janela)

    antes = list(linhas)
    if regenera_janela(linhas, ini, fim, janelas, a.janela, a.forcar) is None:
        return 1

    if a.dry_run:
        print(u"\nSIMULACAO: nada foi escrito.")
        return 0
    if linhas == antes:
        print(u"\nA janela ja estava igual a Rotina mestre - nota intocada.")
        return 0
    io.open(caminho, "w", encoding="utf-8", newline="\n").write(u"\n".join(linhas) + u"\n")
    print(u"\nNota atualizada: %s" % caminho)
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dia", required=True, help=u"Segunda, Terca, Quarta...")
    ap.add_argument("--acordar", help=u"HH:MM - obrigatorio ao gerar o dia inteiro; "
                                      u"no modo --janela o acordar vem da propria nota")
    ap.add_argument("--janela", metavar=u"NOME",
                    help=u"regenera SO essa janela de um dia que ja existe na nota "
                         u"(ex: --janela Inercia), preservando o resto do bloco")
    ap.add_argument("--meta-operacional", action="append", default=None,
                    metavar=u"OP: o que a operacao persegue hoje",
                    help=u"repita a opcao pra cada operacao que o dia toca")
    ap.add_argument("--meta-pessoal", default=None,
                    help=u"o que ele persegue nesse dia, fora da operacao")
    ap.add_argument("--semana", help=u"nome da nota da semana; padrao e a mais recente")
    ap.add_argument("--forcar", action="store_true",
                    help=u"sobrescreve o bloco '#### <Dia>' mesmo se ja existir")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    alvo = next((d for d in DIAS if sem_acento(d) == sem_acento(a.dia)), None)
    if not alvo:
        raise SystemExit(u"Dia invalido: %s. Use um de %s" % (a.dia, u", ".join(DIAS)))

    janelas, por_dia_bruto = ler_rotina_mestre()
    if not janelas:
        raise SystemExit(u"Nao achei nenhuma janela 'Todo dia - Hora X-Y' em Identidade.md.")

    if a.janela:
        return executa_modo_janela(a, alvo, janelas)

    if not a.acordar:
        raise SystemExit(u"--acordar HH:MM e obrigatorio pra gerar o dia inteiro.")
    try:
        h, mi = (int(x) for x in a.acordar.split(":"))
    except ValueError:
        raise SystemExit(u"--acordar precisa ser HH:MM. Recebi: %s" % a.acordar)
    acordar_min = h * 60 + mi

    bloco, sem_duracao, sem_area = montar_bloco(
        janelas, acordar_min, alvo, a.meta_operacional, a.meta_pessoal)

    print(u"dia:     %s" % alvo)
    print(u"acordar: %s" % fmt_hora(acordar_min))
    print(u"janelas: %d, %d itens ao todo\n" % (len(janelas), sum(len(j["itens"]) for j in janelas)))

    if sem_duracao:
        print(u"%d item(ns) sem duracao em Identidade.md - sairam sem hora, dentro da "
              u"janela deles (por decisao dele em 02/09/2026):" % len(sem_duracao))
        for n in sem_duracao:
            print(u"  - %s" % n)
        print(u"")
    if sem_area:
        print(u"AVISO: %d item(ns) sem #area em Identidade.md - saiu sem tag, adicione a mao:"
              % len(sem_area))
        for n in sem_area:
            print(u"  - %s" % n)
        print(u"")

    print(u"-" * 60)
    print(bloco)
    print(u"-" * 60)

    if por_dia_bruto.strip():
        print(u"")
        print(u"LEMBRETE - 'Por dia da semana' em Identidade.md (nao auto-aplicado, ajuste a mao):")
        print(por_dia_bruto)

    if a.dry_run:
        print(u"")
        print(u"SIMULACAO: nada foi escrito.")
        return 0

    caminho, nome_secao = onde_esta_o_bloco(a, alvo)
    if not os.path.isfile(caminho):
        raise SystemExit(u"Nao achei a nota: %s" % caminho)

    linhas_nota = io.open(caminho, encoding="utf-8").read().splitlines()
    ini = cofre.indice_do_titulo(linhas_nota, nome_secao)
    # Na autopsia o titulo da secao ('### Rotina e tarefas de hoje:') ja existe
    # e e fixo. Levar o '#### <Dia>' pra dentro dela criaria uma fronteira de
    # secao no meio da propria rotina, e o resto do bloco cairia pra fora dela.
    na_autopsia = cofre.normalizar(nome_secao) != cofre.normalizar(alvo)
    corpo = bloco.splitlines()[1:] if na_autopsia else bloco.splitlines()

    if na_autopsia:
        if ini is None:
            raise SystemExit(u"'%s' nao tem a secao '%s'."
                             % (os.path.basename(caminho), nome_secao))
        if not a.forcar:
            raise SystemExit(
                u"O dia %s esta aberto em '%s' - regerar apagaria o que voce ja "
                u"marcou hoje. Use --forcar se e isso mesmo."
                % (alvo, os.path.basename(caminho)))
        linhas_nota = cofre.substituir_secao(linhas_nota, nome_secao, corpo)
    elif ini is not None:
        if not a.forcar:
            raise SystemExit(
                u"'%s' ja tem um bloco '#### %s' - nao sobrescrevo sem --forcar."
                % (caminho, alvo))
        _, fim = cofre.limites_da_secao(linhas_nota, nome_secao)
        linhas_nota[ini:fim] = corpo + [u""]
    else:
        if linhas_nota and linhas_nota[-1].strip():
            linhas_nota.append(u"")
        linhas_nota += corpo + [u""]

    io.open(caminho, "w", encoding="utf-8", newline="\n").write(u"\n".join(linhas_nota) + u"\n")
    print(u"\nNota atualizada: %s > %s" % (os.path.basename(caminho), nome_secao))
    return 0


def semana_mais_recente_caminho():
    """Nota da semana com a DATA mais recente no nome.

    Ordenar o nome como texto poe 'Semana 31-08-26' depois de 'Semana 07-09-26',
    porque compara o dia antes do mes. Em 07/09/2026 isso fez as ferramentas
    escreverem na semana PASSADA sem dar erro nenhum.
    """
    import glob
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


if __name__ == "__main__":
    sys.exit(main())
