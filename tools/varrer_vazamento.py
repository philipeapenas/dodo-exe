# -*- coding: utf-8 -*-
"""Varre o repositorio atras de segredo e de dado pessoal antes de um envio.

Rode antes de TODO push. Silencio (codigo 0) e o criterio de pronto; qualquer
achado sai com codigo 1 e a lista de arquivo:linha.

Dois tipos de padrao:

  * GENERICOS (neste arquivo): formato de segredo que nunca deveria estar num
    repositorio - JWT, chave de API, token de bot, chave privada, arquivo .env,
    endereco IP, e-mail e caminho absoluto de maquina.
  * PESSOAIS (em tools/varredura.local.txt, ignorado pelo git): nomes de
    cliente, de pessoa, de servidor, qualquer coisa que so faz sentido para
    quem esta publicando. Uma expressao regular por linha, '#' comenta. Esse
    arquivo nunca vai pro repositorio, porque a lista em si ja seria o
    vazamento.

Uso:
  python tools/varrer_vazamento.py
  python tools/varrer_vazamento.py --lista outro_arquivo.txt
"""
import argparse
import io
import os
import re
import sys

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except AttributeError:
        pass

RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
LISTA_PADRAO = os.path.join(RAIZ, "tools", "varredura.local.txt")

PASTAS_IGNORADAS = {".git", "Vault", "node_modules", "__pycache__", ".vercel"}
TAMANHO_MAXIMO = 2 * 1024 * 1024

ARQUIVOS_PROIBIDOS = re.compile(
    r"(^\.env($|\.)|\.pem$|\.key$|\.session$|^credentials\.json$|service[_-]?account.*\.json$|"
    r"\.pyc$|\.local\.json$|^secrets?\.(?!example\.)[\w.]+$|^tokens?\.json$|cookies?\.(json|txt)$)",
    re.IGNORECASE)

GENERICOS = [
    ("jwt", re.compile(r"eyJ[A-Za-z0-9_-]{10,}\.eyJ[A-Za-z0-9_-]{10,}")),
    ("chave sk-", re.compile(r"\bsk-(?:ant-|proj-)?[A-Za-z0-9_-]{20,}")),
    ("stripe live", re.compile(r"\b[sr]k_live_[A-Za-z0-9]{10,}")),
    ("github token", re.compile(r"\bgh[pousr]_[A-Za-z0-9]{30,}")),
    ("google api key", re.compile(r"\bAIza[0-9A-Za-z_-]{35}")),
    ("token de bot telegram", re.compile(r"\b\d{8,10}:AA[A-Za-z0-9_-]{30,}")),
    ("chave privada", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
    # Sem digito nem ponto colado dos lados: numero de desenho SVG ("1.45.29.15.46") nao e IP.
    ("endereco ip", re.compile(r"(?<![\d.])(?:\d{1,3}\.){3}\d{1,3}(?![\d.])")),
    ("e-mail", re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b")),
    ("caminho de usuario", re.compile(r"[A-Za-z]:\\+Users\\+[^\\\s\"'`]+", re.IGNORECASE)),
    ("caminho de usuario unix", re.compile(r"/(?:home|Users)/[a-z][\w.-]+/")),
]

# Ocorrencias conhecidas e inofensivas dos padroes genericos.
PERMITIDOS = re.compile(
    r"^(127\.0\.0\.1|0\.0\.0\.0|255\.255\.255\.\d+|noreply@anthropic\.com|"
    r"[\w.+-]+@(?:example|exemplo)\.(?:com|org)|git@github\.com|/home/runner/)$",
    re.IGNORECASE)


def carregar_pessoais(caminho):
    if not os.path.isfile(caminho):
        return []
    padroes = []
    for n, linha in enumerate(io.open(caminho, encoding="utf-8"), 1):
        linha = linha.strip()
        if not linha or linha.startswith("#"):
            continue
        try:
            padroes.append(("pessoal: linha %d da lista" % n, re.compile(linha, re.IGNORECASE)))
        except re.error as e:
            print("AVISO: linha %d da lista pessoal nao e regex valida (%s): ignorada" % (n, e))
    return padroes


def mascarar(texto):
    return texto if len(texto) <= 8 else texto[:4] + "..." + texto[-2:]


def arquivos(inicio):
    for pasta, subpastas, nomes in os.walk(inicio):
        subpastas[:] = [s for s in subpastas if s not in PASTAS_IGNORADAS]
        for nome in nomes:
            yield os.path.join(pasta, nome), nome


def varrer(padroes, inicio):
    achados = []
    for caminho, nome in arquivos(inicio):
        rel = os.path.relpath(caminho, RAIZ)
        if rel == os.path.relpath(LISTA_PADRAO, RAIZ) or nome.endswith(".local.txt"):
            continue
        if ARQUIVOS_PROIBIDOS.search(nome):
            achados.append((rel, 0, "arquivo proibido", nome))
            continue
        if os.path.getsize(caminho) > TAMANHO_MAXIMO:
            continue
        try:
            texto = io.open(caminho, encoding="utf-8").read()
        except (UnicodeDecodeError, OSError):
            continue
        for n, linha in enumerate(texto.splitlines(), 1):
            for rotulo, rx in padroes:
                for m in rx.finditer(linha):
                    if PERMITIDOS.match(m.group(0)):
                        continue
                    achados.append((rel, n, rotulo, mascarar(m.group(0))))
    return achados


def main():
    ap = argparse.ArgumentParser(description="Varredura de segredo e dado pessoal")
    ap.add_argument("pasta", nargs="?", default=RAIZ,
                    help="varre so esta pasta (padrao: o repositorio inteiro)")
    ap.add_argument("--lista", default=LISTA_PADRAO, help="arquivo com os padroes pessoais")
    a = ap.parse_args()

    pessoais = carregar_pessoais(a.lista)
    if not pessoais:
        print("AVISO: sem lista pessoal (%s). So os padroes genericos foram usados."
              % os.path.relpath(a.lista, RAIZ))

    achados = varrer(GENERICOS + pessoais, os.path.abspath(a.pasta))
    if not achados:
        print("Varredura limpa: nenhum achado.")
        return 0

    for rel, n, rotulo, trecho in achados:
        print("%s:%s  [%s]  %s" % (rel, n, rotulo, trecho))
    print("\n%d achado(s). Nada sobe enquanto esta lista nao estiver vazia." % len(achados))
    return 1


if __name__ == "__main__":
    sys.exit(main())
