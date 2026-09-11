# -*- coding: utf-8 -*-
"""Instalador do workspace Dodo.exe - a parte mecanica.

A conversa (quem voce e, quais operacoes, qual proposito) e da skill
`instalador-expert`. Este script faz so o que nao precisa de julgamento:

  1. Confere Python, Git e Node.
  2. Cria `Vault/` a partir de `vault-modelo/`, copiando SO o que falta.
     Nada que ja exista no Vault e sobrescrito: rodar de novo e seguro.
  3. Cria a primeira nota da semana, se a pasta Semana estiver vazia.
  4. Cria a pasta de cada operacao pedida com --op, e a secao dela em Ativos.
  5. Roda o sync das skills (.agents -> .claude) e do roteador
     (CLAUDE.md -> AGENTS.md).
  6. Diz se cada IDE esta pronta: Claude Code (CLAUDE.md + .claude/skills),
     Codex e Antigravity (AGENTS.md + .agents/skills).

Uso:
  python instalar.py                      instala (ou completa uma instalacao)
  python instalar.py --dry-run            mostra o que faria, sem escrever
  python instalar.py --op "Loja" --op "Consultoria"
  python instalar.py --verificar          so diz em que estado a instalacao esta

Codigo de saida do --verificar:
  0 instalado e com Identidade preenchida
  2 Vault/ nao existe
  3 Vault/ existe, mas a Identidade ainda e o modelo de fabrica
"""
import argparse
import datetime as dt
import io
import os
import shutil
import subprocess
import sys

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except AttributeError:
        pass

# tools/ -> instalador-expert/ -> skills/ -> .agents (ou .claude)/ -> raiz
RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
MODELO = os.path.join(RAIZ, "vault-modelo")
VAULT = os.path.join(RAIZ, "Vault")
SEMANA_DIR = os.path.join(VAULT, "Vida Pessoal", "Semana")
IDENTIDADE = os.path.join(VAULT, "Vida Pessoal", "Identidade.md")
ATIVOS = os.path.join(VAULT, "Vida Pessoal", "Ativos.md")
OPERACOES = os.path.join(VAULT, u"Operações")
MODELO_SEMANA = os.path.join(os.path.dirname(__file__), "modelos", "Semana.md")
TOOLS_ORQ = os.path.join(RAIZ, "Agente Orquestrador", "tools")

# (IDE, arquivo de instrucoes que ela le, pasta de skills que ela le)
IDES = (
    (u"Claude Code", "CLAUDE.md", ".claude/skills"),
    (u"Codex e Antigravity", "AGENTS.md", ".agents/skills"),
)

MARCA_MODELO = u"[!modelo]"
PASTAS_DA_OP = (u"Decisões estratégicas", u"Planos", u"Processos", u"Material", u"Projetos")
IGNORAR = (".gitkeep",)

SECAO_EXEMPLO_ATIVOS = (
    u"## Nome da operação\n"
    u"Uma frase sobre o que ela vende e pra quem.\n\n"
    u"- Decisões estratégicas:\n\n"
    u"- Projetos:\n"
)


def rel(caminho):
    return os.path.relpath(caminho, RAIZ)


def conferir_requisitos():
    """Python e obrigatorio; Git e Node so avisam, porque o vault funciona sem eles."""
    if sys.version_info < (3, 8):
        print(u"ERRO: precisa de Python 3.8 ou mais novo (achei %d.%d)." % sys.version_info[:2])
        sys.exit(1)
    print(u"Python %d.%d: ok" % sys.version_info[:2])
    for prog, motivo in (("git", u"versionar e receber atualizacoes"),
                         ("node", u"subir projeto com npm run dev")):
        print(u"%s: %s" % (prog, u"ok" if shutil.which(prog) else u"NAO ENCONTRADO (serve pra %s)" % motivo))


def copiar_modelo(dry_run):
    """Copia do vault-modelo so o que falta no Vault. Devolve (criados, mantidos)."""
    if not os.path.isdir(MODELO):
        print(u"ERRO: pasta %s nao encontrada. O repositorio esta completo?" % rel(MODELO))
        sys.exit(1)
    criados, mantidos = [], []
    for pasta, subpastas, arquivos in os.walk(MODELO):
        destino_pasta = os.path.join(VAULT, os.path.relpath(pasta, MODELO))
        if not os.path.isdir(destino_pasta) and not dry_run:
            os.makedirs(destino_pasta)
        for nome in arquivos:
            if nome in IGNORAR:
                continue
            destino = os.path.join(destino_pasta, nome)
            if os.path.exists(destino):
                mantidos.append(destino)
                continue
            criados.append(destino)
            if not dry_run:
                shutil.copy2(os.path.join(pasta, nome), destino)
    return criados, mantidos


def segunda_desta_semana(hoje=None):
    hoje = hoje or dt.date.today()
    return hoje - dt.timedelta(days=hoje.weekday())


def criar_primeira_semana(dry_run):
    """Cria 'Semana DD-MM-AA.md' da semana atual, so se nao houver nenhuma nota de semana."""
    if os.path.isdir(SEMANA_DIR) and any(
            n.startswith("Semana ") and n.endswith(".md") for n in os.listdir(SEMANA_DIR)):
        return None
    data = segunda_desta_semana().strftime("%d-%m-%y")
    destino = os.path.join(SEMANA_DIR, u"Semana %s.md" % data)
    if not dry_run:
        texto = io.open(MODELO_SEMANA, encoding="utf-8").read().replace(u"{{DATA}}", data)
        if not os.path.isdir(SEMANA_DIR):
            os.makedirs(SEMANA_DIR)
        io.open(destino, "w", encoding="utf-8", newline="\n").write(texto)
    return destino


def nome_da_op(bruto):
    nome = bruto.strip()
    if nome.upper().startswith("OP "):
        nome = nome[3:].strip()
    if not nome or any(c in nome for c in u'\\/:*?"<>|'):
        print(u"ERRO: nome de operacao invalido: %r" % bruto)
        sys.exit(1)
    return nome


def criar_operacao(bruto, dry_run):
    """Pasta da OP no esqueleto padrao e a secao dela em Ativos. Idempotente."""
    nome = nome_da_op(bruto)
    raiz_op = os.path.join(OPERACOES, u"OP %s" % nome)
    novas = [os.path.join(raiz_op, p) for p in PASTAS_DA_OP
             if not os.path.isdir(os.path.join(raiz_op, p))]
    if not dry_run:
        for p in novas:
            os.makedirs(p)

    secao_nova = False
    if os.path.isfile(ATIVOS) or dry_run:
        texto = io.open(ATIVOS, encoding="utf-8").read() if os.path.isfile(ATIVOS) else u""
        cabecalho = u"## %s\n" % nome
        if cabecalho not in texto:
            secao_nova = True
            bloco = (u"## %s\nUma frase sobre o que ela vende e pra quem.\n\n"
                     u"- Decisões estratégicas:\n\n- Projetos:\n") % nome
            if SECAO_EXEMPLO_ATIVOS in texto:
                # Primeira operacao real: sai o exemplo e o aviso de modelo junto.
                texto = texto.replace(SECAO_EXEMPLO_ATIVOS, bloco)
                texto = u"".join(l for l in texto.splitlines(True)
                                 if not l.startswith(u"> " + MARCA_MODELO))
                texto = texto.replace(u"\n\n\n", u"\n\n")
            else:
                texto = texto.rstrip(u"\n") + u"\n\n" + bloco
            if not dry_run:
                io.open(ATIVOS, "w", encoding="utf-8", newline="\n").write(texto)
    return nome, novas, secao_nova


def rodar_sync(dry_run):
    for script in ("sync_skills.py", "sync_orchestrators.py"):
        caminho = os.path.join(TOOLS_ORQ, script)
        if dry_run:
            print(u"  rodaria %s" % rel(caminho))
            continue
        # Sem o flush, a saida do sync aparece antes do que este script ja imprimiu.
        sys.stdout.flush()
        r = subprocess.run([sys.executable, caminho], cwd=RAIZ)
        if r.returncode != 0:
            print(u"ERRO: %s saiu com codigo %d." % (script, r.returncode))
            sys.exit(1)


def contar_skills(pasta):
    raiz = os.path.join(RAIZ, pasta)
    if not os.path.isdir(raiz):
        return 0
    return sum(1 for d in os.listdir(raiz) if os.path.isfile(os.path.join(raiz, d, "SKILL.md")))


def prontidao_ides():
    """Uma linha por IDE. Pronta = tem o arquivo de instrucoes e o mesmo time de skills do master."""
    master = contar_skills(".agents/skills")
    linhas = []
    for ide, instrucoes, pasta in IDES:
        tem_instrucoes = os.path.isfile(os.path.join(RAIZ, instrucoes))
        n = contar_skills(pasta)
        if not tem_instrucoes:
            linhas.append(u"  %-20s FALTA o %s (rode o instalador de novo)" % (ide, instrucoes))
        elif n == 0 or n != master:
            linhas.append(u"  %-20s skills fora de sincronia: %d de %d (rode o instalador de novo)"
                          % (ide, n, master))
        else:
            linhas.append(u"  %-20s pronto: %s + %d skills em %s" % (ide, instrucoes, n, pasta))
    return linhas


def estado():
    if not os.path.isdir(VAULT):
        return 2, u"Vault/ nao existe: o workspace ainda nao foi instalado."
    if not os.path.isfile(IDENTIDADE):
        return 2, u"Vault/ existe, mas sem Vida Pessoal/Identidade.md."
    if MARCA_MODELO in io.open(IDENTIDADE, encoding="utf-8").read():
        return 3, u"Vault/ existe, mas a Identidade ainda e o modelo de fabrica."
    return 0, u"Instalado e com Identidade preenchida."


def main():
    ap = argparse.ArgumentParser(description=u"Instalador do workspace Dodo.exe")
    ap.add_argument("--dry-run", action="store_true", help=u"mostra o que faria, sem escrever")
    ap.add_argument("--op", action="append", default=[], metavar="NOME",
                    help=u"cria a pasta e a secao em Ativos de uma operacao (repita a opcao)")
    ap.add_argument("--verificar", action="store_true", help=u"so informa o estado da instalacao")
    ap.add_argument("--sem-sync", action="store_true", help=u"nao roda os scripts de sync")
    a = ap.parse_args()

    if a.verificar:
        codigo, msg = estado()
        print(msg)
        print(u"\n".join(prontidao_ides()))
        return codigo

    print(u"Workspace: %s%s\n" % (RAIZ, u"  (SIMULACAO)" if a.dry_run else u""))
    conferir_requisitos()

    criados, mantidos = copiar_modelo(a.dry_run)
    print(u"\nVault: %d arquivo(s) criado(s), %d ja existiam e ficaram intocados."
          % (len(criados), len(mantidos)))

    semana = criar_primeira_semana(a.dry_run)
    if semana:
        print(u"Primeira nota da semana: %s" % rel(semana))

    for bruto in a.op:
        nome, novas, secao_nova = criar_operacao(bruto, a.dry_run)
        print(u"Operacao '%s': %d pasta(s) nova(s)%s" % (
            nome, len(novas), u", secao criada em Ativos" if secao_nova else u", secao em Ativos ja existia"))

    for pasta in (os.path.join(RAIZ, "Projetos", "Dominio"), os.path.join(RAIZ, "Projetos", "Localhost")):
        if not os.path.isdir(pasta) and not a.dry_run:
            os.makedirs(pasta)

    if not a.sem_sync:
        print(u"\nSync:")
        rodar_sync(a.dry_run)

    if a.dry_run:
        print(u"\nSIMULACAO: nada foi escrito.")
        return 0

    print(u"\nIDEs:")
    print(u"\n".join(prontidao_ides()))

    codigo, msg = estado()
    print(u"\n%s" % msg)
    if codigo == 3:
        print(u"Proximo passo: abra esta pasta no Claude Code, no Codex ou no Antigravity e diga\n"
              u"\"instala o Dodo.exe\". A instalador-expert conversa com voce e preenche a Identidade.")
    print(u"Abra a pasta Vault/ como vault no Obsidian.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
