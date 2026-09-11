import os
import subprocess
import sys

def main():
    print("Configurando repositório pela primeira vez e vinculando ao GitHub...")
    repo_name = sys.argv[1] if len(sys.argv) > 1 else os.path.basename(os.getcwd())
    
    try:
        if not os.path.exists(".git"):
            subprocess.run(["git", "init"], check=True)
            subprocess.run(["git", "branch", "-M", "main"], check=True)
            
        subprocess.run(["git", "add", "."], check=True)
        
        status = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)
        if status.stdout.strip():
            subprocess.run(["git", "commit", "-m", "Initial commit: Project structure via Antigravity"], check=False)
        
        # Usa o GitHub CLI para criar o repositório e forçar o push
        print(f"Criando repositório '{repo_name}' no GitHub...")
        subprocess.run(["gh", "repo", "create", repo_name, "--private", "--source=.", "--remote=origin", "--push"], check=True)
        
        print("✅ Projeto vinculado ao GitHub com sucesso!")
        print("💡 Próximo passo: Vá ao painel da Vercel, clique em 'Add New Project' e importe este repositório do GitHub. Os próximos deploys serão automáticos.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro durante a vinculação: {e}")
        print("Certifique-se de que o GitHub CLI (gh) está instalado e autenticado (rode 'gh auth login' no terminal).")
        sys.exit(1)

if __name__ == "__main__":
    main()
