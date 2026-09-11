# -*- coding: utf-8 -*-
"""Reautoriza o acesso a Google Agenda e regrava o token que as outras ferramentas leem.

Existe porque em 24/08/2026 o refresh token morreu com `invalid_grant` - o app OAuth
estava em modo "Testing" no Google Cloud, e nesse modo o refresh token expira em 7 dias.
Reautorizar resolve o dia; publicar o app como "Production" resolve pra sempre.

O que faz:
  1. acha o client secret em <DODO_GOOGLE_CRED_DIR ou ~/credenciais/MCP - Google Agenda>/<conta>/
  2. abre o navegador pra voce aprovar com a SUA conta Google
  3. faz backup do token velho e grava o novo no formato que o MCP e os scripts leem
     (%USERPROFILE%\\.config\\google-calendar-mcp\\tokens.json, chave "normal")

Uso:
  python autorizar_google.py            # autoriza
  python autorizar_google.py --testar   # so testa o token que ja existe
"""
import argparse
import codecs
import datetime as dt
import glob
import io
import json
import os
import shutil
import sys

if sys.platform == "win32":
    try:
        sys.stdout = codecs.getwriter("utf-8")(sys.stdout.buffer, "replace")
    except AttributeError:
        pass

CRED_DIR = os.environ.get("DODO_GOOGLE_CRED_DIR",
                          os.path.expanduser(os.path.join("~", "credenciais", "MCP - Google Agenda")))
TOKEN = os.path.join(os.path.expanduser("~"), ".config", "google-calendar-mcp", "tokens.json")
ESCOPO = ["https://www.googleapis.com/auth/calendar"]


def client_secret():
    achados = glob.glob(os.path.join(CRED_DIR, "*", "client_secret_*.json"))
    if not achados:
        raise SystemExit(u"Client secret nao encontrado em %s" % CRED_DIR)
    return achados[0]


def testar():
    """Tenta usar o token atual. Devolve True se a agenda responde."""
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build

    if not os.path.isfile(TOKEN):
        print(u"Nao existe token em %s" % TOKEN)
        return False
    with io.open(client_secret(), encoding="utf-8") as fh:
        cfg = json.load(fh)
    cfg = cfg.get("installed") or cfg.get("web") or {}
    with io.open(TOKEN, encoding="utf-8") as fh:
        tok = json.load(fh)
    tok = tok.get("normal") or tok

    creds = Credentials(
        token=tok.get("access_token"),
        refresh_token=tok.get("refresh_token"),
        token_uri="https://oauth2.googleapis.com/token",
        client_id=cfg.get("client_id"),
        client_secret=cfg.get("client_secret"),
        scopes=[tok.get("scope") or ESCOPO[0]],
    )
    try:
        if not creds.valid:
            creds.refresh(Request())
        api = build("calendar", "v3", credentials=creds, cache_discovery=False)
        r = api.calendarList().list(maxResults=10).execute()
        nomes = [c.get("summary") for c in r.get("items", [])]
        print(u"Token VALIDO. Agendas visiveis: %s" % (u", ".join(nomes) or u"(nenhuma)"))
        return True
    except Exception as e:
        print(u"Token INVALIDO: %s" % e)
        return False


PORTA = 8765  # fixa, pra saber exatamente pra onde o Google vai redirecionar
REDIRECT = "http://localhost:%d/" % PORTA


def _flow():
    """Flow com redirect fixo - o mesmo pro modo automatico e pro manual."""
    from google_auth_oauthlib.flow import Flow
    f = Flow.from_client_secrets_file(client_secret(), ESCOPO)
    f.redirect_uri = REDIRECT
    return f


PKCE = os.path.join(os.path.dirname(TOKEN), ".pkce.json")


def mostrar_url():
    """Modo manual: imprime o link pra ele aprovar no navegador.

    Guarda o code_verifier e o state em disco: o link usa PKCE, e o segredo
    gerado aqui precisa ser o MESMO na hora de trocar o codigo por token.
    Sem isso, `--url` falha com 'invalid_grant'.
    """
    f = _flow()
    url, state = f.authorization_url(prompt="consent", access_type="offline")
    pasta = os.path.dirname(PKCE)
    if not os.path.isdir(pasta):
        os.makedirs(pasta)
    with io.open(PKCE, "w", encoding="utf-8") as fh:
        fh.write(json.dumps({"code_verifier": f.code_verifier, "state": state}))
    print(u"1. Abra este link no navegador:\n")
    print(u"   %s\n" % url)
    print(u"2. Escolha a conta e aprove.")
    print(u"3. A pagina final PODE dar erro de conexao - tudo bem, e esperado.")
    print(u"   O que importa esta na BARRA DE ENDERECOS: algo como")
    print(u"   %s?code=4/0Ab...&scope=..." % REDIRECT)
    print(u"4. Copie essa URL inteira e rode:\n")
    print(u'   python autorizar_google.py --url "COLE_A_URL_AQUI"\n')
    return True


def trocar_por_url(url):
    """Completa a autorizacao a partir da URL de retorno colada."""
    if not os.path.isfile(PKCE):
        raise SystemExit(u"Rode primeiro:  python autorizar_google.py --manual")
    with io.open(PKCE, encoding="utf-8") as fh:
        guardado = json.load(fh)
    f = _flow()
    f.code_verifier = guardado["code_verifier"]   # o mesmo segredo do link gerado
    f.fetch_token(authorization_response=url)
    try:
        os.remove(PKCE)
    except OSError:
        pass
    return gravar(f.credentials)


def autorizar():
    seg = client_secret()
    print(u"client secret: %s" % os.path.basename(seg))
    print(u"escopo:        %s" % ESCOPO[0])
    print(u"redirect:      %s" % REDIRECT)
    print(u"\nVai abrir o navegador. Escolha a conta Google dona da agenda.")
    print(u"Se aparecer 'Google nao verificou este app': Avancado > Acessar (nao verificado).")
    print(u"Se a pagina final nao voltar, use:  --manual\n")

    from google_auth_oauthlib.flow import InstalledAppFlow
    flow = InstalledAppFlow.from_client_secrets_file(seg, ESCOPO)
    creds = flow.run_local_server(port=PORTA, prompt="consent", access_type="offline")
    return gravar(creds)


def gravar(creds):
    if not creds.refresh_token:
        raise SystemExit(u"O Google nao devolveu refresh_token. Refaca com prompt=consent.")

    pasta = os.path.dirname(TOKEN)
    if not os.path.isdir(pasta):
        os.makedirs(pasta)
    if os.path.isfile(TOKEN):
        bak = TOKEN + dt.datetime.now().strftime(".bak-%Y%m%d-%H%M")
        shutil.copy2(TOKEN, bak)
        print(u"backup do token velho: %s" % bak)

    corpo = {"normal": {
        "access_token": creds.token,
        "refresh_token": creds.refresh_token,
        "scope": ESCOPO[0],
        "token_type": "Bearer",
        "expiry_date": int((creds.expiry - dt.datetime(1970, 1, 1)).total_seconds() * 1000)
                       if creds.expiry else None,
    }}
    with io.open(TOKEN, "w", encoding="utf-8") as fh:
        fh.write(json.dumps(corpo, indent=2, ensure_ascii=False))
    print(u"\nToken gravado em %s" % TOKEN)
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--testar", action="store_true", help=u"so testa o token atual")
    ap.add_argument("--manual", action="store_true", help=u"imprime o link em vez de abrir o navegador")
    ap.add_argument("--url", help=u"a URL de retorno colada da barra de enderecos")
    a = ap.parse_args()
    if a.testar:
        return 0 if testar() else 1
    if a.manual:
        return 0 if mostrar_url() else 1
    if a.url:
        trocar_por_url(a.url)
    else:
        autorizar()
    print(u"\nConferindo...")
    return 0 if testar() else 1


if __name__ == "__main__":
    sys.exit(main())
