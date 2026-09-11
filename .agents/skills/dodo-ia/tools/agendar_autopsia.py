# -*- coding: utf-8 -*-
"""Le a autopsia das intencoes mais recente e agenda o dia na agenda "Dodo.IA".

Fase 3 do projeto Dodo.IA. Fecha a pendencia "Criar automacao que pega a autopsia
das intencoes e agenda no Google agenda".

Como funciona:
  1. Acha a nota da semana que cobre o dia em Vault/Vida Pessoal/Semana/
     (o nome carrega a data da segunda que abre a semana).
  2. Dentro de `### Metas` -> `- Semana:`, pega o bloco do dia da semana pedido.
  3. Item com hora (`14h15`, `19h`) vira evento com hora. Todo o resto vira UM
     bloco as 09:00 com a lista na descricao. Item ja marcado `[x]` e ignorado.
  4. Escreve na agenda "Dodo.IA" (cria se nao existir), nunca na principal.
  5. Cada evento criado leva a etiqueta privada `dodoia=1`. Ao rodar de novo, o
     script apaga SO os eventos com essa etiqueta naquele dia e recria. Compromisso
     que o fundador criou na mao nunca e tocado.

Credenciais (nada novo: reaproveita o que o MCP do Google Agenda ja autorizou):
  - client secret: <DODO_GOOGLE_CRED_DIR ou ~/credenciais/MCP - Google Agenda>/<conta>/client_secret_*.json
  - token:         %USERPROFILE%\\.config\\google-calendar-mcp\\tokens.json

Uso:
  python agendar_autopsia.py --dry-run          # mostra o que faria, nao escreve
  python agendar_autopsia.py                    # agenda hoje
  python agendar_autopsia.py --dia 2026-08-18   # agenda um dia especifico
"""
import argparse
import datetime as dt
import glob
import io
import json
import os
import re
import sys
import unicodedata

# tools/ -> dodo-ia/ -> skills/ -> .agents (ou .claude)/ -> raiz do workspace
RAIZ = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", ".."))
VAULT = os.path.join(RAIZ, "Vault")
PESSOAL = os.path.join(VAULT, "Vida Pessoal")
ROTINA = os.path.join(PESSOAL, "Rotina")
SEMANA = os.path.join(PESSOAL, "Semana")
CRED_DIR = os.environ.get("DODO_GOOGLE_CRED_DIR",
                          os.path.expanduser(os.path.join("~", "credenciais", "MCP - Google Agenda")))
TOKEN = os.path.join(os.path.expanduser("~"), ".config", "google-calendar-mcp", "tokens.json")
AGENDA = "Dodo.IA"
FUSO = "America/Sao_Paulo"
HORA_BLOCO = 9          # onde cai o bloco dos itens sem hora
DURACAO_PADRAO_MIN = 60
# `tipo` separa os produtores: cada script so apaga o que ele mesmo escreve.
# Sem isso, o resumo financeiro e o bloco do dia se apagariam um ao outro.
ETIQUETA = {"dodoia": "1", "tipo": "dia"}

RX_DATA_ARQ = re.compile(r"(\d{2})-(\d{2})-(\d{2})")
RX_HORA = re.compile(r"(\d{1,2})\s*h\s*(\d{2})?\b")
RX_ITEM = re.compile(r"^([\t ]*)[-+*]\s+(?:\[( |x|X)\]\s*)?(.*)$")
RX_BLOCO = re.compile(r"\s*\^[A-Za-z0-9-]+\s*$")  # id de bloco do Obsidian
RX_TAG = re.compile(r"\s*#[A-Za-zÀ-ú][\w-]*\s*$")  # tag de area da vida

DIAS = {
    0: ("segunda",), 1: ("terca", "terça"), 2: ("quarta",), 3: ("quinta",),
    4: ("sexta",), 5: ("sabado", "sábado"), 6: ("domingo",),
}


def sem_acento(txt):
    txt = unicodedata.normalize("NFKD", txt)
    return "".join(c for c in txt if not unicodedata.combining(c))


def achar_autopsia():
    """Devolve (caminho, data) da autopsia mais recente. A data esta no NOME."""
    achados = []
    for caminho in glob.glob(os.path.join(ROTINA, "*", "*.md")):
        if os.path.basename(os.path.dirname(caminho)) == "Semana":
            continue  # nota de semana nao e autopsia
        m = RX_DATA_ARQ.search(os.path.basename(caminho))
        if m:
            d, mes, ano = (int(x) for x in m.groups())
            try:
                achados.append((dt.date(2000 + ano, mes, d), caminho))
            except ValueError:
                continue  # data invalida no nome, ignora
    if not achados:
        raise SystemExit("Nenhuma autopsia encontrada em %s" % ROTINA)
    achados.sort()
    return achados[-1][1], achados[-1][0]


def achar_semana(alvo):
    """Devolve o caminho da nota da semana que contem o dia alvo.

    O nome da nota carrega a data da SEGUNDA que abre a semana (DD-MM-AA).
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
        if 0 <= (alvo - segunda).days <= 6:
            return caminho, segunda
    return None, None


def indentacao(prefixo):
    return prefixo.replace("\t", "    ").count(" ")


def bloco_do_dia(caminho, alvo):
    """Extrai o bloco do dia de dentro de `### Metas` -> `#### <Dia>`.

    O dia e um titulo de nivel 4; o contexto vem na linha de citacao logo abaixo.
    Devolve (contexto_do_dia, [(indent, feito, texto), ...]).
    """
    with io.open(caminho, encoding="utf-8", errors="replace") as fh:
        linhas = fh.read().splitlines()

    nomes = DIAS[alvo.weekday()]
    em_metas = False
    coletando = False
    contexto = ""
    itens = []

    for linha in linhas:
        if linha.startswith("#"):
            titulo = sem_acento(linha).lower().strip("# ").strip()
            nivel = len(linha) - len(linha.lstrip("#"))
            if nivel <= 3:
                # titulo de secao: entra ou sai de Metas
                if coletando:
                    break
                em_metas = titulo.startswith("metas")
                continue
            if not em_metas:
                continue
            if coletando:
                break  # chegou o proximo dia
            coletando = any(titulo.startswith(n) for n in nomes)
            continue

        if not coletando:
            continue

        if linha.lstrip().startswith(">"):
            if not contexto:
                contexto = linha.lstrip("> 	").strip()
            continue

        m = RX_ITEM.match(linha)
        if not m:
            continue
        ind, marca, texto = indentacao(m.group(1)), m.group(2), m.group(3).strip()
        texto = RX_TAG.sub("", RX_BLOCO.sub("", texto)).strip()
        if not texto:
            continue
        itens.append((ind, marca is not None and marca.lower() == "x", texto))

    return contexto, itens


def extrair_hora(texto):
    """Devolve (titulo_sem_hora, hora, minuto) ou (texto, None, None)."""
    m = None
    for m in RX_HORA.finditer(texto):
        pass  # a hora fica no fim da linha; interessa a ultima
    if not m:
        return texto, None, None
    hora = int(m.group(1))
    minuto = int(m.group(2) or 0)
    if not (0 <= hora <= 23 and 0 <= minuto <= 59):
        return texto, None, None
    titulo = (texto[:m.start()] + texto[m.end():]).strip().strip(":-– ").strip()
    return titulo or texto, hora, minuto


def subarvore(itens, pos):
    """Posicoes dos descendentes de `pos` (mais indentados, ate o proximo irmao)."""
    ind = itens[pos][0]
    fim = pos + 1
    while fim < len(itens) and itens[fim][0] > ind:
        fim += 1
    return list(range(pos + 1, fim))


def montar_eventos(contexto, itens, dia):
    """Separa o que tem hora do que nao tem. Devolve lista de eventos."""
    # 1. Itens com hora viram evento proprio, levando a subarvore como descricao.
    #    A posicao e guardada: procurar depois pela hora confunde dois itens no
    #    mesmo horario (bug real da sexta, com dois blocos as 14h30).
    consumidas = set()
    com_hora = []
    for pos, (ind, feito, texto) in enumerate(itens):
        if feito or pos in consumidas:
            continue
        titulo, hora, minuto = extrair_hora(texto)
        if hora is None:
            continue
        filhos = subarvore(itens, pos)
        com_hora.append({
            "titulo": titulo, "hora": hora, "minuto": minuto,
            "filhos": [itens[p][2] for p in filhos if not itens[p][1]],
        })
        consumidas.add(pos)
        consumidas.update(filhos)

    # 2. O resto vai pro bloco unico, menos categoria que ficou sem item embaixo.
    soltos = [pos for pos, (ind, feito, texto) in enumerate(itens)
              if pos not in consumidas and not feito]
    restantes = set(soltos)
    # de baixo pra cima: o filho e descartado antes do pai ser avaliado, senao
    # sobra categoria orfa (pai mantido por um filho que caiu depois dele)
    for pos in sorted(soltos, reverse=True):
        texto = itens[pos][2]
        if texto.endswith(":") and not any(p in restantes for p in subarvore(itens, pos)):
            restantes.discard(pos)  # cabecalho de categoria vazia e ruido

    eventos = []
    if restantes:
        ordenadas = sorted(restantes)
        base = min(itens[p][0] for p in ordenadas)
        linhas = ["  " * max(0, (itens[p][0] - base) // 4) + "- " + itens[p][2]
                  for p in ordenadas]
        descricao = ("Contexto do dia: %s\n\n" % contexto if contexto else "") + "\n".join(linhas)
        eventos.append({
            "titulo": "[ Dodo.IA ] Tarefas do dia",
            "inicio": dt.datetime.combine(dia, dt.time(HORA_BLOCO, 0)),
            "minutos": DURACAO_PADRAO_MIN,
            "descricao": descricao,
        })
    for ev in com_hora:
        eventos.append({
            "titulo": ev["titulo"],
            "inicio": dt.datetime.combine(dia, dt.time(ev["hora"], ev["minuto"])),
            "minutos": DURACAO_PADRAO_MIN,
            "descricao": "\n".join(ev["filhos"]),
        })
    eventos.sort(key=lambda e: e["inicio"])
    return eventos


def conectar():
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build

    segredos = glob.glob(os.path.join(CRED_DIR, "*", "client_secret_*.json"))
    if not segredos:
        raise SystemExit("Client secret nao encontrado em %s" % CRED_DIR)
    with io.open(segredos[0], encoding="utf-8") as fh:
        cfg = json.load(fh)
    cfg = cfg.get("installed") or cfg.get("web") or {}

    if not os.path.isfile(TOKEN):
        raise SystemExit("Token nao encontrado em %s. Autorize o MCP da agenda primeiro." % TOKEN)
    with io.open(TOKEN, encoding="utf-8") as fh:
        tok = json.load(fh)
    tok = tok.get("normal") or tok

    creds = Credentials(
        token=tok.get("access_token"),
        refresh_token=tok.get("refresh_token"),
        token_uri="https://oauth2.googleapis.com/token",
        client_id=cfg.get("client_id"),
        client_secret=cfg.get("client_secret"),
        scopes=[tok.get("scope", "https://www.googleapis.com/auth/calendar")],
    )
    if not creds.valid:
        creds.refresh(Request())  # o refresh_token nao muda; nada e regravado
    return build("calendar", "v3", credentials=creds, cache_discovery=False)


def id_da_agenda(api, criar=True):
    pagina = None
    while True:
        r = api.calendarList().list(pageToken=pagina).execute()
        for c in r.get("items", []):
            if c.get("summary") == AGENDA:
                return c["id"]
        pagina = r.get("nextPageToken")
        if not pagina:
            break
    if not criar:
        return None
    novo = api.calendars().insert(body={"summary": AGENDA, "timeZone": FUSO}).execute()
    print("agenda '%s' criada" % AGENDA)
    return novo["id"]


def limpar_do_dia(api, cal_id, dia, tipo="dia"):
    """Apaga SO os eventos daquele `tipo` que este ecossistema criou no dia."""
    ini = dt.datetime.combine(dia, dt.time.min).isoformat() + "-03:00"
    fim = dt.datetime.combine(dia, dt.time.max).isoformat() + "-03:00"
    r = api.events().list(calendarId=cal_id, timeMin=ini, timeMax=fim,
                          privateExtendedProperty=["dodoia=1", "tipo=%s" % tipo],
                          singleEvents=True, maxResults=250).execute()
    apagados = 0
    for ev in r.get("items", []):
        api.events().delete(calendarId=cal_id, eventId=ev["id"]).execute()
        apagados += 1
    return apagados


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="mostra e nao escreve")
    ap.add_argument("--dia", help="AAAA-MM-DD (padrao: hoje)")
    args = ap.parse_args()

    dia = dt.date.today()
    if args.dia:
        dia = dt.datetime.strptime(args.dia, "%Y-%m-%d").date()

    caminho, segunda = achar_semana(dia)
    if not caminho:
        print("Nenhuma nota de semana cobre %s em %s." % (dia.strftime("%d/%m/%y"), SEMANA))
        print("Crie a nota da semana (nome: Semana DD-MM-AA, data da segunda) e rode de novo.")
        return 1
    print("semana lida: %s (abre em %s)"
          % (os.path.basename(caminho), segunda.strftime("%d/%m/%y")))

    nome_dia = DIAS[dia.weekday()][0]
    contexto, itens = bloco_do_dia(caminho, dia)
    if not itens:
        print("Nenhum item no bloco de %s. Nada a agendar." % nome_dia)
        return 0

    eventos = montar_eventos(contexto, itens, dia)
    print("dia alvo: %s (%s) | itens no bloco: %d | eventos: %d"
          % (dia.strftime("%d/%m/%y"), nome_dia, len(itens), len(eventos)))
    print()
    for ev in eventos:
        print("  %s  %s" % (ev["inicio"].strftime("%H:%M"), ev["titulo"]))
        for linha in (ev["descricao"] or "").splitlines():
            print("           %s" % linha)
    print()

    if args.dry_run:
        print("SIMULACAO: nada foi escrito na agenda.")
        return 0

    api = conectar()
    cal_id = id_da_agenda(api)
    apagados = limpar_do_dia(api, cal_id, dia)
    if apagados:
        print("substituindo %d evento(s) que este script tinha criado nesse dia" % apagados)

    for ev in eventos:
        fim = ev["inicio"] + dt.timedelta(minutes=ev["minutos"])
        api.events().insert(calendarId=cal_id, body={
            "summary": ev["titulo"],
            "description": ev["descricao"],
            "start": {"dateTime": ev["inicio"].isoformat(), "timeZone": FUSO},
            "end": {"dateTime": fim.isoformat(), "timeZone": FUSO},
            "extendedProperties": {"private": ETIQUETA},
            "source": {"title": os.path.basename(caminho), "url": "https://obsidian.md"},
        }).execute()
    print("agendado: %d evento(s) na agenda '%s'" % (len(eventos), AGENDA))
    return 0


if __name__ == "__main__":
    sys.exit(main())
