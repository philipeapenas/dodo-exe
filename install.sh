#!/usr/bin/env sh
# Instala o workspace Dodo.exe nesta pasta: monta o Vault a partir do modelo e
# sincroniza as skills. Pode rodar quantas vezes quiser: nada que ja exista no
# Vault e sobrescrito.
#
# Uso:  sh install.sh            instala
#       sh install.sh --dry-run  mostra o que faria, sem escrever
set -e

DIR="$(cd "$(dirname "$0")" && pwd)"
INSTALADOR="$DIR/.agents/skills/instalador-expert/tools/instalar.py"

if [ ! -f "$INSTALADOR" ]; then
    echo "ERRO: nao achei $INSTALADOR. Rode install.sh de dentro da pasta do repositorio." >&2
    exit 1
fi

for PY in python3 python; do
    if command -v "$PY" >/dev/null 2>&1 && \
       "$PY" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 8) else 1)' 2>/dev/null; then
        exec "$PY" "$INSTALADOR" "$@"
    fi
done

echo "ERRO: precisa de Python 3.8 ou mais novo." >&2
exit 1
