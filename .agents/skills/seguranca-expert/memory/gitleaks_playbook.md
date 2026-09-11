# Gitleaks Playbook - Motor de Deteccao de Segredos

**Owner:** seguranca-expert | **Origem:** treinamento inicial (new_hire 2026-07-02)

Este playbook e o conhecimento tecnico da seguranca-expert. Descreve por que o gitleaks foi escolhido, como rodar working-tree e historico git, o ruleset customizado do ecossistema Dodo e como classificar severidade.

---

## Por que gitleaks (nao trufflehog, nao scanner de vulnerabilidade)

Pesquisa de mercado (07/2026): gitleaks e trufflehog sao os dois padroes de industria para deteccao de segredos hardcoded.

- **gitleaks**: regex + deteccao de entropia, single binary, sem rede, varre working tree E qualquer commit do historico git nativamente (`gitleaks detect`). Ideal para o caso "95% dos padroes conhecidos", rapido e deterministico. Config em TOML permite adicionar regras proprias sem tocar no motor.
- **trufflehog**: adiciona VERIFICACAO AO VIVO (chama a API do provedor pra confirmar se a chave ainda esta ativa) e cobre mais backends (S3, GCP, etc). Mais poderoso mas mais pesado, exige rede e mais engenharia.

**Decisao de escopo:** deteccao ESTATICA (working tree + historico), sem investigacao de intrusao nem verificacao ao vivo. gitleaks e a ferramenta certa pra esse escopo. Se o fundador quiser saber se uma chave vazada AINDA esta ativa, isso e um upskill futuro na direcao do trufflehog: nao presuma, pergunte antes.

Fontes da pesquisa: comparativos Rafter/Aikido/Secrails/Jit.io (07/2026) e discussao r/devsecops, consenso: gitleaks pra varredura rapida de padroes conhecidos + historico; trufflehog quando precisa validar se a credencial ainda funciona.

---

## Instalacao (Windows) - responsabilidade do dev-expert na Fase 1 de tooling

Checar primeiro: `gitleaks version` (pode ja estar disponivel via scoop/choco/go em alguma maquina).

Opcoes de instalacao (validar qual esta disponivel no ambiente real antes de escolher):
1. **Scoop:** `scoop install gitleaks`
2. **Go:** `go install github.com/gitleaks/gitleaks/v8@latest` (exige Go instalado)
3. **Binario direto:** baixar o release `.zip` mais recente de `github.com/gitleaks/gitleaks/releases` (asset `gitleaks_<versao>_windows_x64.zip`) e extrair `gitleaks.exe` para `.agents/skills/seguranca-expert/tools/bin/gitleaks.exe` (vendorizado, sem depender do PATH do sistema).

> Vendorizar o binario em `tools/bin/` (opcao 3) e mais robusto pra nao depender de instalacao global, segue o mesmo espirito de "vendorizar fonte/emoji" usado no motion-expert (Regra 6, reuso e determinismo).

---

## Comandos de Deteccao

**Atencao:** os flags exatos podem variar por versao do gitleaks. O dev-expert DEVE confirmar com `gitleaks --help` / `gitleaks detect --help` no binario real instalado e ajustar antes de finalizar o wrapper (nao copiar cegamente: calibrar contra o binario real).

### 1. Working tree (estado atual dos arquivos, sem historico)
```
gitleaks detect --no-git --source "<caminho-do-projeto>" --config "dodo-rules.toml" --report-path "working_tree_report.json" -v
```
(Em versoes mais novas pode existir o subcomando dedicado `gitleaks dir <caminho>`: usar se disponivel, e mais explicito.)

### 2. Historico git completo (todos os commits, inclusive os que ja foram "limpos" do working tree)
```
gitleaks detect --source "<caminho-do-projeto>" --log-opts="--all" --config "dodo-rules.toml" --report-path "git_history_report.json" -v
```
Isso e CRITICO: o caso classico e o working tree limpo enquanto o historico dos commits continua com as chaves originais. Rodar SEMPRE os dois comandos, nunca so o working tree.

### 3. Se o projeto nao for um repo git (ex: pasta solta em `Projetos/Localhost/` sem `git init`)
Rodar so o comando de working tree (nao ha historico pra varrer). Reportar isso explicitamente no relatorio final ("projeto sem controle de versao, sem historico a auditar").

---

## Ruleset customizado Dodo (`dodo-rules.toml`)

Alem do ruleset default do gitleaks (que ja cobre AWS, GitHub, Slack, Stripe, chaves genericas por entropia, etc), o ecossistema Dodo usa servicos que precisam de regras proprias. Confianca de cada regra abaixo, para o dev-expert priorizar:

| Servico | Formato conhecido | Confianca | Regra |
|---|---|---|---|
| Telegram Bot Token | `\d{8,10}:[A-Za-z0-9_-]{35}` | Alta (formato documentado publicamente pelo BotFather) | Regex direta |
| Supabase JWT (service_role/anon) | `eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}` | Alta (JWT padrao, 3 partes separadas por ponto) | Regex direta + contexto: procurar proximo a `SUPABASE_SERVICE_ROLE_KEY` / `SUPABASE_ANON_KEY` / `service_role` no texto pra reduzir falso positivo |
| Google Service Account JSON | chave privada no campo `"private_key"`, com o cabecalho PEM de chave privada | Alta (formato PEM padrao) | Regex no padrao PEM + contexto `"type": "service_account"` |
| AWS Access Key | `AKIA[0-9A-Z]{16}` | Alta (ja no default ruleset do gitleaks, so confirmar que esta ativo) | Ja coberta |
| GitHub Token | `gh[pousr]_[A-Za-z0-9]{36,}` | Alta (ja no default ruleset do gitleaks) | Ja coberta |
| PushinPay API Token | formato exato NAO confirmado ainda | Baixa | Nao inventar regex - na primeira execucao real, se aparecer um token da PushinPay em texto claro, capturar o formato observado e devolver pro seguranca-expert atualizar esta tabela via skill-expert |
| ElevenLabs API Key | formato exato NAO confirmado ainda (historicamente string hex, sem prefixo fixo) | Baixa | Mesma politica acima - depender da deteccao por ENTROPIA generica do gitleaks ate confirmar um padrao estavel |
| RunningHub / Firecrawl API Key | formato exato NAO confirmado ainda | Baixa | Mesma politica acima |
| Vercel Token | sem prefixo distintivo conhecido | Baixa | Depender de deteccao por entropia generica + contexto (`VERCEL_TOKEN=`) |

**Regra de ouro do ruleset:** regras de ALTA confianca viram regex explicita no `dodo-rules.toml` (baixo falso-positivo, alta certeza). Regras de BAIXA confianca NAO devem virar regex inventada (risco de nunca disparar OU de gerar ruido) - confiar na deteccao por entropia generica que o gitleaks ja faz por padrao, e quando um achado real desses servicos aparecer, atualizar esta tabela com o formato confirmado (via `help` ao skill-expert, que e quem edita este arquivo).

O arquivo fisico `dodo-rules.toml` (sintaxe TOML valida do gitleaks, com os `[[rules]]` blocks) e responsabilidade do dev-expert construir em `tools/dodo-rules.toml`, usando esta tabela como spec (Regra 8 das regras_de_ouro - a seguranca-expert especifica, o dev-expert coda/configura).

---

## Classificacao de Severidade

| Severidade | Criterio |
|---|---|
| **Critico** | Achado no WORKING TREE ATUAL (chave provavelmente ainda em uso) de um projeto em `Projetos/Dominio/` (repo publico proprio no GitHub) |
| **Alto** | Achado SO no historico git (ja removido do working tree, mas o repo e publico/compartilhado) OU achado no working tree de um projeto `Projetos/Localhost/` (privado, dentro do dodo-company) |
| **Medio** | Achado no historico de um projeto `Localhost` (privado) OU achado em arquivo que deveria estar no `.gitignore` mas nao esta (risco preventivo, nao vazamento confirmado) |
| **Baixo** | Achado por entropia generica sem confirmacao de formato conhecido (pode ser falso positivo - hash, UUID, id nao-secreto) |

Descarte (nao reportar como achado real, so mencionar se relevante): placeholders obvios (`<SEU_TOKEN_AQUI>`, `xxx`, `example_key_123`), valores em arquivos de documentacao/README claramente ilustrativos.

---

## Checagem de .gitignore

Para cada projeto auditado, conferir se o `.gitignore` cobre (lista minima esperada, ver Regra 9 e Regra 20 das regras_de_ouro):
- `.env`, `.env.local`, `.env.*.local`
- `credentials.json`, `*.session` (arquivos de sessao Telethon/Telegram)
- `node_modules/`, `dist/`, `.vercel/` (nao sao segredo mas indicam repo mal higienizado)

Se um arquivo de segredo estiver sendo rastreado pelo git (`git ls-files | grep .env` retorna algo), isso e achado CRITICO independente de ter disparado alguma regex - o arquivo inteiro esta exposto.

---

## Formato do Relatorio Final

Markdown simples, nunca JSON cru no chat (Regra de Otimizacao de Tokens):

```
## Auditoria de Seguranca - <Nome do Projeto> (<data>)

### Achados
| Severidade | Arquivo | Linha | Tipo | So no historico? |
|---|---|---|---|---|
| Critico | checkout.html | 42 | Supabase service_role JWT | Nao (working tree) |
| Alto | (commit 6725bb7) config.js | 8 | Telegram Bot Token | Sim (so historico) |

### Cobertura .gitignore
- [ ] .env NAO esta no .gitignore (RISCO)
- [x] credentials.json coberto

### Recomendacoes
1. Rotacionar a service_role key do Supabase (projeto <nome>) - AGUARDANDO APROVACAO DO FUNDADOR para agir.
2. Reescrever o historico do commit 6725bb7 em diante com git filter-repo - operacao DESTRUTIVA, so com aprovacao explicita.
3. Adicionar .env ao .gitignore (nao-destrutivo, pode ser feito pelo dev-expert direto apos confirmacao).
```
