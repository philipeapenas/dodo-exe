# Protocolo de Mensagens - Ecossistema Dodo
**Versao:** 3.1 | **Data:** 14/05/2026

Este documento e o padrao canonico de comunicacao inter-skill. Todo funcionario (skill) DEVE ler e seguir este protocolo ao ler/escrever em `mensagens.json`.

---

## A Regra de Localizacao (V3.0)

O "cerebro" de comunicacao de um projeto NAO e mais global. O arquivo `mensagens.json` deve residir ESTRITAMENTE dentro da pasta do projeto em desenvolvimento (projetos de codigo, frontend, etc).
**Caminho Padrao:** `Projetos/[NomeDoProjeto]/Resumo do projeto/mensagens.json`

Se o arquivo ou a pasta `Resumo do projeto/` nao existirem ao iniciar ou modificar um projeto, a primeira skill acionada (ou o orquestrador) DEVE cria-los.

---

## Rotacao de Sessao (V3.1)

**Politica:** 1 `mensagens.json` por sessao. Historico em `_arquivo/`.

**Gatilhos de rotacao** (qualquer um dispara o ritual):
1. Founder decreta encerramento da sessao verbalmente ("pode encerrar", "fecha sessao", etc.)
2. `mensagens.json` ultrapassa **~50KB** durante a sessao (medir antes de cada nova mensagem grande)

**Ritual de rotacao** (orquestrador delega para `assistente-expert`):
1. Criar pasta `[ProjetoPath]/Resumo do projeto/_arquivo/` se nao existir
2. Mover `mensagens.json` atual para `_arquivo/mensagens_<YYYY-MM-DD>.json` (timezone Brasilia)
3. Criar novo `mensagens.json` zerado:
   ```json
   {
     "messages": [],
     "session_started": "<YYYY-MM-DD>",
     "note": "Arquivo zerado em <YYYY-MM-DD>. Historico anterior em _arquivo/. Politica: 1 arquivo por sessao."
   }
   ```
4. NAO criar nota no Vault: rotacao e housekeeping interno, nao entrega de valor.

**Razao:** Arquivos inflados acima de 50KB deixam o contexto inter-skill lento, dificultam debug e poluem prompts de skills que precisam ler `mensagens.json` na ativacao. Rotacao por sessao mantem o "cerebro de comunicacao" enxuto e o historico recuperavel.

**Conflito de gatilhos:** Se o limite de 50KB disparar antes do encerramento, rotacionar imediatamente: a nova sessao continua com o mesmo trabalho mas em arquivo limpo.

---

## Formato da Mensagem

```json
{
  "id": "msg_001",
  "type": "work_order | handoff | request | response | broadcast | help",
  "from": "user | nome-da-skill-remetente",
  "to": "nome-da-skill-destinataria | all",
  "subject": "Resumo em uma linha do assunto",
  "message": "Corpo da mensagem com contexto necessario para a skill destinataria executar sua tarefa.",
  "context": {
    "project": "Nome do projeto relevante",
    "artifacts": ["caminho/relativo/do/arquivo.md"],
    "next_action": "O que a skill destinataria deve fazer com essa informacao"
  },
  "timestamp": "2026-05-03T20:08:00-03:00",
  "status": "pending"
}
```

### Campos obrigatorios
| Campo | Tipo | Descricao |
|---|---|---|
| `id` | string | ID unico: `msg_` + sequencial (ex: `msg_001`) |
| `type` | string | Tipo da mensagem (Obrigatorio) |
| `from` | string | Nome exato da skill remetente (ou "user" se for input direto) |
| `to` | string | Nome da skill destinataria, ou `"all"` para broadcast |
| `subject` | string | Uma linha descrevendo o assunto |
| `message` | string | Contexto completo que a destinataria precisa |
| `timestamp` | ISO 8601 | Data/hora no timezone Brasilia (UTC-3) |
| `status` | enum | `"pending"` (nao lido) ou `"read"` (processado) |

---

## Protocolo de Ativacao (O Input)

O workspace opera como uma maquina de estados baseada neste JSON.

1. **Gatilho Inicial:** Ao receber um pedido livre do usuario no chat, o Orquestrador (ceo-dodo ou a primeira skill acionada) **DEVE** transformar esse prompt em uma Ordem de Servico estruturada (`type: "work_order"`, `from: "user"`) e salva-la no `mensagens.json` do projeto. Isso age como um filtro cognitivo.
2. **Leitura:** Toda skill, ao iniciar o trabalho, DEVE ler o `mensagens.json` do projeto.
3. **Filtragem:** Filtrar mensagens onde `to == nome-desta-skill` OU `to == "all"` E `status == "pending"`.
4. **Processamento:** Extrair o contexto, entender a missao e, imediatamente, marcar o `status` como `"read"`.

---

## Protocolo de Encerramento (O Handoff)

Toda skill, ao concluir sua micro-tarefa, DEVE:

1. **Depositar uma mensagem** no `mensagens.json` do projeto com:
   - `from:` o proprio nome
   - `to:` a proxima skill na cadeia (ou `"ceo-dodo"` / `"user"` se for o fim do track)
   - `type:` `"handoff"`
   - `status: "pending"`

> **Aviso Tracker de Atividades Ativo:** O arquivo `registro_atividades.json` continua sendo utilizado DURANTE a sessao para mapear o status das tasks e com qual skill/sub-agente a bola esta. Ele corre em paralelo ao `mensagens.json` para evitar perda de contexto.
>
> **Encerramento da Sessao (O Resumo):** A sessao de trabalho SO termina quando o usuario decretar o fim verbalmente na interface de chat. Neste momento, o Orquestrador deve compilar as acoes realizadas em um arquivo `session_summary.json` (dentro de `Resumo do projeto/`). A criacao/preenchimento deste arquivo engatilha a `assistente-expert` para compilar o contexto e redigir o relatorio final no Vault em formato Markdown (`.md`).

---

## Tipos de Mensagem

| `type` | Quando usar | Exemplo |
|---|---|---|
| `"work_order"` | Transformacao do prompt do usuario em JSON (passo inicial) | user -> frontend-expert: "Refazer layout X" |
| `"handoff"` | Skill terminou trabalho e entrega para a proxima | frontend-expert -> dev-expert: "CSS pronto, contrato de classes em X" |
| `"request"` | Skill precisa pedir algo para outra skill | copywriter-expert -> voice-expert: "preciso da transcricao do audio X" |
| `"response"` | Skill respondendo a um `request` | voice-expert -> copywriter-expert: "transcricao pronta, ver arquivo Y" |
| `"broadcast"` | Informacao para todos os funcionarios | ceo-dodo -> all: "protocolo atualizado para V3" |
| `"help"` | Skill nao sabe fazer algo, e pede socorro ao RH | frontend-expert -> skill-expert: "preciso de skill que transcreva" |

---

## Regras de Colaboracao Inter-Skill

1. **Skills conversam diretamente** - sem precisar do CEO como intermediario.
2. **Quem pede DEVE passar as especificacoes.** A skill remetente define o que precisa, formato e destino.
3. **Quem recebe o request DEVE responder** com um `response` (se souber fazer) ou pedir `help` (se nao souber e precisar de treinamento).
4. **O RH (skill-expert) cuida de novas capacidades.** Se ninguem souber fazer, o RH aciona o `training_protocol.md`.
5. **O CEO monitora** a comunicacao, mas as skills resolvem seus gargalos entre si.
