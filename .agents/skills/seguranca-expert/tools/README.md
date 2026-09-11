# Spec do tooling da seguranca-expert (a implementar pelo dev-expert - Regra 8)

Este arquivo e a especificacao funcional, nao a implementacao. A seguranca-expert define o comportamento esperado; o dev-expert coda.

## O que falta construir

1. **`tools/bin/gitleaks.exe`** - binario vendorizado (ver `memory/gitleaks_playbook.md`, secao Instalacao, pra escolher entre scoop/go/download direto). Confirmar `gitleaks version` antes de seguir.
2. **`tools/dodo-rules.toml`** - ruleset customizado do gitleaks com as regras de ALTA confianca da tabela em `memory/gitleaks_playbook.md` (Telegram Bot Token, Supabase JWT, Google Service Account). NAO inventar regex para as de baixa confianca (PushinPay, ElevenLabs, RunningHub, Firecrawl, Vercel) - deixar pro ruleset default de entropia do gitleaks ate ter um formato confirmado.
3. **`tools/run_scan.py`** - wrapper que:
   - Recebe `--project <caminho>` (obrigatorio) e `--out <caminho-do-relatorio>` (opcional, default stdout).
   - Roda o comando de working tree E o comando de historico git (ver playbook, secao Comandos de Deteccao) usando `dodo-rules.toml`.
   - Se o projeto nao for um repo git, pula a etapa de historico e avisa isso no relatorio.
   - Parseia o JSON de saida do gitleaks (2 relatorios: working tree + historico) e classifica cada achado por severidade conforme a tabela do playbook (usa o caminho do projeto pra saber se e `Projetos/Dominio/` ou `Projetos/Localhost/`).
   - Checa cobertura do `.gitignore` do projeto contra a lista minima esperada (`.env`, `credentials.json`, `*.session`).
   - Roda `git ls-files` no projeto e alerta CRITICO se algum arquivo de segredo esperado (`.env`, `credentials.json`) estiver sendo rastreado pelo git.
   - Imprime/retorna o relatorio final ja no formato Markdown do playbook (nao JSON cru).
   - Reuso obrigatorio (Regra 6): antes de escrever helpers de subprocess/leitura de arquivo do zero, checar se `.agents/skills/motion-expert/tools/finalize_video.py` ou outro tool ja tem um padrao de "rodar comando externo + tratar erro amigavel" reaproveitavel.

## Criterio de sucesso (pra validar antes de entregar)

Rodar `tools/run_scan.py --project "Projetos/Dominio/<algum-projeto-real>"` numa pasta que:
- (a) NAO tenha segredo nenhum -> relatorio "0 achados, .gitignore OK".
- (b) Tenha um segredo de teste plantado deliberadamente no working tree -> relatorio classifica como Critico/Alto corretamente.
- (c) Tenha um segredo so no historico (commitado e depois removido do working tree, ex: um repo de teste local) -> relatorio pega no passo de historico mesmo NAO aparecendo no working tree.

Sem push, sem alteracao de codigo produtivo do projeto auditado - a seguranca-expert e read-only.
