# -*- coding: utf-8 -*-
"""Motor de posse de secoes do cofre. Uma secao mora em UM arquivo por vez.

PROBLEMA QUE ELE RESOLVE (07/09/2026)
A autopsia do dia era montada com embed (`![[Semana#Segunda]]`). Embed do
Obsidian e SO LEITURA: pra marcar um checkbox ou preencher o tempo real o
fundador tinha que abrir a nota da semana, editar la e voltar. O dia inteiro
indo e voltando entre duas notas.

A SAIDA NAO E COPIAR, E MUDAR DE CASA
Copiar o bloco pra autopsia criaria duas versoes vivas do mesmo texto e um
merge pra reconciliar - que e exatamente onde se perde linha. Em vez disso a
secao se MUDA:

  de manha  `criar_autopsia.py` RECORTA a secao da nota da semana e cola na
            autopsia do dia. Na semana fica um ponteiro apontando pro dia.
  a noite   `fechar_dia.py` DEVOLVE a secao pra semana, no lugar do ponteiro.

Em qualquer instante existe um arquivo so que e dono daquele texto. Nao ha
duas copias, entao nao ha conflito nem reconciliacao.

O DONO E PROCURADO, NUNCA ASSUMIDO
`dono_da_secao()` olha a autopsia do dia primeiro e a nota da semana depois.
Se o fechamento de ontem nao rodou (PC desligado, madrugada virada), o texto
continua na autopsia de ontem e o motor acha ele la. Nenhum consumidor pode
assumir "esta na semana": era essa suposicao que amarrava tudo ao embed.

POR QUE RX_TITULO PARA EM 4 CERQUILHAS
O bloco do dia usa `##### 09h-11h (...)` pras janelas. Se o regex enxergasse
5 cerquilhas, a primeira janela viraria fronteira de secao e o recorte levaria
so o cabecalho do dia, deixando a rotina inteira pra tras. O limite em `#{2,4}`
NAO e descuido: e o que mantem as janelas dentro do bloco. Ver secao 6 do
senior_dev_playbook - ferramenta que le posicao fixa envelhece calada.
"""
import difflib
import glob
import io
import os
import re
import shutil
import sys
import unicodedata
import datetime as dt

if sys.platform == "win32":
    try:
        import codecs
        sys.stdout = codecs.getwriter("utf-8")(sys.stdout.buffer, "replace")
    except AttributeError:
        pass

# tools/ -> dodo-ia/ -> skills/ -> .agents (ou .claude)/ -> raiz do workspace
RAIZ = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", ".."))
VAULT = os.path.join(RAIZ, "Vault")
PESSOAL = os.path.join(VAULT, "Vida Pessoal")
ROTINA = os.path.join(PESSOAL, "Rotina")
SEMANA = os.path.join(PESSOAL, "Semana")
INSIGHTS_GERAL = os.path.join(VAULT, "Insights", "Insights Geral.md")
BACKUP = os.path.join(RAIZ, ".backups", "autopsia")

MESES = (u"Janeiro", u"Fevereiro", u"Mar\u00e7o", u"Abril", u"Maio", u"Junho",
         u"Julho", u"Agosto", u"Setembro", u"Outubro", u"Novembro", u"Dezembro")
DIAS = (u"Segunda", u"Ter\u00e7a", u"Quarta", u"Quinta", u"Sexta",
        u"S\u00e1bado", u"Domingo")

# Ver o docstring: parar em 4 e o que mantem `##### <janela>` dentro do bloco.
RX_TITULO = re.compile(r"^#{2,4}\s+(.+?)\s*:?\s*$")
RX_DATA_ARQ = re.compile(r"(\d{2})-(\d{2})-(\d{2})")

# Marca deixada na nota da semana enquanto a secao esta na autopsia. Precisa ser
# reconhecivel por regex: e ela que `devolver_posse` apaga pra por o texto de
# volta. Qualquer outra coisa no lugar significa que alguem escreveu na semana
# com a secao fora - e ai a devolucao para, em vez de escrever por cima.
PONTEIRO_PREFIXO = u"> Em posse da aut\u00f3psia do dia:"

# Linha de transclusao (`![[Semana 07-09-26#Segunda]]`). Ela PARECE conteudo e
# nao e: e a vitrine somente-leitura do modelo antigo. Tratar embed como texto
# faria o transporte pular toda secao ainda no formato velho, e o dia nasceria
# vazio sem erro nenhum. E tambem o que torna a migracao automatica: a primeira
# tomada de posse enxerga a secao como vazia e escreve o texto de verdade nela.
RX_EMBED = re.compile(r"^!\[\[.+\]\]$")


def eh_embed(linha):
    return bool(RX_EMBED.match(linha.strip()))


def ponteiro(nome_autopsia):
    return u"%s [[%s]]" % (PONTEIRO_PREFIXO, nome_autopsia)


def eh_ponteiro(linha):
    return linha.strip().startswith(PONTEIRO_PREFIXO)


def normalizar(texto):
    """minusculo e sem acento, pra 'Pendencias' casar com 'Pend\u00eancias'."""
    if texto is None:
        return u""
    sem_acento = unicodedata.normalize("NFKD", texto)
    sem_acento = u"".join(c for c in sem_acento if not unicodedata.combining(c))
    return sem_acento.strip().lower()


# ---------------------------------------------------------------- arquivo


def ler(caminho):
    """(linhas, fim_de_linha). Preserva CRLF do arquivo pra nao sujar o diff."""
    with io.open(caminho, encoding="utf-8", newline="") as fh:
        bruto = fh.read()
    fim = u"\r\n" if u"\r\n" in bruto else u"\n"
    return bruto.replace(u"\r\n", u"\n").split(u"\n"), fim


def gravar(caminho, linhas, fim_linha, com_backup=True):
    """Grava, sempre com copia de seguranca antes.

    O backup nao e zelo excessivo: o cofre sincroniza pro celular. Se ele
    escreveu algo no celular e a sincronizacao ainda nao chegou, o recorte
    passa por cima - e a copia e a unica forma de voltar.
    """
    if com_backup and os.path.isfile(caminho):
        if not os.path.isdir(BACKUP):
            os.makedirs(BACKUP)
        copia = os.path.join(BACKUP, u"%s_%s" % (
            dt.datetime.now().strftime("%Y%m%d-%H%M%S"),
            os.path.basename(caminho)))
        shutil.copy2(caminho, copia)
    with io.open(caminho, "w", encoding="utf-8", newline="") as fh:
        fh.write(fim_linha.join(linhas))


def mostrar_diff(antes, depois, rotulo):
    """Imprime so o que mudou. Usado pelo --dry-run de todos os comandos."""
    saida = list(difflib.unified_diff(antes, depois, lineterm="", n=1))
    if not saida:
        print(u"  %s: nada muda" % rotulo)
        return
    print(u"  %s:" % rotulo)
    for linha in saida:
        if linha.startswith(u"+++") or linha.startswith(u"---"):
            continue
        if linha.startswith(u"+"):
            print(u"    + %s" % linha[1:].replace(u"\t", u"    "))
        elif linha.startswith(u"-"):
            print(u"    - %s" % linha[1:].replace(u"\t", u"    "))


# ---------------------------------------------------------------- secoes


def indice_do_titulo(linhas, nome):
    """Linha do titulo da secao, ou None. Compara sem acento e sem os dois pontos."""
    alvo = normalizar(nome)
    for i, linha in enumerate(linhas):
        m = RX_TITULO.match(linha)
        if m and normalizar(m.group(1)) == alvo:
            return i
    return None


def limites_da_secao(linhas, nome):
    """(inicio, fim) do CONTEUDO da secao. inicio = linha logo apos o titulo."""
    i = indice_do_titulo(linhas, nome)
    if i is None:
        return None, None
    for j in range(i + 1, len(linhas)):
        if RX_TITULO.match(linhas[j]):
            return i + 1, j
    return i + 1, len(linhas)


def profundidade(linha):
    return len(linha) - len(linha.lstrip(u"\t"))


def fim_do_bloco(linhas, pos, fim_secao):
    """Ultima linha da subarvore que comeca em `pos` (exclusivo)."""
    base = profundidade(linhas[pos])
    fim = pos + 1
    while fim < fim_secao:
        linha = linhas[fim]
        if linha.strip() and profundidade(linha) <= base:
            break
        fim += 1
    while fim > pos + 1 and not linhas[fim - 1].strip():
        fim -= 1
    return fim


def _sem_brancos_nas_pontas(corpo):
    ini, fim = 0, len(corpo)
    while ini < fim and not corpo[ini].strip():
        ini += 1
    while fim > ini and not corpo[fim - 1].strip():
        fim -= 1
    return corpo[ini:fim]


def corpo_da_secao(linhas, nome):
    """Conteudo da secao sem os brancos das pontas, ou None se a secao nao existe."""
    ini, fim = limites_da_secao(linhas, nome)
    if ini is None:
        return None
    return _sem_brancos_nas_pontas(linhas[ini:fim])


def substituir_secao(linhas, nome, novo_corpo):
    """Troca o conteudo da secao. Mantem uma linha em branco antes do proximo titulo."""
    ini, fim = limites_da_secao(linhas, nome)
    if ini is None:
        raise ValueError(u"secao '%s' nao encontrada" % nome)
    corpo = list(_sem_brancos_nas_pontas(novo_corpo))
    if fim < len(linhas):
        corpo = corpo + [u""]
    return linhas[:ini] + corpo + linhas[fim:]


# ---------------------------------------------------------------- notas


def nome_do_dia(dia):
    return DIAS[dia.weekday()]


def nome_autopsia(dia):
    return u"Autopsia das intencoes %s" % dia.strftime("%d-%m-%y")


def caminho_autopsia(dia):
    """Onde a autopsia do dia mora - exista ela ou nao."""
    return os.path.join(ROTINA, MESES[dia.month - 1],
                        nome_autopsia(dia) + u".md")


def autopsia_do_dia(dia):
    """Caminho da autopsia daquele dia, ou None. A data esta no NOME do arquivo.

    Varre a arvore inteira porque o fundador ja renomeou nota a mao ('Autopsia
    das Intencoes 07-08-26', com I maiusculo) e ja moveu nota de pasta.
    """
    for caminho in glob.glob(os.path.join(ROTINA, "*", "*.md")):
        if os.path.basename(os.path.dirname(caminho)) == "Semana":
            continue
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
    """Nota da semana que COBRE o dia. O nome carrega a segunda que abre a semana.

    Testa containment (0..6 dias), nunca 'a mais recente': ordenar
    'Semana DD-MM-AA' como texto poe 31-08-26 depois de 07-09-26. Esse defeito
    ja mordeu tres ferramentas em 07/09/2026 (msg_006).
    """
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


def data_da_semana(caminho):
    """date da SEGUNDA que abre a semana, tirada do nome 'Semana DD-MM-AA.md'."""
    m = RX_DATA_ARQ.search(os.path.basename(caminho))
    if not m:
        return None
    d, mes, ano = (int(x) for x in m.groups())
    try:
        return dt.date(2000 + ano, mes, d)
    except ValueError:
        return None


def semana_mais_recente():
    """Nota da semana com a DATA mais recente no nome, ou None.

    Pela data parseada, nunca pelo texto do nome: 'Semana 31-08-26' ordenado
    como texto vem depois de 'Semana 07-09-26', e em 07/09/2026 esse defeito fez
    tres ferramentas escreverem na semana passada sem erro nenhum (msg_006).
    """
    achados = []
    for caminho in glob.glob(os.path.join(SEMANA, "Semana *.md")):
        data = data_da_semana(caminho)
        if data is not None:
            achados.append((data, caminho))
    return max(achados)[1] if achados else None


def data_do_dia(nome_dia, caminho_semana=None):
    """date daquele dia da semana, dentro da semana indicada (ou a mais recente).

    Ponte entre as ferramentas que falam por nome ('--dia Segunda') e o motor,
    que precisa de data pra saber qual autopsia procurar.
    """
    alvo = normalizar(nome_dia)
    indice = next((i for i, d in enumerate(DIAS) if normalizar(d) == alvo), None)
    if indice is None:
        return None
    caminho_semana = caminho_semana or semana_mais_recente()
    if not caminho_semana:
        return None
    segunda = data_da_semana(caminho_semana)
    return segunda + dt.timedelta(days=indice) if segunda else None


# ---------------------------------------------------------------- posse

# (nome na nota da SEMANA, nome na AUTOPSIA). O bloco do dia troca de nome:
# na semana ele e `#### Segunda`, na autopsia e `### Rotina e tarefas de hoje`.
# O heading `#### Segunda` NAO viaja junto - se viajasse, viraria fronteira de
# secao dentro da autopsia e cortaria a propria rotina fora dela.
def secoes_moveis(dia):
    return [
        (nome_do_dia(dia), u"Rotina e tarefas de hoje"),
        (u"Pend\u00eancias", u"Pend\u00eancias"),
        (u"Perguntas", u"Perguntas"),
        (u"Desejos", u"Desejos"),
        (u"Ideias", u"Ideias"),
    ]


SEC_RESOLUCAO = u"Resolu\u00e7\u00e3o de Problemas"


def dono_da_secao(nome_na_autopsia, dia):
    """(caminho, corpo) de quem tem a secao agora. Autopsia primeiro, semana depois.

    Devolve (None, None) se ninguem tem. Nunca assume a semana: se o fechamento
    de ontem nao rodou, o texto esta na autopsia e e la que ele tem que ser lido.
    """
    caminho = autopsia_do_dia(dia)
    if caminho:
        linhas, _ = ler(caminho)
        corpo = corpo_da_secao(linhas, nome_na_autopsia)
        if corpo is not None and not _vazia(corpo):
            return caminho, corpo
    caminho = semana_do_dia(dia)
    if caminho:
        linhas, _ = ler(caminho)
        for na_semana, na_autopsia in secoes_moveis(dia):
            if normalizar(na_autopsia) == normalizar(nome_na_autopsia):
                corpo = corpo_da_secao(linhas, na_semana)
                if corpo is not None:
                    return caminho, corpo
    return None, None


def bloco_do_dia(dia):
    """(caminho, corpo) da rotina do dia, onde quer que ela esteja agora.

    E o que `recalcular_dia`, `montar_esqueleto_dia`, `equilibrio_das_areas` e
    `dissecar_autopsia` usam pra parar de assumir que o bloco esta na semana.
    """
    return dono_da_secao(u"Rotina e tarefas de hoje", dia)


def nome_da_secao_no_arquivo(caminho, dia):
    """Como a rotina do dia se chama naquele arquivo: 'Segunda' ou o titulo longo."""
    if caminho and os.path.basename(os.path.dirname(caminho)) == "Semana":
        return nome_do_dia(dia)
    return u"Rotina e tarefas de hoje"


# ----------------------------------------- resolucao de problemas (por dia)


def _item_do_dia(linhas, dia):
    """(indice, fim) do item '- Segunda:' dentro de Resolucao de Problemas."""
    ini, fim = limites_da_secao(linhas, SEC_RESOLUCAO)
    if ini is None:
        return None, None
    alvo = normalizar(nome_do_dia(dia))
    for i in range(ini, fim):
        texto = linhas[i].strip()
        if not texto.startswith(u"- "):
            continue
        if profundidade(linhas[i]) != 0:
            continue
        if normalizar(texto[2:].rstrip().rstrip(u":")) == alvo:
            return i, fim_do_bloco(linhas, i, fim)
    return None, None


def tirar_resolucao(linhas, dia):
    """Retira os filhos de '- Segunda:' e devolve (linhas, corpo sem um nivel de tab).

    A linha '- Segunda:' FICA na semana. So os filhos viajam, senao a ordem dos
    sete dias se perde e a devolucao teria que adivinhar onde reinserir.
    """
    i, fim = _item_do_dia(linhas, dia)
    if i is None:
        return linhas, None
    filhos = linhas[i + 1:fim]
    corpo = [(l[1:] if l.startswith(u"\t") else l) for l in filhos]
    return linhas[:i + 1] + linhas[fim:], _sem_brancos_nas_pontas(corpo)


def por_resolucao(linhas, dia, corpo):
    """Recoloca os filhos sob '- Segunda:', reindentando um nivel."""
    corpo = _sem_brancos_nas_pontas(corpo or [])
    if not corpo:
        return linhas, u"vazia, nada a devolver"
    i, fim = _item_do_dia(linhas, dia)
    if i is None:
        return linhas, u"item '- %s:' nao existe na semana" % nome_do_dia(dia)
    if fim > i + 1 and any(l.strip() for l in linhas[i + 1:fim]):
        return linhas, u"JA TEM CONTEUDO na semana - devolucao abortada"
    filhos = [(u"\t" + l if l.strip() else l) for l in corpo]
    return linhas[:i + 1] + filhos + linhas[i + 1:], u"%d linha(s)" % len(filhos)


# ----------------------------------------------- tomar e devolver a posse

PONTEIRO_DEVOLVIDO = u"> Devolvido para:"


def devolvido(nome_semana):
    return u"%s [[%s]]" % (PONTEIRO_DEVOLVIDO, nome_semana)


def _vazia(corpo):
    """Secao sem nada util: vazia, so brancos, ou so um ponteiro."""
    corpo = _sem_brancos_nas_pontas(corpo or [])
    if not corpo:
        return True
    return all(eh_ponteiro(l) or eh_embed(l)
               or l.strip().startswith(PONTEIRO_DEVOLVIDO)
               for l in corpo)


def tomar_posse(dia, dry_run=False):
    """Recorta as secoes da nota da semana e cola na autopsia do dia.

    Nao cria a autopsia - `criar_autopsia.py` escreve o esqueleto com as secoes
    vazias e chama isto pra preencher. Secao que ja tem conteudo no destino e
    PULADA: e o que impede escrever por cima do que ele digitou no celular.
    """
    aut = autopsia_do_dia(dia)
    if not aut:
        return 1, [u"a autopsia de %s nao existe" % dia.strftime("%d/%m/%y")]
    sem = semana_do_dia(dia)
    if not sem:
        return 1, [u"nenhuma nota de semana cobre %s" % dia.strftime("%d/%m/%y")]

    linhas_aut, fim_aut = ler(aut)
    linhas_sem, fim_sem = ler(sem)
    antes_aut, antes_sem = list(linhas_aut), list(linhas_sem)
    relato, movidas = [], 0

    for na_semana, na_autopsia in secoes_moveis(dia):
        corpo = corpo_da_secao(linhas_sem, na_semana)
        if corpo is None:
            relato.append(u"%-24s a semana nao tem essa secao" % na_semana)
            continue
        if _vazia(corpo):
            relato.append(u"%-24s vazia na semana (ou ja em posse de outro dia)"
                          % na_semana)
            continue
        if corpo_da_secao(linhas_aut, na_autopsia) is None:
            relato.append(u"%-24s a autopsia nao tem '%s'" % (na_semana, na_autopsia))
            continue
        if not _vazia(corpo_da_secao(linhas_aut, na_autopsia)):
            relato.append(u"%-24s PULADA: a autopsia ja tem conteudo ai" % na_semana)
            continue
        linhas_aut = substituir_secao(linhas_aut, na_autopsia, corpo)
        linhas_sem = substituir_secao(linhas_sem, na_semana,
                                      [ponteiro(nome_autopsia(dia))])
        relato.append(u"%-24s -> autopsia (%d linhas)" % (na_semana, len(corpo)))
        movidas += 1

    novas_sem, corpo_res = tirar_resolucao(linhas_sem, dia)
    if corpo_res:
        if corpo_da_secao(linhas_aut, SEC_RESOLUCAO) is None:
            relato.append(u"%-24s a autopsia nao tem essa secao" % SEC_RESOLUCAO)
        elif not _vazia(corpo_da_secao(linhas_aut, SEC_RESOLUCAO)):
            relato.append(u"%-24s PULADA: a autopsia ja tem conteudo ai" % SEC_RESOLUCAO)
        else:
            linhas_aut = substituir_secao(linhas_aut, SEC_RESOLUCAO, corpo_res)
            linhas_sem = novas_sem
            relato.append(u"%-24s -> autopsia (%d linhas)" % (SEC_RESOLUCAO, len(corpo_res)))
            movidas += 1

    if dry_run:
        mostrar_diff(antes_aut, linhas_aut, os.path.basename(aut))
        mostrar_diff(antes_sem, linhas_sem, os.path.basename(sem))
        return 0, relato
    if movidas:
        gravar(aut, linhas_aut, fim_aut)
        gravar(sem, linhas_sem, fim_sem)
    return 0, relato


def devolver_posse(dia, dry_run=False):
    """Devolve as secoes da autopsia do dia pra nota da semana.

    ABORTA a secao (sem escrever) se a semana ganhou conteudo enquanto a secao
    estava fora. Nesse caso existem dois textos e quem decide o que fica e ele -
    perder um em silencio seria o pior resultado possivel.
    """
    aut = autopsia_do_dia(dia)
    if not aut:
        return 1, [u"a autopsia de %s nao existe" % dia.strftime("%d/%m/%y")]
    sem = semana_do_dia(dia)
    if not sem:
        return 1, [u"nenhuma nota de semana cobre %s" % dia.strftime("%d/%m/%y")]

    linhas_aut, fim_aut = ler(aut)
    linhas_sem, fim_sem = ler(sem)
    antes_aut, antes_sem = list(linhas_aut), list(linhas_sem)
    nome_sem = os.path.splitext(os.path.basename(sem))[0]
    relato, movidas, conflitos = [], 0, 0

    for na_semana, na_autopsia in secoes_moveis(dia):
        corpo = corpo_da_secao(linhas_aut, na_autopsia)
        if corpo is None or _vazia(corpo):
            relato.append(u"%-24s nada a devolver" % na_autopsia)
            continue
        destino = corpo_da_secao(linhas_sem, na_semana)
        if destino is None:
            relato.append(u"%-24s a semana nao tem '%s'" % (na_autopsia, na_semana))
            continue
        if not _vazia(destino):
            relato.append(u"%-24s CONFLITO: a semana tem conteudo proprio - abortada"
                          % na_autopsia)
            conflitos += 1
            continue
        linhas_sem = substituir_secao(linhas_sem, na_semana, corpo)
        linhas_aut = substituir_secao(linhas_aut, na_autopsia, [devolvido(nome_sem)])
        relato.append(u"%-24s -> semana (%d linhas)" % (na_autopsia, len(corpo)))
        movidas += 1

    corpo_res = corpo_da_secao(linhas_aut, SEC_RESOLUCAO)
    if corpo_res is not None and not _vazia(corpo_res):
        novas_sem, nota = por_resolucao(linhas_sem, dia, corpo_res)
        if nota.startswith(u"JA TEM CONTEUDO"):
            relato.append(u"%-24s CONFLITO: %s" % (SEC_RESOLUCAO, nota))
            conflitos += 1
        elif novas_sem is linhas_sem and u"nao existe" in nota:
            relato.append(u"%-24s %s" % (SEC_RESOLUCAO, nota))
        else:
            linhas_sem = novas_sem
            linhas_aut = substituir_secao(linhas_aut, SEC_RESOLUCAO, [devolvido(nome_sem)])
            relato.append(u"%-24s -> semana (%s)" % (SEC_RESOLUCAO, nota))
            movidas += 1
    else:
        relato.append(u"%-24s nada a devolver" % SEC_RESOLUCAO)

    if dry_run:
        mostrar_diff(antes_aut, linhas_aut, os.path.basename(aut))
        mostrar_diff(antes_sem, linhas_sem, os.path.basename(sem))
        return 0, relato
    if movidas:
        gravar(aut, linhas_aut, fim_aut)
        gravar(sem, linhas_sem, fim_sem)
    return (2 if conflitos else 0), relato


def semana_reconstituida(caminho_semana):
    """Linhas da semana COMO SE todos os dias ja estivessem fechados. So leitura.

    Existe pras ferramentas que apenas CONTAM e ANALISAM (equilibrio das areas,
    dissecacao da identidade). Elas leem a nota da semana inteira e derivam
    numero dali; com um dia em posse da autopsia, aquele dia sumiria da conta e
    o placar sairia menor SEM ERRO NENHUM - relatorio errado com cara de certo,
    que e o defeito descrito na secao 6 do senior_dev_playbook.

    Devolve linhas em memoria. NUNCA grava: quem escreve tem que falar com o
    dono de verdade, senao escreveria numa copia que ninguem le.
    """
    linhas, _ = ler(caminho_semana)
    segunda = data_da_semana(caminho_semana)
    if segunda is None:
        return linhas
    for i in range(7):
        dia = segunda + dt.timedelta(days=i)
        corpo_semana = corpo_da_secao(linhas, nome_do_dia(dia))
        if corpo_semana is None or not _vazia(corpo_semana):
            continue  # o bloco esta na semana mesmo
        aut = autopsia_do_dia(dia)
        if not aut:
            continue
        linhas_aut, _ = ler(aut)
        corpo = corpo_da_secao(linhas_aut, u"Rotina e tarefas de hoje")
        if corpo is None or _vazia(corpo):
            continue
        linhas = substituir_secao(linhas, nome_do_dia(dia), corpo)
    return linhas


def dia_esta_aberto(dia):
    """True se alguma secao movel ainda esta na autopsia daquele dia."""
    aut = autopsia_do_dia(dia)
    if not aut:
        return False
    linhas, _ = ler(aut)
    for _, na_autopsia in secoes_moveis(dia):
        corpo = corpo_da_secao(linhas, na_autopsia)
        if corpo is not None and not _vazia(corpo):
            return True
    corpo = corpo_da_secao(linhas, SEC_RESOLUCAO)
    return corpo is not None and not _vazia(corpo)
