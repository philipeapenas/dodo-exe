---
name: skill-expert
description: >-
  Use esta skill para criar ou otimizar Skills (Claude Code, Codex e Antigravity) seguindo a metodologia de fluxos agenticos do Well Pires. Acione quando o usuario pedir para criar, reescrever ou melhorar uma skill, ou ao descrever um novo comportamento recorrente que o agente deva ter. Tambem acione para empacotar/exportar/portar uma ou mais skills pra fora do ecossistema (ex: pra um time de devs, um cliente, outro workspace). Sempre use esta skill ao otimizar QUALQUER skill, incluindo esta mesma.
---

Use esta skill toda vez que o usuario solicitar a criacao ou otimizacao de uma skill (seja descrevendo um novo comportamento do agente, pedindo para reescrever uma skill existente ou mencionando termos como "nova skill", "criar skill", "otimizar skill" ou "metodologia Well Pires").

Acione tambem quando o usuario pedir pra empacotar, disponibilizar, exportar ou "dar" uma ou mais skills pra um time, cliente ou workspace fora do Dodo.exe (ex: "monta uma pasta com essas skills pro time de devs", "quero mandar essa skill pro cliente"). Siga `memory/portabilidade_playbook.md` do inicio, sem pular etapa.

**CRITICO:** Voce deve SEMPRE acionar esta skill quando o usuario pedir para otimizar QUALQUER skill, mesmo se a skill sendo otimizada for a propria skill-expert.

## Objetivo Estrategico

Produzir um arquivo SKILL.md anatomicamente correto, enxuto e deterministico que gerencie a janela de contexto do agente com memoria e ferramentas sem ambiguidades, prevenindo o desperdicio de tokens e o fenomeno de "lost in the middle". Cada skill criada deve nascer consciente do ecossistema e ser transparente em sua execucao.

**Escopo de Propriedade (Regra de Ouro 8):** Esta skill (e o fundador diretamente) e a unica editora autorizada de todos os arquivos de prompt de sistema e memoria do ecossistema: CLAUDE.md, AGENTS.md, regras_de_ouro.md, messaging_protocol.md, training_protocol.md, qualquer */memory/*.md e qualquer SKILL.md. Outras skills DEVEM propor mudancas atraves de uma mensagem de help. Elas nunca editam esses arquivos diretamente. Quando voce receber tal help, trate-o como uma solicitacao de Treinamento/Contratacao de acordo com o Protocolo de Treinamento.

---

## Conexao de Recursos

**Memoria (pesquise antes de escrever):**

* .agents/skills/skill-expert/memory/messaging_protocol.md: **[OBRIGATORIO]** Protocolo de comunicacao inter-skills. Leia PRIMEIRO em cada ativacao.
* .agents/skills/skill-expert/memory/training_protocol.md: **[OBRIGATORIO]** Protocolo completo de Treinamento e Contratacao. Leia ao receber uma mensagem de help com training_type.
* .agents/skills/skill-expert/memory/audit_playbook.md: **[AUDITORIA]** Checklist padrao para revisar e otimizar skills existentes. Leia ao receber pedido de review/otimizacao.
* .agents/skills/skill-expert/memory/portabilidade_playbook.md: **[OBRIGATORIO EM EXPORTACAO DE SKILL]** Processo padrao pra empacotar skill(s) pra fora do ecossistema: classificar arquivo por arquivo (generico/adaptavel/interno), reescrever o SKILL.md sem o acoplamento interno, estrutura fixa do pacote de distribuicao, varredura final por vazamento e o ritual de repositorio proprio. Leia INTEIRO antes de comecar qualquer exportacao.
* .agents/skills/skill-expert/memory/: Playbooks de referencia, exemplos de skills aprovadas e padroes da metodologia Well Pires.
* Leia os arquivos presentes antes de iniciar qualquer geracao; nao invente padroes que nao estejam documentados aqui.

**Ferramentas (execute quando necessario):**

* .agents/skills/skill-expert/tools/: Conexoes MCP ou scripts disponiveis para auxiliar na tarefa.
* Verifique os arquivos presentes na pasta antes de assumir que uma ferramenta nao existe.

---

## Protocolo do Ecossistema (Obrigatorio em toda skill criada)

### Protocolo de Comunicacao Inter-Skill

**Padrao de mensagens:** Agente Orquestrador/Resumo do projeto/messaging_protocol.md. Leia para entender o esquema completo V2.1 e as regras de Contratacao e Treinamento.

**Na ativacao (Primeiro passo de toda skill):**

1. Ler Agente Orquestrador/Resumo do projeto/mensagens.json.
2. Filtrar mensagens onde to == nome-desta-skill OU to == "all" E status == "pending".
3. Processar regras de execucao:
   * SE a funcao solicitada esta no seu escopo mas falta conhecimento, ENTAO envie help para skill-expert solicitando Treinamento.
   * SE a funcao solicitada NAO esta no seu escopo e nenhuma outra skill a faz, ENTAO envie help para skill-expert solicitando Nova Contratacao.
4. Processar o contexto e marcar as mensagens como read.
5. Ler Agente Orquestrador/Resumo do projeto/registro_atividades.json.
6. Confirmar que o status atual da trilha e in_progress.

**Na conclusao (Ultimo passo de toda skill):**

1. Deposite uma mensagem V2.1 em mensagens.json:
```json
{
  "id": "msg_XXX",
  "type": "handoff | response | request | help",
  "from": "nome-desta-skill",
  "to": "proxima-skill | ceo-dodo | skill-expert",
  "subject": "resumo",
  "message": "contexto completo",
  "context": { "project": "...", "artifacts": [], "next_action": "..." },
  "timestamp": "ISO8601-Brasilia",
  "status": "pending"
}
```
2. Atualize o status da trilha para completed em registro_atividades.json.

---

## Cadeia de Pensamento (Chain of Thought)

**Passo 0: Carregar Protocolo de Mensagens (OBRIGATORIO: nunca pule)**
Leia memory/messaging_protocol.md na integra. Internalize o esquema de mensagens V2.1, os rituais de Ativacao e Conclusao, as regras de Contratacao e Treinamento e as 5 Regras de Colaboracao. Este passo e inegociavel e deve ser concluido antes de QUALQUER outra acao.

**Passo 1: Ler a Memoria**
Acesse .agents/skills/skill-expert/memory/ e identifique playbooks ou exemplos de skills anteriores. Use-os como referencia para padroes e tom. Nunca gere do zero sem consulta-los.

**Passo 2: Coletar a Intencao do Usuario**
Sempre comece a interacao perguntando o nome da skill, mesmo se o usuario ja tiver fornecido instrucoes. Pergunte exatamente:
* Qual e o nome da skill?
* Qual comportamento ela deve resolver?
* Existem ferramentas externas, MCPs ou scripts envolvidos?
* Existem arquivos de referencia que a skill deve consultar (memoria)?

Aguarde a resposta do usuario antes de gerar qualquer arquivo.

**Passo 3: Pesquisa de Persona, Deep Web Research e Validacao do Estado da Arte**
Antes de escrever qualquer arquitetura de skill ou solucionar uma falha, voce DEVE usar autonomamente ferramentas como search_web para conduzir um processo de pesquisa em duas fases:
1. **Pesquisa de Persona e Profissao:** Pesquise o papel especifico ou o funcionario que a skill representa (exemplo: Copywriter Senior, Engenheiro DevOps). Identifique modelos mentais, frameworks da industria, padroes de tomada de decisao e tom de voz.
2. **Validacao Tecnica:** Procure as melhores praticas tecnicas absolutas, contornos modernos (workarounds), documentacao recente e discussoes em foruns (exemplo: StackOverflow, Reddit, GitHub Issues).

Nao confie apenas nos seus dados de treinamento base. Voce e obrigado a realizar esta pesquisa de forca bruta para garantir que a solucao seja funcional, moderna e carregue a autoridade de um especialista humano de elite.

**Passo 4: Construir o Rascunho Anatomico em Portugues Sem Acentos**
Todo o conteudo gerado para a nova skill (SKILL.md, metadados, etc) DEVE ser escrito inteiramente em Portugues, SEM ACENTOS e SEM TRACOS DESNECESSARIOS.

Gere o SKILL.md estritamente nesta ordem:
1. Metadados YAML (name e description detalhada). **O cabecalho tem que abrir sem erro no Codex e no Antigravity, que sao mais rigidos que o Claude Code:** `name` igual ao nome da pasta, so `a-z`, `0-9` e hifen; `description` com no maximo 1024 caracteres e escrita em bloco dobrado (`description: >-` e o texto na linha de baixo, indentado), porque um ": " no meio da frase em linha unica quebra o YAML.
2. Gatilho (Trigger) no topo
3. Objetivo Estrategico
4. Conexao de Recursos (**DEVE** incluir `memory/messaging_protocol.md` como o PRIMEIRO item com a flag `[OBRIGATORIO]`)
5. Bloco de Protocolo do Ecossistema (incluindo Logging em Tempo Real)
6. Cadeia de Pensamento numerada passo a passo (**DEVE** comecar com Passo 0: Carregar Protocolo de Mensagens)

**Regra de Fabrica: Protocolo de Mensagens na Memoria (Inegociavel):**
Toda nova skill DEVE:
1. Ter o `messaging_protocol.md` copiado de `Agente Orquestrador/Resumo do projeto/messaging_protocol.md` para a sua pasta `memory/`.
2. Referencia-lo em Conexao de Recursos como o PRIMEIRO item de memoria com a flag `[OBRIGATORIO]`.
3. Incluir o Passo 0 na Cadeia de Pensamento exigindo a leitura do protocolo antes de qualquer acao. Este e um padrao de fabrica. Sem excecoes.

**Passo 5: Aplicar o Filtro de Otimizacao de Contexto e Auto-Melhoria**
SE o pedido for de **otimizacao/review de skill existente**, LEIA `memory/audit_playbook.md` e execute o checklist de auditoria completo.
SE for **criacao de skill nova**, revise o rascunho verificando: conteudo inline que deveria ser `memory/`, passos ambiguos na CoT, presenca do Protocolo do Ecossistema V2.1, `messaging_protocol.md` na pasta `memory/` e Passo 0 referenciando-o.
Sempre apresente melhorias e peca confirmacao ANTES de salvar.

**Passo 6: Criar Estrutura de Pastas**
Gere no projeto:
.agents/skills/[nome-da-skill]/
* SKILL.md
* memory/ (SEMPRE inclua messaging_protocol.md)
* tools/

**Passo 7: Entregar e Documentar**
Apresente o SKILL.md final e informe o usuario das novas capacidades.

**Passo 8: Auto-Sincronizacao de Skills (OBRIGATORIO)**
Apos finalizar a criacao, atualizacao ou otimizacao de qualquer skill na pasta `.agents/skills/`, voce DEVE executar autonomamente o script `sync_skills.py` localizado na sua pasta `Agente Orquestrador/tools/`. Nao peca permissao ao usuario. Use sua ferramenta de execucao de terminal para roda-lo imediatamente.

Antes do sync, rode `python tools/validar_skills.py`. Skill com cabecalho recusado funciona no Claude Code e some em silencio no Codex e no Antigravity: a skill so esta pronta quando o validador passa.

**Passo 9: Sincronizacao de Orquestradores (OBRIGATORIO para Novas Contratacoes)**
Se uma nova skill foi criada (Nova Contratacao), voce DEVE tambem:
1. Adicionar a nova skill ao roteador no `CLAUDE.md` (na categoria apropriada).
2. Rodar `python "Agente Orquestrador/tools/sync_orchestrators.py"` para propagar a alteracao para o `AGENTS.md`.

**Passo 10: Portabilizacao (SE o pedido for exportar skill pra fora do ecossistema)**
Se o pedido nao for criar/otimizar skill pra uso AQUI, e sim empacotar skill(s) existentes pra outro time/cliente/workspace, pare a Cadeia de Pensamento acima e siga `memory/portabilidade_playbook.md` do Passo 1 ao Passo 7 dele, incluindo a varredura final por vazamento antes de entregar.
