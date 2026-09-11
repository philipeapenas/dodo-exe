# Auto-Archive Protocol: assistente-expert

> Memoria exclusiva do ritual de encerramento autonomo. Consulte sempre que receber um `SessionContext` do `ceo-dodo` ou quando existir um `session_summary.json` preenchido.

---

## Schema do session_summary.json

```json
{
  "session_id": "YYYY-MM-DD_HH-MM",
  "objetivo": "1 frase do que foi feito",
  "skills_acionadas": ["skill1", "skill2"],
  "entregas": [{"titulo": "Nome da entrega", "arquivo": "caminho/vault/entrega.md"}],
  "decisoes": "decisoes tomadas",
  "aprendizados": "regras/licoes geradas",
  "projeto": "Nome exato do projeto (ex: 'Dodo')",
  "template": "entrega | funcionario | projeto | chat_only",
  "relatorio_execucao": "caminho/da/nota/de/relatorio.md (opcional, ver abaixo)"
}
```

### O relatorio de execucao (26/08/2026)

Quando a sessao mexeu em varias pecas de um projeto, ela produz um **relatorio de execucao**: o que passou a existir, o que quebrou e foi consertado, o que ficou pendente, e o custo quando houver.

**Ele vive como NOTA no vault, nao como Artifact.** O fundador decidiu assim ao comparar o custo: o relatorio nasce no Obsidian e fica linkado na nota da tarefa da OP do dia. O Artifact cobra o andaime de HTML/CSS por cima do mesmo conteudo, e a nota ja nasce onde o arquivamento precisa dela. O Artifact continua sendo o formato do DESENHO antes de codar (Regra de Ouro 19), nao do relatorio depois.

#### Relatorio e entrega sao notas DIFERENTES (corrigido por ele em 27/08/2026)

Ele corrigiu essa divisao depois de ver os papeis trocados. Nao confunda:

| Nota | Responde | Escopo | Onde |
|---|---|---|---|
| **Relatorio de execucao** | *Onde o plano esta?* | Uma nota por **PLANO**, acumulando **SESSOES**: "Sessao 1 cobriu os processos 1, 2 e 3". Abre com a tabela de cada processo do plano e seu estado. | `Tarefas/<Mes>/<OP>/Relatorio de execucao DD-MM-AA.md` |
| **Nota de entrega** | *O que foi feito?* | Uma nota por **SESSAO**. O detalhe concreto do que foi construido naquela sessao, o que quebrou e foi consertado, decisoes e custo. | `Operações/OP <Nome>/Projetos/<projeto>/03_Entregas/DD-MM-AA/` |

Na definicao do fundador: o relatorio e o livro das sessoes, e a nota de entrega e o que foi feito tecnicamente dentro de cada sessao.

**Por que a distincao importa:** o plano tem processos numerados e leva varias sessoes. Sem o livro das sessoes, ninguem sabe em que ponto do plano a operacao parou sem reler todas as notas de dia. **Numa sessao seguinte do mesmo plano, NAO crie relatorio novo**: acrescente a secao `## Sessao N` no relatorio que ja existe e atualize a tabela de estado no topo.

**Formato:** `memory/templates/template_relatorio_de_execucao.md`, aprovado pelo fundador como padrao.

**Nome do arquivo:** `Relatorio de execucao - <Nome do plano> DD-MM-AA.md`. O nome do plano no titulo foi acrescentado pelo proprio fundador, renomeando a nota, e o que distingue dois relatorios da mesma OP na mesma pasta.

**Quem escreve e voce, `assistente-expert`.** A skill de execucao entrega o conteudo; a escrita no vault e sua.

**Onde:** nota dedicada, **linkada na nota da tarefa da OP do dia**. A nota da tarefa segue como registro unico da tarefa (Regra 16), o relatorio pendura nela, nao a substitui. Detalhe tecnico e permitido nessa cadeia, que e a excecao explicita a Regra 13.

**Consequencia pra este ritual:**

1. **Se `relatorio_execucao` vier preenchido, LEIA a nota**: mas **`mensagens.json` continua sendo a fonte do que aconteceu.** Os dois papeis nao se substituem:

   | | `mensagens.json` | Relatorio de execucao |
   |---|---|---|
   | Como nasce | escrito a cada handoff, durante a sessao | escrito no fim, por um autor que escolhe o que contar |
   | Forte em | **completude**: nada que passou pela cadeia fica de fora | **estrutura e porque**: ja vem organizado e explicado |
   | Fraco em | narrativa: e log, nao texto | **omissao**: o que o autor esqueceu de por, sumiu |

   Ordem de uso: **relatorio pra entender, `mensagens.json` pra conferir.** Depois de escrever, varra o `mensagens.json` procurando handoff que a nota nao cobre, decisao revertida, erro corrigido no meio, pendencia aberta e nao resolvida. E ali que mora o que o relatorio final costuma comer.
2. **A NOTA DE ENTREGA nao e copia do relatorio.** Sao notas diferentes com regras diferentes: a de entrega segue a Regra 13 (objetiva, linguagem de negocio, sem bloco de codigo, caminho de arquivo, nome de funcao ou endpoint); o relatorio de execucao pendura na nota da tarefa, onde o detalhe tecnico e permitido (Regra 16).
3. **A nota de entrega abre com DUAS linhas de link**, logo abaixo do titulo e antes do Resumo (aprovado por ele em 30/08/2026):
   - `Relatório de execução do plano: [[...]]`: o detalhe fica a um clique sem poluir o texto que ele consulta.
   - `Material de referência usado: [[...]]`: as notas de INSUMO da sessao (referencia visual, canvas, material que virou codigo). Elas nao sao entrega e nao podem ser listadas junto das entregas, senao viram produto da sessao aos olhos de quem le depois.
4. Se o campo vier vazio, siga como antes, `mensagens.json` continua sendo a fonte do que mudou.

---

## Checklist dos 4 Passos (em ordem, sem pular)

> **Nao existe nota diaria solta.** O ritual NAO cria nota de dia fora da nota de tarefa da OP, e nao registra log de atividade nem de chat. O registro do dia vive na nota do dia da OP e na autopsia.

### Mapa de caminhos do vault

> **Leia esta tabela ANTES de escrever qualquer coisa.** Pastas numeradas na raiz (`01_Projetos/`, `03_Recursos/Anotacoes/`) **nao existem** neste vault. Quando houver duvida, abra a OP mais completa do vault e copie a forma (ver `vault_structure.md`).

| O que | Onde vive hoje |
|---|---|
| Nota mestre da operacao | `Operações/OP <Nome>/Tudo sobre <Nome> DD-MM-AA.md` |
| Plano da semana | `Operações/OP <Nome>/Planos/Plano inicial DD-MM-AA.md` |
| Decisao estrategica | `Operações/OP <Nome>/Decisões estratégicas/<decisao> - <Projeto> - DD-MM-AA.md` (padrao desde 10/09/2026) |
| Registro de tarefa **arquivado** | `Operações/OP <Nome>/Projetos/<projeto>/Processos/<Titulo> DD-MM-AA.md` quando a OP tem projeto. Ver Passo 2.6 |
| Documento de estado do projeto | `Operações/OP <Nome>/Projetos/<projeto>/01_PRF.md` |
| Nota de entrega | `Operações/OP <Nome>/Projetos/<projeto>/03_Entregas/<DD-MM-AA>/<slug>-<DD-MM-AA>.md` |
| Nota de tarefa (a do dia, em uso) | `Tarefas/<Mes>/OP <Nome>/<Titulo> DD-MM-AA.md` |

**Duas armadilhas de formato:**

- A data e **DD-MM-AA**, nao `YYYY-MM-DD`, e vem no **fim** do nome do arquivo, nao no comeco.
- A entrega mora numa **pasta por dia** dentro de `03_Entregas/`, nao solta na raiz dela.

**Subpasta de Semana:** `Tarefas/Julho/` usa `Semana N/`; de **Agosto em diante nao usa mais**. Olhe o mes de destino antes de criar pasta.

**Registro de tarefa arquivado vai pra `Processos/`, nao pra `03_Entregas/`.** `03_Entregas/` e so nota de entrega. Ao arquivar, **preservar o nome do arquivo**: renomear quebra o wikilink do `01_PRF`.

---

### Passo 1: Nota de Entrega (OBRIGATORIO se projeto foi tocado)

```
Local: Vault/Operações/OP <Nome>/Projetos/<projeto>/03_Entregas/<DD-MM-AA>/<slug>-<DD-MM-AA>.md
Template: memory/templates/template_entrega.md
```

O `<slug>` sai do titulo da propria nota, em kebab-case e sem acento.

**Roteamento de Inteligencia:**
- Mudancas de **Workflow, Vault, Skills, Regras** → `Projetos/Dodo Workspace/`
- Mudancas **Tecnicas, Codigo, Bugs** de um projeto de cliente → a pasta do projeto dentro da OP dele
- Multiplas entregas na sessao → criar notas SEPARADAS por projeto/categoria

**Secoes obrigatorias da nota:**
1. Resumo da Entrega
2. Detalhes Tecnicos (mudancas, arquivos, decisoes)
3. Funcionario Responsavel (links `[[skill]]`)
4. Resultado (sucesso/parcial/falha)
5. Arquivos Criados/Modificados
6. Aprendizados

**Quando criar post-mortem:** Se a sessao envolveu diagnostico de erro/bug → adicionar secao `## POST-MORTEM` com: sintoma, root cause, por que nao foi detectado antes, timeline, regras permanentes.

---

### Passo 2: Sincronizar os documentos vivos do projeto (OBRIGATORIO se projeto foi tocado)

> Objetivo: o fundador nunca mais topar com documento de projeto desatualizado. A regra nasceu de um `01_PRF.md` que passou dois meses descrevendo uma arquitetura que ja tinha sido trocada.

**Fonte da verdade do que mudou:** ler `Resumo do projeto/mensagens.json` (handoffs desta sessao) e `Resumo do projeto/session_summary.json`. E dali que sai a lista do que a sessao alterou, nao inferir da conversa quando o registro existe.

**Somente estes tipos de `.md`. NAO migrar todo `.md` do projeto pro vault:**

| Documento | Onde vive | Acao no encerramento |
|---|---|---|
| Plano de implementacao | **Dentro da nota de tarefa** em `Tarefas/<Mes>/OP <Nome>/` (Regra de Ouro 16) | Confirmar que a nota reflete o que a sessao mudou. Se ainda existir plano solto na raiz do projeto (padrao antigo), migrar o conteudo pra nota e apagar o arquivo. Planos ja arquivados em `02_Planos/` NAO sao migrados, a regra nao retroage |
| **Fecho da nota do dia** | Ultima secao de `Tarefas/<Mes>/OP <Nome>/<Titulo> DD-MM-AA.md` | Acrescentar `## Relatório de execução - DD/MM` no formato do fundador, **indice de links, nunca narrativa**. Esqueleto e regras em `templates/template_retomada_op.md`. Ver abaixo |
| Documento de estado | `Operações/OP <Nome>/Projetos/<projeto>/01_PRF.md` | Se a sessao mudou COMO o projeto funciona (arquitetura, onde roda, como se opera), corrigir as secoes que descrevem o PRESENTE e atualizar o campo `atualizado` |
| Nota de entrega | `Operações/OP <Nome>/Projetos/<projeto>/03_Entregas/<DD-MM-AA>/` | Ja coberto pelo Passo 1 |

**Regras:**

- NAO mover `README.md` do repositorio, `SKILL.md`, `CLAUDE.md`, `AGENTS.md` nem qualquer `*/memory/*.md`. Esses permanecem onde estao (Regra de Ouro 8, so skill-expert ou fundador editam).
- Ao mover qualquer documento, procurar quem o referencia (codigo e outros docs) e atualizar o caminho. Referencia orfa vira link morto.
- O vault NAO tem git: conteudo apagado la nao volta. Mover e preservar, nunca deletar historico. Ao enxugar um documento, marcar o trecho antigo como arquivo em vez de remover.
- Texto da nota segue a Regra de Ouro 13 (objetiva, linguagem de negocio, sem caminho de arquivo nem nome de funcao). O detalhe tecnico vive na **nota de tarefa** (Regra de Ouro 16, unica excecao a Regra 13) e no `mensagens.json`. Nota de entrega, `01_PRF.md` e daily seguem a Regra 13 integralmente.

#### O fecho da nota do dia (formato do fundador, 27/08/2026)

Ele reescreveu esta secao por cima da versao que a skill tinha deposto. **NAO recontar a sessao aqui:** a versao anterior trazia o que mudou no escopo, as pendencias que ficam e as que se resolveram, e ele apagou tudo. Esse conteudo ja vive no relatorio de execucao e na nota de entrega, repetir cria tres versoes da mesma coisa pra desatualizar em ritmos diferentes.

```
---

## Relatório de execução - DD/MM

**Relatório de execução:** [[Relatorio de execucao - <Nome do plano> DD-MM-AA]]

- **Nota de entrega:**
	- Seção 1: [[<slug-da-entrega>-DD-MM-AA]]

- **Desenho aprovado da tela:**
	- Seção 1: <link do artefato>
```

- A data do titulo e a do **dia da nota**, nao a do dia em que a sessao foi encerrada.
- Entrega e desenho sao **lista aninhada indexada por seção**, porque a secao ACUMULA: a sessao seguinte acrescenta `Seção 2:` embaixo de cada uma, em vez de sobrescrever.
- Bloco que nao existir naquela sessao nao entra. Nunca deixar rotulo vazio esperando preenchimento.

---

### Passo 2.5: Nota de processo (OBRIGATORIO se a sessao rodou um processo que se repete)

```
Local: Vault/Processos/<Area ou OP>/<Nome do processo> DD-MM-AA.md
Template: memory/templates/template_processo.md
```

**O fundador parou de escrever essas notas a mao em 28/08/2026.** Ele as escrevia pra nunca
esquecer como um processo foi feito, e passou a escrita pro time mantendo o padrao dele. Uma
das notas da pasta estava vazia ha semanas, criada e nunca preenchida, e o sintoma que gerou
a mudanca.

**O que a nota carrega:** o FLUXO, em 3 a 6 passos numerados, na linguagem dele, mais a linha
`Qnt tempo p fazer` quando houver tempo real medido. **Nao carrega tecnica:** quem sabe fazer cada coisa com excelencia sao as skills
especializadas, pelo treinamento que receberam. Comando, caminho, parametro e decisao
tecnica vivem na `memory/` da skill que executa, repetir aqui cria duas fontes e uma delas
envelhece.

**Nutrir a que existe e o padrao.** Nota nova, com data nova, so quando o fluxo mudou a ponto
de ser outro processo; nesse caso, linkar a anterior.

**Nem toda sessao gera.** So gera quando a sessao rodou um processo que vai se repetir. Sessao
de conversa, de decisao ou de correcao pontual nao gera, mesmo criterio da Regra de Ouro 20.

**Quem le depois:** a `dodo-ia`, pra saber se um processo que ele pediu no chat ja foi feito e
com qual fluxo. E o que alimenta o catalogo dela (`memory/fluxos_operacionais.md`).

---

### Passo 2.6: Arquivamento de fim de sessao (OBRIGATORIO, ritual automatico)

**Origem:** erro real. A nota do dia anterior de uma OP foi arquivada em
`Operações/OP <Nome>/Processos/` (nivel da OP) quando as notas irmas ja viviam em
`Operações/OP <Nome>/Projetos/<projeto>/Processos/` (nivel do PROJETO). O fundador mandou virar ritual automatico: **nao esperar ele reparar a bagunca.**

**O que fazer, toda vez que a sessao encerra:**

Varrer `Tarefas/<Mes>/<OP>/` e subir pro `Processos/` correto tudo que ja saiu de uso,
deixando na pasta de tarefas **somente a nota do dia ATIVA**.

**Qual `Processos/` e o correto:**

| Caso | Destino |
|---|---|
| A OP tem projeto e a nota e registro de dia daquele projeto | `Operações/OP <Nome>/Projetos/<projeto>/Processos/` |
| A OP nao tem projeto | `Operações/OP <Nome>/Processos/` |
| A nota descreve um processo da operacao inteira, nao de um projeto | `Operações/OP <Nome>/Processos/` (ex: funil, redes sociais, validacao de modelo) |

**Empate ou duvida:** vale `reuso_de_padrao_de_nota.md` - abra o `Processos/` e veja onde a
**nota irma mais recente** foi parar. O disco ganha do template.

**Regras do movimento:**

- **Preservar o nome do arquivo.** Renomear ao arquivar quebra o wikilink do `01_PRF` e das
  notas que apontam pra ela.
- **Mover, nunca copiar nem deletar.** O vault nao tem git.
- Nota de processo solta na pasta de tarefas tambem sobe (aconteceu com duas notas de 14/08).
- Depois de mover, conferir se algum wikilink ficou orfao.

---

### Passo 2.7: Conferir a afirmacao contra o sistema (OBRIGATORIO ao escrever COMO algo funciona)

*Gravado em 09/09/2026, aprovado pelo fundador.*

**Toda frase que afirma como o sistema funciona e conferida contra o sistema antes de virar
documento.** Vale para o `01_PRF`, a nota de entrega, a decisao estrategica e o plano - qualquer
nota que descreva mecanismo.

**O modo de falha, medido na OP Cameras:** quatro documentos do projeto afirmavam que cada
confirmacao humana virava exemplo de treino e que "a exatidao cresce com o uso". O codigo nunca fez
isso: a correcao era coletada, agregada e servida por um caminho pronto, e nunca chegava a
inteligencia artificial, que recebia sempre a mesma instrucao fixa.

Ninguem mentiu. As notas foram escritas a partir da **intencao de construir**, no momento em que a
decisao foi tomada, e a construcao parou no meio. **Documento assim nao levanta suspeita: ele parece
verdade e e lido como verdade**, inclusive por quem vai responder ao cliente com ele na mao.

**Como aplicar, sem virar auditoria de codigo:**

1. Se a frase diz o que o sistema FAZ, peca a confirmacao a quem construiu (`dev-expert`), ou
   confira a evidencia que a sessao produziu. Nao deduza do plano - plano e o que se pretendia.
2. Se nao der para conferir naquele momento, **escreva como intencao e nao como estado**: "vai
   passar a", "esta previsto", "decidido em DD/MM e ainda nao construido". A frase continua util e
   deixa de mentir.
3. Frase que descreve DECISAO nao precisa disso. "Ficou decidido que X" e verdadeiro assim que ele
   decide. O cuidado e so com afirmacao de mecanismo.

**Quando descobrir que um documento vivo afirma o que o sistema nao faz, corrija na mesma sessao**,
sem esperar o encerramento. Foi o que aconteceu em 09/09: o `01_PRF` recebeu a correcao no mesmo
turno em que o achado apareceu.

---

### Passo 3: mensagens.json

Depositar mensagem V2.1:
```json
{
  "id": "msg_[proximo_id]",
  "type": "handoff",
  "from": "assistente-expert",
  "to": "ceo-dodo",
  "subject": "Vault atualizado, [data]",
  "message": "Auto-archive concluido. Daily, entrega e logs atualizados.",
  "context": {
    "project": "[nome do projeto]",
    "artifacts": ["Operações/OP <Nome>/Projetos/<projeto>/03_Entregas/<DD-MM-AA>/<arquivo>.md", "Tarefas/<Mes>/OP <Nome>/<nota-de-tarefa>.md"],
    "next_action": "Nenhuma. Vault sincronizado."
  },
  "timestamp": "[ISO8601-Brasilia]",
  "status": "pending"
}
```

---

### Passo 4: registro_atividades.json

Atualizar o track atual para `"completed"`.

---

## Edge Cases

| Situacao | Acao |
|---|---|
| Pasta `03_Entregas/` nao existe | Criar silenciosamente |
| Nota de tarefa nao existe pro assunto | Criar em `Tarefas/<Mes>/OP <Nome>/` (Regra de Ouro 16) |
| Pasta da OP fora do padrao | Abrir a OP mais completa do vault e copiar a forma (`vault_structure.md`), nao inventar |
| SessionContext incompleto | Inferir campos da conversa, nunca perguntar |
| Multiplas entregas | Uma nota por entrega distinta |
| Sessao sem entrega tecnica | `template: "chat_only"`: so os passos 3 e 4, sem nota de entrega |
| Nenhum projeto foi tocado | Passos 1 e 2 nao se aplicam; rodar so os passos 3 e 4 |

---

## Confirmacao Final ao CEO

```
Auto-Archive concluido.
   Entrega: Operações/OP <Nome>/Projetos/<projeto>/03_Entregas/<DD-MM-AA>/<arquivo>.md
   Plano:   Tarefas/<Mes>/OP <Nome>/<nota>.md
   Estado:  01_PRF.md atualizado (ou "sem mudanca de funcionamento")
   mensagens.json: atualizado
   registro_atividades.json: track [N] → completed
```
