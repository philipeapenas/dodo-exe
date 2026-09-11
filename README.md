# Dodo.exe

O Dodo.exe e a primeira distribuicao do projeto Dodo.IA: um ecossistema portatil de agentes de IA com orquestracao, memoria operacional e Obsidian. Ele e o inicio de um Jarvis pessoal que aprende a estrutura, as operacoes e a forma de decidir de quem instala.

Voce clona, abre no Claude Code, no Codex ou no Antigravity, diz **"instala o Dodo.exe"** e sai com a mesma estrutura que roda uma operacao real: um roteador que manda cada pedido pra skill certa, regras que valem pra todas elas, um protocolo de mensagens pra elas passarem trabalho uma pra outra, e um vault organizado por operacao, tarefa, processo e estudo.

---

## O que vem dentro

**A orquestra**

| Peca | O que faz |
| --- | --- |
| `CLAUDE.md` | O roteador: le o pedido e aponta a skill que resolve. O `AGENTS.md` e gerado a partir dele, entao o mesmo workspace funciona no Codex e no Antigravity |
| `Agente Orquestrador/memory/regras_de_ouro.md` | As regras que valem pra todas as skills: planejar antes de executar, desenho antes do codigo, o vault como fonte da verdade, sem emoji e sem travessao |
| `Agente Orquestrador/Resumo do projeto/messaging_protocol.md` | Como uma skill passa trabalho pra outra, com rastro de quem fez o que |
| `Agente Orquestrador/tools/` | Os scripts de sync (skills, orquestradores, protocolo) e o lancador de `npm run dev` |

**O time (21 skills)**

| Area | Skills |
| --- | --- |
| Direcao | `ceo-dodo` (estrategia e orquestracao), `dodo-ia` (le a sua Identidade e decide como voce decidiria), `instalador-expert` (instala e personaliza o workspace) |
| Engenharia | `dev-expert`, `frontend-expert`, `vercel-expert`, `bot-expert`, `checkout-expert`, `seguranca-expert`, `cinematic-expert`, `clone-site-expert` |
| Operacao e marketing | `assistente-expert` (mantem o vault), `copywriter-expert`, `vitrine-expert`, `estudos-expert`, `processo-expert` |
| Conteudo com IA | `prompt-expert`, `motion-expert`, `voice-expert`, `lipsync-expert` |
| RH | `skill-expert` (cria, treina e contrata skills novas) |

**O vault (`vault-modelo/`)**

A estrutura de pastas e os modelos em branco: `Vida Pessoal` (Identidade, Ativos, Semana, Rotina), `Operações`, `Tarefas`, `Processos`, `Estudos`, `Insights`, `Problemas`, `Recursos`, `Investimentos` e `Canvas`. Na instalacao ele e copiado para `Vault/`, que e seu e nunca sobe pro repositorio.

---

## Funciona em tres IDEs

O mesmo repositorio ja vem pronto pras tres, sem configuracao:

| IDE | Le as instrucoes de | Le as skills de |
| --- | --- | --- |
| Claude Code | `CLAUDE.md` | `.claude/skills/` |
| Codex | `AGENTS.md` | `.agents/skills/` |
| Antigravity | `AGENTS.md` | `.agents/skills/` |

`.agents/skills/` e o padrao aberto de Agent Skills e e onde as skills sao editadas; o `.claude/skills/` e um espelho que o instalador regera. Por isso **nao existe `GEMINI.md`** na raiz: o Antigravity le o `GEMINI.md` e o `AGENTS.md` juntos, e os dois fariam ele carregar o roteador em dobro.

Depois de instalar, `python .agents/skills/instalador-expert/tools/instalar.py --verificar` diz se cada IDE esta pronta.

---

## Requisitos

- **Claude Code, Codex ou Antigravity**
- **Python 3.8+**
- **Obsidian**
- **Git**

Opcionais, so para as skills que usam:

| Ferramenta | Quem usa |
| --- | --- |
| Node.js (`npm run dev` dos projetos) | todas as de site |
| Vercel CLI | `vercel-expert` |
| GitHub CLI (`gh`) | publicacao de projeto (Regra de Ouro 9) |
| ffmpeg | `motion-expert`, `lipsync-expert`, `processo-expert`, `cinematic-expert` |
| ElevenLabs (chave em `voice-expert/tools/secrets.local.json`, modelo em `secrets.example.json`) | `voice-expert`, `estudos-expert`, `processo-expert` |
| Higgsfield MCP | `cinematic-expert` |
| Skills `gsap-*` e `img2threejs` (marketplace de skills do Claude Code) | `cinematic-expert`, cenas 3D |
| RunningHub e Gemini (chaves em `motion-expert/tools/secrets.local.json`) | `motion-expert` |
| Google Stitch MCP | `frontend-expert` (funciona sem) |

Duas skills pedem um passo antes do primeiro uso: a `vitrine-expert` usa a primeira vitrine que a esteira montar como gabarito das seguintes, e a `dodo-ia` fica mais precisa depois das primeiras semanas de autopsia (a interpretacao dela nasce vazia e se enche com o uso).

---

## Instalar

```
git clone https://github.com/philipeapenas/dodo-exe.git
cd dodo-exe
```

Depois, **abra a pasta no Claude Code, no Codex ou no Antigravity e diga: `instala o Dodo.exe`**. A `instalador-expert` roda o instalador, conversa com voce pra preencher a sua Identidade (proposito, meta, principios, rotina), cria uma pasta para cada operacao que voce tocar e gera a sua primeira semana.

Prefere rodar a parte mecanica antes, sem IA?

- Windows: `powershell -ExecutionPolicy Bypass -File install.ps1`
- Mac, Linux ou Git Bash: `sh install.sh`

Por ultimo, no Obsidian: **Abrir pasta como vault** e escolha `Vault/`.

---

## Como o dia funciona

1. De manha a autopsia do dia nasce com o seu bloco de rotina.
2. Voce diz a hora que acordou e a `dodo-ia` recalcula os horarios do dia inteiro.
3. Ao abrir um bloco de operacao, ela conduz o ritual: analisar a meta, criar o plano do dia, otimizar os documentos. Quando voce disser "aplique o plano do dia", o time executa.
4. No domingo, a `dodo-ia` levanta o estado das operacoes e o `ceo-dodo` propoe a ordem da semana.
5. Quando nenhuma skill souber fazer algo, a `skill-expert` treina a mais proxima ou contrata uma nova.

As automacoes que rodam sozinhas no Windows (autopsia de manha, vigia da rotina, fechamento do dia) vem **desligadas**. Os comandos pra ligar estao em `.agents/skills/dodo-ia/tools/comandos_da_rotina.md`.

---

## Atualizar

```
git pull
sh install.sh        (ou install.ps1 no Windows)
```

O instalador nunca sobrescreve nada que ja exista no seu `Vault/`.

---

## Licenca

Distribuido sob a [Dodo Company License](LICENSE). O codigo pode ser usado, modificado e distribuido com o aviso de copyright e a licenca. Os nomes, logos e identidade visual de Dodo.exe e Dodo.IA nao sao cedidos como marca.

---

## Estrutura

```
dodo-exe/
├── CLAUDE.md  AGENTS.md               roteador (CLAUDE.md e o master; AGENTS.md e gerado)
├── .agents/skills/                    as skills (master; Codex e Antigravity leem daqui)
├── .claude/skills/                    espelho que o Claude Code le
├── Agente Orquestrador/               regras de ouro, protocolo de mensagens, sync
├── vault-modelo/                      o modelo de fabrica do vault
├── Vault/                             o SEU vault, criado na instalacao (fora do git)
├── Projetos/Dominio/  Projetos/Localhost/
├── tools/varrer_vazamento.py          varredura de segredo antes de publicar
├── tools/validar_skills.py            confere o cabecalho das skills (Codex e Antigravity sao rigidos)
└── install.ps1  install.sh  INSTALAR.md
```
