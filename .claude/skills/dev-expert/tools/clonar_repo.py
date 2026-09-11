#!/usr/bin/env python3
"""Clona (ou atualiza) um repositorio Git dentro do workspace Dodo.exe.

Motivo de existir: ser colaborador de um repo no GitHub e permissao de push,
nao e ter o codigo na maquina. Pra mexer e preciso uma copia local. Este script
padroniza esse passo e evita os dois erros classicos: clonar duas vezes o mesmo
repo em pastas diferentes, e clonar por cima de uma pasta que ja tem conteudo.

Uso:
    python clonar_repo.py <url>
    python clonar_repo.py <url> --nome meu-projeto
    python clonar_repo.py <url> --destino "Projetos/Dominio" --branch dev
    python clonar_repo.py <url> --dry-run

Comportamento:
    - Destino padrao: <workspace>/Projetos/Localhost/<nome-do-repo>
    - Se a pasta ja existe e e o MESMO repo: roda `git pull --ff-only` em vez
      de falhar (idempotente).
    - Se a pasta ja existe e e OUTRO repo, ou tem conteudo e nao e repo git:
      aborta sem tocar em nada.
    - No fim imprime o estado (branch, ultimo commit) e os proximos passos
      deduzidos da stack (requirements.txt, package.json, arquivos de exemplo).

Codigos de saida: 0 sucesso, 1 erro de uso/ambiente, 2 conflito no destino.
"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path

TIMEOUT_GIT = 600  # clone de repo grande pode demorar; 10 min e teto generoso
DESTINO_PADRAO = "Projetos/Localhost"


def raiz_do_workspace() -> Path:
    """Sobe de tools/ -> dev-expert -> skills -> .agents -> raiz do workspace."""
    return Path(__file__).resolve().parents[4]


def nome_do_repo(url: str) -> str:
    """Deriva o nome da pasta a partir da URL do repo.

    'https://github.com/user/meu-projeto-.git' -> 'meu-projeto'
    'git@github.com:user/Meu_Repo.git'        -> 'Meu_Repo'
    """
    bruto = url.strip().rstrip("/")
    bruto = re.sub(r"\.git$", "", bruto)
    bruto = bruto.split("/")[-1].split(":")[-1]
    # hifen ou underscore solto no fim e quase sempre erro de digitacao de quem
    # criou o repo (ex: 'meu-projeto-'); nao carrega isso pra pasta local
    bruto = bruto.rstrip("-_")
    return bruto


def git_disponivel() -> bool:
    return shutil.which("git") is not None


def rodar(args: list[str], cwd: Path | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(
        args,
        cwd=str(cwd) if cwd else None,
        capture_output=True,
        text=True,
        timeout=TIMEOUT_GIT,
    )


def origin_de(pasta: Path) -> str | None:
    """URL do remote origin. None se a pasta nao e repo git; "" se e repo sem origin."""
    if not (pasta / ".git").exists():
        return None
    r = rodar(["git", "remote", "get-url", "origin"], cwd=pasta)
    if r.returncode != 0:
        return ""
    return r.stdout.strip()


def mesma_origem(a: str, b: str) -> bool:
    """Compara URLs ignorando .git final, barra final, caixa e forma ssh/https."""

    def normaliza(u: str) -> str:
        u = u.strip().rstrip("/").lower()
        u = re.sub(r"\.git$", "", u)
        u = re.sub(r"^git@([^:]+):", r"https://\1/", u)
        u = re.sub(r"^https?://", "", u)
        return u

    return normaliza(a) == normaliza(b)


def pasta_vazia(pasta: Path) -> bool:
    return not any(pasta.iterdir())


def resumo_do_repo(pasta: Path) -> None:
    """Imprime branch, ultimo commit e proximos passos deduzidos da stack."""
    branch = rodar(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=pasta)
    ultimo = rodar(["git", "log", "-1", "--oneline"], cwd=pasta)

    print()
    print("Estado do repositorio:")
    print(f"  pasta   : {pasta}")
    if branch.returncode == 0:
        print(f"  branch  : {branch.stdout.strip()}")
    if ultimo.returncode == 0 and ultimo.stdout.strip():
        print(f"  ultimo  : {ultimo.stdout.strip()}")

    passos: list[str] = []
    if (pasta / "requirements.txt").exists():
        passos.append("pip install -r requirements.txt")
    if (pasta / "package.json").exists():
        passos.append("npm install")
    if (pasta / "pyproject.toml").exists() and not (pasta / "requirements.txt").exists():
        passos.append("pip install -e .")

    exemplos = [
        n
        for n in (".env.example", ".env.sample", "settings.example.json",
                  "secrets.example.json", "config.example.json")
        if (pasta / n).exists()
    ]
    for exemplo in exemplos:
        real = exemplo.replace(".example", "").replace(".sample", "")
        passos.append(f"copiar {exemplo} para {real} e preencher as credenciais")

    if passos:
        print()
        print("Proximos passos:")
        for p in passos:
            print(f"  - {p}")

    print()
    print("Ciclo de trabalho (colaborador: push vai direto, sem fork nem PR):")
    print("  git pull                       # antes de comecar")
    print("  git add . && git commit -m ... # depois de mexer")
    print("  git push")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Clona ou atualiza um repositorio Git no workspace Dodo.exe."
    )
    parser.add_argument("url", help="URL do repositorio (https ou ssh)")
    parser.add_argument("--nome", help="nome da pasta local (padrao: nome do repo)")
    parser.add_argument(
        "--destino",
        default=DESTINO_PADRAO,
        help=f"pasta pai, relativa a raiz do workspace (padrao: {DESTINO_PADRAO})",
    )
    parser.add_argument("--branch", help="branch especifica a clonar")
    parser.add_argument(
        "--dry-run", action="store_true", help="mostra o que faria, sem escrever nada"
    )
    args = parser.parse_args()

    if not git_disponivel():
        print("ERRO: git nao encontrado no PATH.", file=sys.stderr)
        return 1

    url = args.url.strip()
    if not url:
        print("ERRO: url vazia.", file=sys.stderr)
        return 1

    nome = (args.nome or nome_do_repo(url)).strip()
    if not nome:
        print(
            f"ERRO: nao consegui derivar o nome da pasta de '{url}'. Passe --nome.",
            file=sys.stderr,
        )
        return 1

    pai = (raiz_do_workspace() / args.destino).resolve()
    alvo = pai / nome

    print(f"Repositorio : {url}")
    print(f"Destino     : {alvo}")
    if args.branch:
        print(f"Branch      : {args.branch}")

    # Caso 1: o destino ja existe
    if alvo.exists():
        if not alvo.is_dir():
            print(f"ERRO: '{alvo}' existe e nao e uma pasta.", file=sys.stderr)
            return 2

        origem = origin_de(alvo)

        if origem is None:
            if pasta_vazia(alvo):
                print("Pasta existe e esta vazia: segue com o clone dentro dela.")
            else:
                print(
                    f"ERRO: '{alvo}' ja existe, tem conteudo e nao e um repo git. "
                    f"Nao vou escrever por cima.",
                    file=sys.stderr,
                )
                return 2
        elif origem and mesma_origem(origem, url):
            print("Ja clonado, mesmo origin. Atualizando com git pull --ff-only.")
            if args.dry_run:
                print("[dry-run] nada foi executado.")
                return 0
            r = rodar(["git", "pull", "--ff-only"], cwd=alvo)
            print(r.stdout.strip() or r.stderr.strip())
            if r.returncode != 0:
                print(
                    "AVISO: o pull nao passou limpo. Provavel divergencia local; "
                    "resolva na mao antes de continuar.",
                    file=sys.stderr,
                )
                return 2
            resumo_do_repo(alvo)
            return 0
        else:
            print(
                f"ERRO: '{alvo}' ja e um repo git de outra origem:\n"
                f"       existente: {origem or '(sem origin)'}\n"
                f"       pedido   : {url}\n"
                f"Use --nome pra escolher outra pasta.",
                file=sys.stderr,
            )
            return 2

    # Caso 2: clonar do zero
    if args.dry_run:
        print("[dry-run] clonaria agora. Nada foi escrito.")
        return 0

    try:
        pai.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        print(f"ERRO: nao consegui criar '{pai}': {e}", file=sys.stderr)
        return 1

    comando = ["git", "clone"]
    if args.branch:
        comando += ["--branch", args.branch]
    comando += [url, str(alvo)]

    print("Clonando...")
    try:
        r = rodar(comando)
    except subprocess.TimeoutExpired:
        print(f"ERRO: o clone passou de {TIMEOUT_GIT}s e foi abortado.", file=sys.stderr)
        return 1

    if r.returncode != 0:
        print(r.stderr.strip(), file=sys.stderr)
        print(
            "ERRO: o clone falhou. Se o repo e privado, confirme se voce esta "
            "autenticado no git (gh auth login ou o credential manager do Windows).",
            file=sys.stderr,
        )
        return 1

    print("Clone concluido.")
    resumo_do_repo(alvo)
    return 0


if __name__ == "__main__":
    sys.exit(main())
