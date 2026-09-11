# Instalar o Dodo.exe

Este arquivo tem dois publicos: cole ele (ou o link deste repositorio) no seu assistente de codigo pra ele executar, ou siga o passo a passo manual no fim.

---

## Instrucoes pra IA (Claude Code, Codex, Antigravity ou similar)

Voce e um assistente de codigo. O usuario quer instalar o workspace Dodo.exe. Siga estes passos, na ordem.

**Passo 1 - Confirme que esta na raiz do repositorio.**
A pasta atual precisa ter `CLAUDE.md`, `vault-modelo/` e `.agents/skills/instalador-expert/`. Se nao tiver:
- Se o usuario so passou a URL, clone: `git clone <URL> dodo-exe` e entre na pasta.
- Se o repositorio ja esta em outro caminho, pergunte qual e. Nao assuma.

**Passo 2 - Veja em que estado a instalacao esta.**
```
python .agents/skills/instalador-expert/tools/instalar.py --verificar
```
Codigo 0: ja instalado, pergunte o que o usuario quer mudar. Codigo 2 ou 3: siga.

**Passo 3 - Leia e siga a skill instaladora.**
Leia `.agents/skills/instalador-expert/SKILL.md` e `.agents/skills/instalador-expert/memory/roteiro_de_instalacao.md` e conduza a instalacao como eles mandam: rodar o instalador, conversar com o usuario uma pergunta por vez, escrever a Identidade com a palavra dele, gerar a semana.

**Passo 4 - Confira.**
- `instalar.py --verificar` sai com codigo 0.
- `Vault/Vida Pessoal/Identidade.md` nao tem mais o aviso `> [!modelo]`.
- Existe uma nota em `Vault/Vida Pessoal/Semana/`.
- `.claude/skills/` tem as mesmas skills de `.agents/skills/`, e o `--verificar` mostra as tres IDEs como `pronto` (Claude Code; Codex e Antigravity).

Se algum item falhar, releia a saida do instalador antes de dizer que terminou.

**Passo 5 - Entregue.** Diga ao usuario o que foi criado, o que ficou pendente e como abrir `Vault/` no Obsidian (Abrir pasta como vault).

---

## Passo a passo manual (sem IA)

1. Clone o repositorio.
2. Rode o instalador: `powershell -ExecutionPolicy Bypass -File install.ps1` no Windows, ou `sh install.sh` no Mac, Linux ou Git Bash.
3. Abra `Vault/Vida Pessoal/Identidade.md` e preencha: proposito, meta, principios e a rotina mestre. Mantenha os titulos das secoes como estao e apague o aviso `> [!modelo]` do topo.
4. Para cada operacao que voce toca: `python .agents/skills/instalador-expert/tools/instalar.py --op "Nome da operacao"`.
5. No Obsidian, abra a pasta `Vault/` como vault.

---

## Atualizar depois

`git pull` e rode o instalador de novo. Ele so cria o que falta e nunca sobrescreve nada que ja exista no seu `Vault/`.
