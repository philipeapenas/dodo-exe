# Regras de Ouro - Ecossistema Dodo.exe

Este arquivo e a **memoria compartilhada** entre os orquestradores (`CLAUDE.md`, lido pelo Claude Code, e `AGENTS.md`, lido pelo Codex e pelo Antigravity). Toda regra aqui vale para qualquer agente operando neste workspace, em qualquer IDE.

> O **fundador** e a pessoa dona deste workspace. A identidade dele (proposito, meta, principios, rotina) vive em `Vault/Vida Pessoal/Identidade.md` e so ele muda. Estas regras nao substituem as preferencias que ele configurar no proprio IDE: elas registram as decisoes permanentes do ecossistema, para que persistam no repositorio.

> **Numeracao estavel.** As skills citam as regras pelo numero. Regra nova entra no fim; regra aposentada vira "(aposentada)" e o numero nao e reaproveitado.

---

## 1. Regra do Ecossistema Onisciente (Treinamento e Contratacao)

Quando uma skill nao sabe executar uma funcao solicitada, ela aciona o `skill-expert` via `help`. O `skill-expert` age sobre o ecossistema inteiro:

1. Avalia qual skill existente tem o escopo mais proximo para absorver aquela habilidade e faz o treinamento (`upskill`) nela.
2. So quando nenhuma skill tem escopo compativel, cria e treina uma skill nova (`new_hire`).

> O fluxo detalhado de pesquisa, validacao com o fundador e aprovacao segue `.agents/skills/skill-expert/memory/training_protocol.md`.

---

## 2. Regra de Comunicacao

- Toda comunicacao inter-skill usa o protocolo definido em `messaging_protocol.md`.
- O campo `type` e obrigatorio em toda mensagem.
- Skills conversam diretamente, sem precisar do CEO como intermediario.

---

## 3. Regra Anti-Bypass de Interface

- O prompt livre do fundador no chat **DEVE** ser destilado para o `mensagens.json` do projeto (em `Projetos/<Dominio ou Localhost>/<Projeto>/Resumo do projeto/`, ou em `Agente Orquestrador/Resumo do projeto/` quando o trabalho e do proprio ecossistema) como passo inicial: a Ordem de Servico.
- O estado da tarefa e rastreado no `registro_atividades.json`; a comunicacao tatica entre skills acontece no `mensagens.json`.
- A documentacao de encerramento so acontece quando o fundador decreta o fim da sessao. O orquestrador compila as entregas no `session_summary.json`, e isso aciona a `assistente-expert` para escrever o resumo no vault.

---

## 4. Regra de Idioma

- Documentacao, planos, relatorios e comunicacao com o fundador: **Portugues sem acentuacao**.
- Codigo (variaveis, funcoes, configs internas): **Portugues sem acentuacao**.
- `SKILL.md`, playbooks, regras de ouro, orquestradores e qualquer `.md` que sirva de contexto para agente: **Portugues sem acentuacao**.

---

## 5. Regra de Testes (Sempre via curl)

- Teste de servidor e sempre via `curl` (no PowerShell, `Invoke-WebRequest`), nunca pelo navegador.

---

## 6. Regra de Automacao (Nao Duplicar Trabalho Automatizado)

Quando existe um script que automatiza uma tarefa, **USE O SCRIPT**. Executar na mao o que ja esta automatizado gera divergencia, desperdica tempo e quebra a fonte unica de verdade.

**Exemplos canonicos:**

- Gerar o `AGENTS.md`: rodar `python "Agente Orquestrador/tools/sync_orchestrators.py"`. **NUNCA** editar ele na mao: o `CLAUDE.md` e o master. Nao criar `GEMINI.md` na raiz: o Antigravity le os dois e carregaria o roteador em dobro.
- Espelhar as skills: `python "Agente Orquestrador/tools/sync_skills.py"` (`.agents/skills` e o master, `.claude/skills` e o espelho).
- Propagar o protocolo de mensagens: **sempre** que o `messaging_protocol.md` mudar, rodar `python "Agente Orquestrador/tools/sync_protocol.py"`. O orquestrador roda esse script, nao delega.

**Protocolo:**

1. Antes de editar na mao qualquer arquivo derivado ou sincronizado, verifique se existe script em `Agente Orquestrador/tools/` ou em `.agents/skills/<skill>/tools/`.
2. Se houver, rode o script. Se faltar capacidade nele, atualize o script, nao contorne.
3. Se for a primeira vez que um processo roda e nao ha automacao, considere criar uma (pergunte ao fundador antes de codar ferramenta nova).

---

## 7. Protocolo Karpathy (Principios de Execucao para Todas as Skills)

Principios de comportamento que valem para **todas** as skills, por cima das regras de cada `SKILL.md`. Reduzem os erros comuns de LLM em codigo, copy, planejamento e operacao.

> **Tradeoff explicito:** estes principios priorizam **cautela sobre velocidade**. Em tarefa trivial (trocar uma string, ajustar um padding), use bom senso e siga.

### §1 - Pense Antes de Executar

**Nao assuma. Nao esconda confusao. Exponha tradeoffs.**

- Declare as suposicoes. Se houver incerteza, **pergunte ao fundador**.
- Se existirem varias interpretacoes, apresente todas; nao escolha em silencio.
- Se houver abordagem mais simples, diga. Empurre de volta quando fizer sentido.
- Se algo nao esta claro, **pare**, nomeie o que confunde e pergunte.

### §2 - Simplicidade Primeiro

**O minimo que resolve o problema. Nada especulativo.**

- Sem feature alem do pedido.
- Sem abstracao para codigo de uso unico.
- Sem "flexibilidade" que ninguem pediu.
- Sem tratamento de erro para cenario impossivel.
- Se deu 200 linhas e cabia em 50, reescreva.

Teste mental: *um engenheiro senior diria que isso esta complicado demais?* Se sim, simplifique.

### §3 - Mudancas Cirurgicas

**Toque so no que precisa. Limpe so a sua propria bagunca.**

- Nao "melhore" trecho vizinho, comentario ou formatacao.
- Nao refatore o que nao esta quebrado.
- Siga o estilo existente, mesmo que voce faria diferente.
- Codigo morto ou copy velha fora do escopo: **mencione**, nao apague.
- Remova so os orfaos que **as suas** mudancas criaram.

**Criterio final:** cada linha alterada rastreia direto ao pedido do fundador.

### §4 - Execucao Orientada a Meta

**Defina o criterio de sucesso. Repita ate verificar.**

- "Adicionar validacao" vira "escrever teste para entrada invalida e fazer passar".
- "Corrigir o bug" vira "escrever teste que reproduz o bug e fazer passar".
- "Otimizar copy" vira "definir a metrica de comparacao antes de mexer".

Em tarefa de varios passos, declare um plano curto antes de agir:

```
1. [Passo] -> verificar: [check concreto]
2. [Passo] -> verificar: [check concreto]
```

Criterio forte permite seguir sozinho. Criterio fraco ("faca funcionar") obriga a reabrir a conversa o tempo todo.

---

## 8. Regra de Edicao dos .md do Ecossistema

`CLAUDE.md`, `AGENTS.md` e todo `.md` de memory ou de prompt de sistema (incluindo `regras_de_ouro.md`, `messaging_protocol.md`, `training_protocol.md`, qualquer `*/memory/*.md` e qualquer `SKILL.md`) so sao editados pela `skill-expert` ou pelo fundador. As outras skills propoem mudanca via `help` para a `skill-expert`.

---

## 9. Regra de Organizacao de Projetos

Todo projeto em `Projetos/` vive em **uma de duas** subpastas:

- **`Projetos/Dominio/`**: projeto com repositorio Git proprio e publicacao publica. Versionado de forma independente do workspace.
- **`Projetos/Localhost/`**: projeto sem repositorio proprio (roda local e e versionado junto do workspace).

**Convencoes obrigatorias:**

1. **Nome de pasta sem espaco e sem acento** (`site-cliente`, nao `Site do Cliente`). Espaco causa lock de arquivo no Windows e quebra caminho em script.
2. Todo projeto em `Dominio/` tem `tools/backup.bat` que faz `git add -A`, commit e `push origin main`. Modelo: `Agente Orquestrador/tools/backup_projeto.bat`.
3. Projeto em `Dominio/` fica fora do git do workspace (o `.gitignore` raiz ja ignora as subpastas de `Projetos/Dominio/`).
4. Caminho absoluto em config (`config.json`, tarefa agendada) reflete o caminho completo `Projetos/Dominio/<nome>/...` ou `Projetos/Localhost/<nome>/...`.

**Projeto novo:** decida primeiro se tera repositorio e publicacao proprios (`Dominio/`) ou se roda so local (`Localhost/`). **Nunca crie na raiz de `Projetos/`.**

**Promocao de Localhost para Dominio (obrigatoria, no mesmo turno da publicacao).** O gatilho e a publicacao publica, nao o dominio pago: subdominio gratuito (`.vercel.app` e similares) ja conta. Projeto no ar morando em `Localhost/` mente no nome da pasta.

Ritual da promocao:

1. Mover com `robocopy /MOVE /R:10 /W:2` (nao `Move-Item`): tolera lock transitorio de file watcher.
2. Corrigir o nome da pasta se ele nao for o da operacao (projeto que nasceu de copia costuma herdar o nome do dono original).
3. **Garantir o repositorio proprio no GitHub** (verificar e criar se nao existir). Detalhe abaixo.
4. Criar `tools/backup.bat` a partir do modelo.
5. Varrer o workspace pelo caminho antigo e atualizar **cada** referencia: nota do vault, `Resumo do projeto/`, memoria de skill.
6. Conferir que o vinculo com a hospedagem sobreviveu e que o site responde.

### O repositorio proprio

**Todo projeto que sobe para hospedagem publica sai do turno com repositorio proprio.** O agente verifica, cria e envia; nao entrega isso como tarefa pro fundador.

```
gh repo list --limit 100 | grep <nome>          # ja existe?
gh repo create <nome> --private --source=. --remote=origin --push
```

- **Privado por padrao.** Publico so se o fundador pedir.
- **Antes de enviar, varrer por segredo.** Procurar `service_role`, `sk_live`, chave de API, `.env` e JWT solto, e **conferir o papel** de cada token achado. Chave `anon` de Supabase e publica por natureza; `service_role` **nunca** vai.
- **`.gitignore` do projeto** exclui pelo menos `.vercel/` (guarda IDs de projeto e organizacao) e `__pycache__/`.

---

## 10. Regra de Planejamento Tecnico Obrigatorio

Antes de qualquer implementacao (feature nova, refator, bugfix nao trivial), o agente DEVE:

1. **Pedir contexto ao fundador** se o prompt nao trouxer escopo suficiente. Nao assuma.
2. **Fazer o deep-dive tecnico**: ler o codigo existente, mapear funcoes e estado envolvidos, citar arquivo e funcao exatos.
3. **Escrever o plano de implementacao** na nota de tarefa do vault (Regra 16): problema e contexto atual, mudancas por skill responsavel, funcao alvo e logica exata de cada mudanca, plano de verificacao.
4. **Aguardar a aprovacao do fundador** antes de executar.

**Por que:** plano raso gera entrega errada e retrabalho. O deep-dive antecipado da a cada skill uma especificacao cirurgica para acertar na primeira tentativa.

**Excecao:** tarefa trivial nao exige plano formal (Regra 7 §2).

---

## 11. Regra de Estilo de Escrita (Sem Emojis)

**Proibido em tudo que o ecossistema escreve:**

- Emoji decorativo em texto: nota do vault, doc, relatorio, heading, plano, `SKILL.md`, playbook.
- Emoji na interface de ferramenta interna: botao, rotulo, badge de painel e formulario operacional.

**Permitido:**

- Emoji em CONTEUDO de produto: legenda de post, copy de marketing, mensagem para o cliente final.
- Estilo terminal na interface: `[ Sair ]`, `[ + ]`, `[ x ]`.
- Unicode geometrico minimo quando funcional: `⋮⋮` (arrastar), `↑↓` (atalho), `<` `>`.

**Por que:** emoji e um dos sinais mais reconheciveis de texto gerado por LLM e quebra a leitura minimalista e profissional do ecossistema.

---

## 12. Regra de Autoaperfeicoamento por Postmortem

Toda skill que, durante uma tarefa, precisar corrigir um erro que **NAO estava documentado na propria `memory/`** (caminho desatualizado, bug de ferramenta, suposicao invalida, config que mudou) DEVE, alem de resolver e reportar ao fundador, mandar `help` ao `skill-expert` (fluxo de `upskill` do `training_protocol.md`) com:

1. O que deu errado.
2. A causa raiz.
3. A correcao aplicada.
4. Qual arquivo de `memory/` deveria mudar para a causa nao se repetir.

O `skill-expert` pesquisa se precisar, apresenta o playbook atualizado ao fundador e **so grava com aprovacao explicita**.

**Por que:** erro corrigido na hora e nao gravado e redescoberto do zero na semana seguinte. Meta: cada erro corrigido uma vez vira conhecimento permanente.

---

## 13. Regra de Escrita no Vault (Objetividade)

Toda nota no vault (`Vault/`) e escrita de forma **objetiva, em linguagem de negocio, SEM explicacao tecnica**.

> **Unica excecao: a nota de tarefa** (Regra 16), que carrega o plano de implementacao com detalhe tecnico completo.

**A nota contem:** o que passou a funcionar, o que quebrou e foi consertado, o que ficou pendente, o que precisa de decisao do fundador. Secoes curtas com titulo, frases diretas.

**Proibido na nota do vault:** bloco de codigo, comando de terminal, trecho de log, caminho de arquivo, nome de funcao, tabela de banco, endpoint, narrativa de como a solucao foi construida, emoji.

**Onde o detalhe tecnico vive:** na nota de tarefa (Regra 16) e no `mensagens.json` do projeto. O vault e onde o fundador **consulta o que aconteceu**, nao onde estuda como funciona.

**Roteamento:** antes de criar nota nova, procure em `Vault/Tarefas/<Mes>/` se o fundador ja abriu nota para o assunto. Se abriu, o resultado vai **na nota dele**, abaixo do que ele escreveu, sem alterar o texto dele.

---

## 14. Regra de Encerramento por Projeto (sempre pela assistente-expert)

Toda sessao que tocar algum projeto encerra passando pela `assistente-expert`, mesmo que o fundador so diga "finalizamos". Ela roda o `auto_archive_protocol.md`, que garante os documentos do projeto no vault atualizados:

- **Plano de implementacao**: vive na nota de tarefa (Regra 16); no encerramento, confirmar que ela reflete o que a sessao mudou.
- **Documento de estado** (`01_PRF.md`): corrigido quando a sessao mudou COMO o projeto funciona.
- **Nota de entrega** em `03_Entregas/`.

A fonte do que mudou e o `mensagens.json` + `session_summary.json`, nao a memoria da conversa.

**Escopo:** so esses tipos de `.md`. `README.md`, `SKILL.md`, orquestradores e `*/memory/*.md` ficam onde estao (Regra 8).

**Por que:** documento de estado desatualizado e pior que documento inexistente, porque parece verdade. Esta regra existe para o fundador nunca gastar tempo descobrindo defasagem de documento.

---

## 15. Regra de Plugin Sob Demanda (Custo Fixo de Contexto)

Plugin que cobra **custo fixo de contexto** (skill sempre ligada, hook de inicio de sessao, roteador permanente) fica **DESATIVADO por padrao**. Liga quando o fundador vai trabalhar naquele dominio e desliga ao terminar.

1. Quem vai trabalhar no dominio **ativa antes de comecar** e avisa o fundador que ativou e por que.
2. Ao concluir, **desativa de novo**.

```
claude plugin enable <plugin> --scope project
claude plugin disable <plugin> --scope project
```

**Fora do escopo:** servidores MCP. As ferramentas de MCP carregam sob demanda e o custo de contexto e baixo; eles ficam ligados. Servidor MCP que leva chave de API e registrado em escopo local, fora do repositorio.

**Por que:** contexto gasto com manual de ferramenta que nao esta em uso e contexto roubado do trabalho real da sessao.

---

## 16. Regra do Registro Unico da Tarefa

O **plano de implementacao vive DENTRO da nota de tarefa do vault**, nao em arquivo solto no projeto. **Nao se cria `implementation_plan.md` em `Projetos/`.**

**Onde:** `Vault/Tarefas/<Mes>/<OP>/<Titulo> DD-MM-AA.md`, a nota que o fundador abre para a tarefa.

**O que a nota carrega, do inicio ao fim:**

1. **Objetivo** e link para a nota de contexto que originou.
2. **Registro do processo**: o que aconteceu em ordem (alinhamento, achados que mudaram o rumo, decisoes, ajustes pedidos pelo fundador). E a memoria de POR QUE o desenho ficou assim.
3. **Decisoes travadas**, cada uma com a consequencia direta.
4. **Achados de pesquisa**: o que foi verificado E o que foi descartado, com o motivo.
5. **Arquitetura**: o corte de responsabilidade entre as pecas.
6. **Fases**, cada uma com criterio de verificacao concreto.
7. **Riscos aceitos** pelo fundador.
8. **Pendencias**: o que falta e de quem depende.

**EXCECAO EXPLICITA A REGRA 13:** nesta nota o detalhe tecnico **e permitido e desejado** (tabela, esquema de banco, parametro, endpoint, caminho de arquivo).

**Por que:** a nota de tarefa e onde o fundador vai estudar **como** a tarefa funciona. Aplicar a Regra 13 aqui apagaria o conhecimento tecnico junto, e achado que custou horas seria redescoberto do zero.

---

## 17. Regra do Segundo Cerebro (o vault e o neuronio, a memory e o ponteiro)

O vault e o **segundo cerebro** do fundador e do ecossistema. A `memory/` de uma skill guarda **INTERPRETACAO** (o que uma coisa significa, que peso tem, de onde veio). O vault guarda o **VALOR ATUAL**. Nunca confunda os dois, e nunca copie um dentro do outro.

### As notas de `Estudos/` sao os neuronios

`Vault/Estudos/` e onde vive a **definicao do que uma coisa E**. Nao e material de leitura: e a especificacao executavel do bloco de trabalho.

**Antes de executar um bloco da rotina do fundador, a skill LE a nota de estudo que define aquele bloco.** E ela que diz quais sao os pilares, em que ordem e o que cada um cobre. Exemplo de como isso aparece:

| Bloco da rotina | Neuronio que define (exemplo de nome) |
|---|---|
| Gerir ativos | `Estudos/Areas da Vida/Financeiro/O que e gerir ativos DD-MM-AA.md` |
| Auto gestao | `Estudos/Areas da Vida/Auto Conhecimento/O que e auto gestao DD-MM-AA.md` |

A nota da semana e a autopsia do dia citam o neuronio por wikilink com ancora de bloco (`[[O que e auto gestao DD-MM-AA#^gestao-do-tempo]]`). Esse link e a instrucao de qual pilar esta sendo executado naquela hora.

### As tres leis

1. **Aponte, nunca copie.** Memoria de skill referencia o caminho e a ancora. Copia desatualiza em silencio no dia em que o fundador reescreve a nota; ponteiro nunca desatualiza.
2. **Falta de ancora se resolve criando a ancora** dentro da nota de estudo (`^slug` na linha do pilar), nunca duplicando o texto dentro da skill.
3. **Conhecimento novo declarado pelo fundador tem dois destinos.** O que e dele (auto conhecimento, principio, definicao) vira nota no vault, escrita pela `assistente-expert`. O que e de execucao (fluxo, padrao de nota, ordem de acionamento) vira ponteiro na `memory/` da skill que executa, escrito pela `skill-expert`.

**Por que:** proposito, meta e principios mudam. Qualquer valor congelado em arquivo de skill fica errado em poucas semanas; ponteiro para o vault nao fica.

---

## 18. Regra do Bloco de Operacao (o ritual de abertura e o gatilho de execucao)

Todo bloco de operacao de um ativo abre pelo mesmo ritual, que e o checklist de abertura da nota do dia:

```
1. Analisar plano da meta do dia
2. Criar plano do dia
3. Otimizar documentos da operacao
```

**Confira o checklist no disco antes de escrever a nota.** O fundador mexe nesta lista; a nota mais recente e sempre a fonte, nunca a ordem decorada daqui.

**Por que "Otimizar documentos" e o ULTIMO item:** e o plano fechado que diz o que os documentos precisam registrar. Escrever antes obriga a reescrever depois.

### O que "Otimizar documentos da operacao" cobre, em ordem

1. **Decisao estrategica** da OP, se mudou.
2. **Plano do dia**: o que existe, terminado; nunca um plano novo para trabalho ja planejado.
3. **Nota do dia** em `Vault/Tarefas/<Mes>/<OP>/`.
4. **Documento de estado** (`01_PRF.md`), quando a sessao mudou COMO o projeto funciona.
5. **Autopsia do dia**, nas tarefas de gerir ativos: o alvo da operacao e os links do que foi produzido, aninhados embaixo da tarefa.

**Atencao ao dono do texto:** o bloco do dia MUDA DE CASA. Enquanto o dia corre ele mora na autopsia, e a nota da semana fica so com o ponteiro. Pergunte ao `cofre.bloco_do_dia()` da `dodo-ia` onde ele esta antes de escrever.

### Quem faz cada parte (a cadeia nao pula etapa)

| Skill | O que entrega | O que NAO faz |
|---|---|---|
| `dodo-ia` | Le o vault (Identidade, Semana, autopsia do dia, Ativos, decisao estrategica vigente), levanta o estado real da operacao e entrega **criterio** | Nao escreve nota. Nao decide a meta sozinha |
| `ceo-dodo` | Roda o `strategic_os` na meta: restricao real, ROI, onde cortar. Especifica **exatamente** o que deve ser anotado | Nao escreve nota. Nao executa |
| `assistente-expert` | **Escreve**, depois de ler a nota irma mais recente do mesmo tipo | Nao inventa a meta. Nao pula o CEO |

### A hierarquia que o ritual produz

**decisao estrategica -> plano -> nota do dia -> entrega.** Cada nota responde uma pergunta diferente: por que, como, o que aconteceu hoje, o que ficou pronto.

### O GATILHO DE EXECUCAO

Depois do ritual, quando o fundador disser **"perfeito, aplique o plano do dia"** (ou equivalente), a fase de documento esta FECHADA e a execucao comeca.

- **NAO** repropor o corte, nem reabrir decisao ja travada.
- **NAO** pedir aprovacao item a item. O plano do dia na nota **e a ordem de servico**.
- **NAO** refazer o levantamento de estado.
- Executar na ordem do plano, registrando o resultado na nota do dia.

**A unica coisa que interrompe a execucao** e um achado que ameace **dado, dinheiro ou o ar da operacao**. Qualquer outro achado vira `> Ajuste no plano do dia`, numerado, dentro da nota, e a execucao segue. Nunca apagar o que o fundador escreveu.

**Por que:** o ritual de abertura custa tempo real do bloco. Reabrir o escopo depois do plano aprovado gasta o mesmo tempo duas vezes.

### O plano em execucao volta pra meta do dia

Quando a execucao comeca, o plano e linkado dentro do bloco do dia, aninhado sob o pilar do neuronio que ele serve, com **estimativa e tempo real por processo**:

```
- [[O que e gerir ativos DD-MM-AA#Ciclo de Vida]] - 3h:
    - [[<decisao estrategica> DD-MM-AA]] - 3h:
        - [[<Plano ...> DD-MM-AA]]
            - 1. <processo em linguagem de negocio> (45m → ):
            - 2. <processo> (1h → ):
```

A estimativa ao lado do real e o unico jeito de a estimativa parar de ser chute. Um processo pode cair em pilares diferentes: distribua pelo pilar que ele serve de verdade.

---

## 19. Regra do Desenho Antes do Codigo

**Antes de construir ou reformar qualquer interface, publique um desenho da tela e mostre ao fundador.** Vale para painel, landing page, formulario, dashboard, app.

**O que o desenho e:**

* Uma pagina de verdade, que ele abre e navega. Nao e descricao em texto.
* **Construida sobre o sistema visual que ja existe**: cor, tipo, raio e espacamento saem do CSS do produto.
* Com **dado de exemplo no formato do dado real**, dizendo no topo que aquilo e desenho e nao o que esta no ar.
* Com o que e **novo marcado**.

**A cadeia:**

```
frontend-expert   pesquisa referencia real ANTES de desenhar (galeria de
      |           painel, biblioteca de componente, banco de conceito visual).
      v
   desenho        o fundador VALIDA na prancheta antes de existir codigo.
      v
frontend-expert   CSS.   dev-expert   JS.   Nessa ordem.
```

### O desenho leva TODAS as telas, nao uma

* **Uma prancheta por tela do sistema**, com os estados que mudam a leitura.
* **Cada tela no estado REAL, nao no estado feliz.**
* **Computador E celular no mesmo artefato.**
* **Numero derivado mostra a conta na tela** ("599 na esteira / 3 por dia", nao "199 dias" solto).

### A fonte e regra de criacao de sistema

* **Montserrat e o default do papel de leitura** em artefato, prancheta e projeto novo, com fallback declarado: `'Montserrat', 'Segoe UI', system-ui, sans-serif`.
* **Duas familias com papeis separados**: uma para texto corrido e dado, outra para titulo e rotulo.
* **Excecao:** prancheta que retrata sistema real usa, dentro do quadro, a fonte do sistema retratado.
* **Precedencia:** palavra do fundador > sistema visual que ja existe no projeto > este default.
* **Numero em coluna leva `font-variant-numeric: tabular-nums`.**

**Por que:** alinhamento de layout custa minutos no desenho e horas depois de construido, e o fundador decide melhor vendo do que lendo.

---

## 20. Regra da Skill como Saida do Plano (todo processo repetivel ganha dono)

**Todo plano do dia aplicado carrega tambem a meta de criar ou treinar uma skill que rode aquele processo, sempre que o processo for repetivel e ainda nao tiver skill dona.**

Ao fechar cada processo do plano:

1. Esse processo vai se repetir? Ja existe skill que o executa?
2. **Repete e nao tem dono:** `help` para `skill-expert` pedindo Nova Contratacao (ou Treinamento, se uma skill vizinha ja cobre o escopo). Nao codar automacao solta fora desse fluxo.
3. **Repete e ja tem dono:** o plano so registra qual skill assume.
4. **Tarefa unica:** nao cria skill (Regra 7 §2).

**Quem decide se repete:** o criterio de negocio do fundador. Na duvida, pergunte.

---

## 21. Regra de Estilo de Escrita (Sem Travessao)

Nada que o ecossistema escreve leva travessao (o traco longo). Troque por virgula, dois pontos, parenteses ou ponto final.

**Onde vale:** em TUDO. Nota do vault, playbook, `SKILL.md`, documento, artefato, copy de cliente e resposta no chat.

**Por que:** atrapalha a leitura corrida e e um dos sinais mais reconheciveis de texto gerado por LLM (mesmo motivo da Regra 11).

**Como aplicar:** varrer o texto atras de travessao antes de entregar.

---

## 22. Regra do Processo que Volta (a nota de processo e escrita pelo time)

**Toda sessao que rodar com o time um processo que vai se repetir nutre a nota de processo no vault, no encerramento.** Quem escreve e a `assistente-expert`, dentro do `auto_archive_protocol.md`. O fundador nao escreve essas notas a mao.

**Onde:** `Vault/Processos/<Area ou OP>/<Nome do processo> DD-MM-AA.md`, no formato de `templates/template_processo.md` da `assistente-expert`.

**A nota carrega o FLUXO, nao a tecnica:** 3 a 6 passos numerados na linguagem do fundador, quem faz cada um quando nao for obvio, e o tempo real quando houver. A tecnica e das skills especializadas, que devem saber fazer cada coisa pelo treinamento que receberam.

**Consequencia:** quando faltar tecnica, o destino e treinamento da skill responsavel via `skill-expert` (Regra 1), nunca paragrafo explicativo na nota de processo.

**Nutrir a existente e o padrao.** Nota nova so quando o fluxo mudou a ponto de virar outro processo, linkando a anterior.

**Quem consome:** a `dodo-ia` le essa pasta para saber se um processo pedido no chat ja foi feito antes, e com qual fluxo, antes de conduzir do zero.

**Por que:** processo que depende da mao do fundador para ser registrado nao e registrado.

---

## 23. Regra do `npm run dev` (todo projeto sobe com o mesmo comando)

**Todo projeto com alguma coisa para ver em localhost responde a `npm run dev`.** Um comando so, igual em todos, escondendo a stack por baixo.

| O projeto e | O `dev` chama |
| --- | --- |
| Framework (Next, Vite) | o dev server do framework (`next dev`, `vite`) |
| Tem pasta `api/` (funcoes) | `node "<workspace>/Agente Orquestrador/tools/dev_local.js"` |
| Site estatico | o mesmo lancador, com a subpasta quando houver (`... dev_local.js site`) |
| Tem servidor proprio | o arquivo dele (`node servidor.js`, `python app.py`) |

O lancador `Agente Orquestrador/tools/dev_local.js` cobre os casos sem dev server: projeto com funcoes (chama a CLI da Vercel, que serve arquivos E roda funcoes) e site estatico (servidor embutido). Porta padrao 3000, trocavel com `npm run dev -- --porta 3001`.

**A armadilha:** em projeto com `api/`, o `dev` NAO pode ser `vercel dev`. A CLI le o proprio script `dev` do `package.json`, ve que ia chamar a si mesma e **aborta com "must not recursively invoke itself"**, sem dizer que a culpa e do nome do script. Por isso o lancador chama o `vc.js` da CLI direto.

**Site estatico ja publicado sem `package.json`:** criar o arquivo muda como a hospedagem enxerga o projeto; nesses casos o `package.json` entra no `.vercelignore`.

**Nao se aplica** a projeto sem localhost: raspador, bot, worker, automacao agendada.

**Por que:** o fundador nao pode depender do agente para subir o proprio ambiente.
