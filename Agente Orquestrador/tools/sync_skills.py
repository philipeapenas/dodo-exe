import os
import shutil
import sys


def sync_skills():
    # Raiz do workspace: tools/ -> Agente Orquestrador/ -> raiz
    current_dir = os.path.dirname(os.path.abspath(__file__))
    workspace_root = os.path.abspath(os.path.join(current_dir, '..', '..'))
    source = os.path.join(workspace_root, '.agents', 'skills')

    # .agents/skills e o master; .claude/skills e o espelho que o Claude Code le.
    target = os.path.join(workspace_root, '.claude', 'skills')

    print(f"Sincronizando skills de {source} para {target}...")

    if not os.path.exists(source):
        print("Erro: pasta de origem nao encontrada.")
        sys.exit(1)

    try:
        shutil.copytree(source, target, dirs_exist_ok=True,
                        ignore=shutil.ignore_patterns('.git', '__pycache__', '*.pyc', '.env', '.env.*'))
        print("Sincronizacao concluida com sucesso!")
    except Exception as e:
        print(f"Erro durante a copia: {e}")
        sys.exit(1)


if __name__ == "__main__":
    sync_skills()
