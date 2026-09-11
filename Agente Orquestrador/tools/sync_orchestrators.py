"""
Sync Orchestrators - CLAUDE.md como master dos demais orquestradores
====================================================================
Gera o AGENTS.md (lido pelo Codex e pelo Antigravity) a partir do CLAUDE.md.

Uso: python "Agente Orquestrador/tools/sync_orchestrators.py"

Por que so o AGENTS.md: o Antigravity le o AGENTS.md E o GEMINI.md da raiz.
Gerar os dois faria ele carregar o roteador duas vezes. O Codex le so o
AGENTS.md, entao um arquivo atende as duas IDEs.

Por que cada troca e verificada:
Uma versao anterior procurava uma ancora que deixou de existir quando os
cabecalhos foram reescritos. Como str.replace nao reclama quando nao acha nada,
o script seguia imprimindo sucesso enquanto o arquivo gerado dizia ao outro
runtime que ele era o Claude Code. Agora toda ancora e conferida e o script
morre se alguma sumir.
"""

import os
import sys
from datetime import datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
WORKSPACE_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", ".."))
CLAUDE_PATH = os.path.join(WORKSPACE_ROOT, "CLAUDE.md")

# Cada alvo e um arquivo gerado, com o nome do runtime que ele instrui.
ALVOS = {
    "AGENTS.md": "Codex e Antigravity",
}

TITULO = "# Dodo.exe Workspace - System Prompt & Skill Router ({runtime})"
WORKFLOW = "## Workflow de Execucao do {runtime}"
NOTA_DE_SYNC = "## Nota de Sync"

NOTA_GERADA = """## Nota de Sync

Este arquivo (`{alvo}`) e **gerado automaticamente** a partir do `CLAUDE.md`, que
e o master. **NUNCA** edite este arquivo manualmente - qualquer alteracao aqui e
descartada no proximo sync. Edite o `CLAUDE.md` e rode:

```
python "Agente Orquestrador/tools/sync_orchestrators.py"
```

(Conforme **Regra 6** - Automacao.)
"""


def trocar(texto, antigo, novo, alvo):
    """Troca uma ancora unica, ou aborta dizendo qual ancora sumiu."""
    ocorrencias = texto.count(antigo)
    if ocorrencias != 1:
        print(f"ERRO gerando {alvo}: esperava 1 ocorrencia da ancora abaixo no "
              f"CLAUDE.md, achei {ocorrencias}.")
        print(f"  ancora: {antigo!r}")
        print("  O CLAUDE.md foi reescrito? Ajuste as ancoras neste script.")
        sys.exit(1)
    return texto.replace(antigo, novo)


def gerar(master, alvo, runtime):
    conteudo = trocar(master,
                      TITULO.format(runtime="Claude Code"),
                      TITULO.format(runtime=runtime), alvo)
    conteudo = trocar(conteudo,
                      WORKFLOW.format(runtime="Claude Code"),
                      WORKFLOW.format(runtime=runtime), alvo)

    # A Nota de Sync do master fala com quem edita o master. No arquivo gerado
    # ela precisa dizer o oposto: nao edite aqui. Troca a secao inteira, do
    # cabecalho ate o fim do arquivo.
    if conteudo.count(NOTA_DE_SYNC) != 1:
        print(f"ERRO gerando {alvo}: nao achei a secao '{NOTA_DE_SYNC}' "
              "no CLAUDE.md.")
        sys.exit(1)
    corte = conteudo.index(NOTA_DE_SYNC)
    return conteudo[:corte] + NOTA_GERADA.format(alvo=alvo)


def sync():
    if not os.path.exists(CLAUDE_PATH):
        print(f"ERRO: CLAUDE.md nao encontrado em {CLAUDE_PATH}")
        sys.exit(1)

    with open(CLAUDE_PATH, "r", encoding="utf-8") as f:
        master = f.read()

    # Gera tudo antes de escrever qualquer coisa: se uma ancora sumiu, nenhum
    # orquestrador e sobrescrito pela metade.
    gerados = {alvo: gerar(master, alvo, runtime)
               for alvo, runtime in ALVOS.items()}

    # newline="\n": no Windows o modo texto grava CRLF, e o git de quem clonou passa a
    # acusar os dois arquivos como modificados, travando o git pull das atualizacoes.
    for alvo, conteudo in gerados.items():
        with open(os.path.join(WORKSPACE_ROOT, alvo), "w", encoding="utf-8", newline="\n") as f:
            f.write(conteudo)

    print("Sincronizacao concluida com sucesso!")
    for alvo, conteudo in gerados.items():
        print(f"   CLAUDE.md -> {alvo} ({ALVOS[alvo]}), {len(conteudo)} bytes")
    print(f"   Timestamp: {datetime.now().isoformat()}")


if __name__ == "__main__":
    sync()
