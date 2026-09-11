import os
import subprocess
import sys

def main():
    print("Atualizando deploy via GitHub (Auto-Vercel)...")
    try:
        subprocess.run(["git", "add", "."], check=True)
        # Verifica se há alterações
        status = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)
        if not status.stdout.strip():
            print("Nenhuma alteração para commitar. O deploy já está atualizado no GitHub.")
            return

        commit_msg = "feat: auto-update deploy via vercel-expert"
        if len(sys.argv) > 1:
            commit_msg = " ".join(sys.argv[1:])
            
        subprocess.run(["git", "commit", "-m", commit_msg], check=True)
        subprocess.run(["git", "push", "origin", "main"], check=True)
        print("✅ Deploy disparado com sucesso na Vercel via GitHub Push!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro durante o deploy: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
