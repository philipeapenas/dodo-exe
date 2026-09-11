# Template - Nota de retomada de OP

Formato canonico da nota de trabalho do dia em Tarefas/<Mes>/<OP ou Operacao>/<Titulo> DD-MM-AA.md.
Confirmado em uso real em pelo menos duas OPs e ajustado com o fundador. Aplica-se a qualquer nota que sirva pro fundador retomar o trabalho
numa operacao - seja dia de so revisao, seja dia de execucao tecnica de verdade.

## Esqueleto

```
Contexto: [[Tudo sobre <OP> DD-MM-AA]]

**Meta do dia:** [[<decisao estrategica> DD-MM-AA]]
**Plano do dia:** [[<Plano ...> DD-MM-AA]]
**Ultima entrega:** [[link]] - leia esta primeiro, e o relatorio de onde o projeto parou
**Entrega anterior:** [[link]]                   (so se existir)
**Registro do dia anterior** (arquivado na pasta da OP): [[link]]   (so se ja existir dia anterior arquivado)

---

## Onde paramos

Paragrafos corridos, nao lista. Cobre: ultimo dia de trabalho, o resultado alcancado, o que
trava agora, o que falta pra virar dinheiro/valor, e qualquer aviso herdado de sessao anterior
que ainda vale.

---

## Pendencias abertas

| Pendencia | Depende de | Desbloqueia o que |
|---|---|---|

---

## Fases restantes

## Trabalho de hoje - DD/MM

Processos: <o papel que o fundador veste no bloco, tirado de "Quem sou" na Identidade>
- [ ] Analisar plano da meta do dia
- [ ] Criar plano do dia
- [ ] Otimizar documentos da operacao

**Meta**: 

**Plano do dia** (os pontos alinhados pelo fundador; o detalhe embaixo de cada um e o que o
time executa):

**1. <Ponto macro que o fundador alinhou>**
- <detalhe de execucao>
- <detalhe de execucao>

**2. <Ponto macro>**
- <detalhe de execucao>

**Fica fora do bloco de hoje:** <o que existe, continua valido e nao entra hoje>

---

## Adiantamento - <assunto> (DD/MM)

<achado principal em uma ou duas frases>

1. <passo>
2. <passo>

**Fontes:** <link ou caminho consultado>

---

## Relatório de execução - DD/MM

**Relatório de execução:** [[Relatorio de execucao - <Nome do plano> DD-MM-AA]]

- **Nota de entrega:**
	- Seção 1: [[<slug-da-entrega>-DD-MM-AA]]

- **Desenho aprovado da tela:**
	- Seção 1: <link do artefato>
```

## A secao Adiantamento (formalizada em 29/08/2026)

E uma secao **reconhecida e opcional** da nota do dia. Entra quando o plano ja esta escrito e
algum passo dele tem mecanica incerta: em vez de comecar a executar e descobrir no meio, a
pesquisa roda na mesma sessao e o resultado vira esta secao.

- **Uma secao por assunto pesquisado**, com o assunto no titulo e a data.
- **Formato fixo:** achado principal, passo a passo numerado, fontes citadas.
- **Ela nao fica sozinha:** depois de escrita, a decisao estrategica e o plano sao ATUALIZADOS
  pra refletir o que a pesquisa corrigiu. Adiantamento que nao corrige o plano nao serviu.
- **Quem pesquisa:** sistema externo fica com quem estiver no papel de dodo-ia ou ceo-dodo;
  codigo interno vai pro dev-expert, que escreve a secao tecnica ele mesmo.
- Regra completa e o precedente medido em `.agents/skills/dodo-ia/memory/gerir_ativos_playbook.md`,
  secao 2.2.

Nota que nao teve adiantamento simplesmente nao tem a secao. Nunca deixar o titulo vazio.

## Regras de cada secao

**Bloco de topo - reescrito pelo fundador em 24/08/2026.** Ele trocou "Meta da semana" e
"Plano do projeto" por **Meta do dia** e **Plano do dia**, e mandou que isso vire o padrao.
A regra por tras:

* **A meta do dia E a decisao estrategica do dia.** Aponta pra
  `Operações/OP <Nome>/Decisões estratégicas/<decisao> - <Projeto> - DD-MM-AA.md` (nome padrao
  desde 10/09/2026). Nao se escreve meta
  em texto solto no topo - ela ja existe como nota datada, com consequencia declarada.
* **O plano do dia nasce da meta do dia.** Aponta pra `Operações/OP <Nome>/Planos/`, no
  formato de `template_nota_de_plano.md`. Se a nota de plano ainda nao existir, ela e
  criada ANTES - pelo fluxo dodo-ia -> ceo-dodo -> assistente-expert.
* A cadeia de leitura completa vira **decisao estrategica -> plano -> nota do dia ->
  entrega**: por que, como, o que aconteceu hoje, o que ficou pronto.

So entra o link que existir de verdade - nunca criar nota nova so pra preencher o campo.
"Processos de apoio" NAO faz parte do esqueleto padrao (removido em 21/08/2026); linkar
apoio direto no corpo de "Onde paramos" quando fizer sentido.

**"Registro do dia anterior (arquivado na pasta da OP)" e literal: a nota anterior E movida.**
**So a nota do dia corrente fica em `Tarefas/<Mes>/`, todas as anteriores vao pra
`Processos/`.**

**O nivel da pasta varia por OP, e o disco desempata.** Pode ser
`Operações/OP <Nome>/Processos/` (nivel OP) ou
`Operações/OP <Nome>/Projetos/<projeto>/Processos/` (nivel projeto). **Antes de mover, abra a
OP e veja onde as irmas foram parar.** Nao inventar a pasta.

**Duas armadilhas que ja geraram conclusao errada:** OP com sessao ainda aberta nao
arquivou nada, e isso nao prova que a regra nao vale; e `Processos/` tambem guarda nota de
processo de verdade, entao achar processo na pasta nao significa que registro de dia nao va pra la. Preservar o
nome do arquivo ao mover - renomear quebra o wikilink.

**Rotulo do checklist:** `Processos: <papel>`, onde o papel e a definicao que o fundador da de
si mesmo em `## Quem sou:` da Identidade. Quando ele muda a definicao, o rotulo muda junto.

**Ele mexe nesta lista, e ja mexeu duas vezes: confira a nota mais recente no disco antes
de escrever** (`reuso_de_padrao_de_nota.md`), nunca a ordem decorada deste template.

* **24/08/2026** - encolheu pra tres itens. Saiu "Ler relatorio de onde paramos", e o
  primeiro virou "Analisar plano da meta do dia": a leitura do estado continua
  acontecendo, so deixou de ser passo separado.
* **09/09/2026** - "Otimizar documentos da operacao" trocou de lugar com "Criar plano do
  dia" e foi para o fim. E o plano fechado que diz o que os documentos precisam
  registrar; escrever antes obriga a reescrever depois. Naquele dia a decisao estrategica
  e a nota do dia foram escritas, o corte foi reprovado por ele, e as duas foram refeitas
  inteiras. **Consequencia pra esta skill: escrever os documentos e o ULTIMO passo do
  ritual, nao o do meio.**

**"Otimizar documentos da operacao" inclui a AUTOPSIA DO DIA.** Nao basta escrever a nota de tarefa e o PRF: as tarefas de `Gerir ativos` na
autopsia recebem o alvo da operacao e os links do que foi produzido, aninhados embaixo. Ver a Regra
de Ouro 18, secoes "O que Otimizar documentos da operacao cobre" e "O plano em execucao volta pra
meta do dia".

**Cuidado com o dono do texto:** desde 07/09/2026 o bloco do dia mora na AUTOPSIA enquanto o dia
corre, e a nota da semana fica so com o ponteiro. Pergunte ao `cofre.bloco_do_dia()` antes de
escrever, nunca assuma o arquivo.

**Quando os tres itens estiverem marcados, a fase de documento fechou.** O que vem depois
e o gatilho de execucao da Regra de Ouro 18: ao ouvir "perfeito, aplique o plano do dia",
executar sem reabrir escopo.

**Pendencias abertas.** Tabela sem coluna de numeracao. Terceira coluna e sempre framing
positivo - o que a pendencia resolvida desbloqueia, nao o que ela trava.

**Fases restantes - OPCIONAL, so quando existir "Plano do projeto" linkado no topo.** Puxada
direto de la: lista as fases que o plano define e que ainda NAO foram concluidas, com o
criterio de verificacao que ja estiver escrito no plano. Nao inventar fase nova aqui - so
refletir o que o plano ja define como restante. Sem plano formal, a secao nao entra.

**Plano do dia em dois niveis - aprovado pelo fundador em 28/08/2026.** O plano deixa de ser
lista unica. Os PONTOS MACRO sao os que ele alinha na conversa e formam a espinha; o DETALHE
DE EXECUCAO fica aninhado embaixo de cada ponto. O porque: os pontos que ele alinha servem pra ele ficar ciente; o resto do plano e o que
da assertividade quando o time for aplicar o trabalho. A regra: **o que ele
alinha nao apaga o detalhe que a skill levantou** - vira o cabecalho dele. Nunca colapsar os
dois niveis num so, e nunca jogar fora o detalhe porque ele resumiu em quatro linhas.

**Orcamento - REMOVIDO em 09/09/2026.** A linha de orcamento saiu da nota de tarefa por decisao
do fundador. **Nao recolocar.** O tamanho do bloco ele
ve na rotina do dia, que ja carrega hora e duracao de cada tarefa; repetir na nota de tarefa era o
mesmo dado em dois lugares, e o da rotina e o que ele edita.

O que NAO saiu junto e continua obrigatorio: o **criterio de corte**, logo abaixo. Ele responde uma
pergunta diferente - nao quanto tempo tem, e sim o que cede quando o tempo acaba.

**Criterio de corte - declarado ANTES da execucao, dentro de `Decisoes travadas hoje`.** Qual
ponto do plano cede se o bloco estourar, e o porque em uma linha. Existe pra ele nao decidir
isso cansado no fim do bloco. Formato: "se as 22h30 chegarem com algum ponto aberto, quem cede e o 3, nunca
o 1 e o 2", seguido da razao.

**`Fica fora do bloco de hoje` - fecha o Plano do dia.** Lista curta do que continua valido e
nao entra hoje. Nao e pendencia (a tabela ja cobre isso): e o corte explicito do dia, pra o
item nao voltar como duvida no meio do bloco.

**Trabalho de hoje - NUNCA e condicional.** Sempre a ultima secao, sempre nesta posicao. E o
gatilho que o fundador usa pra comecar a trabalhar.

- **Deposito de so levantamento/revisao** (skill nutriu a nota fora de um bloco de execucao
  do fundador): entra com os campos em branco e o checklist desmarcado, exatamente como no
  esqueleto acima. E o fundador quem preenche antes de comecar.
- **Dia de execucao real** (o fundador ja rodou os processos e a skill/ele trabalhou): o
  checklist fica marcado, Meta e Plano do dia preenchidos, e entram ainda
  `### Decisoes travadas hoje` (tabela: Decisao | Escolha | Consequencia direta) e
  `### Registro do processo - DD/MM` (paragrafos narrando o que aconteceu, achados e
  decisoes tomadas na hora).
**Relatório de execução - o fecho da nota, escrito pelo fundador em 27/08/2026.** Ele reescreveu esta secao por cima da versao que a skill tinha deposto, e o corte dele e a regra:

* **E um INDICE DE LINKS, nao narrativa.** A versao anterior trazia "o que mudou no escopo", "pendencias que ficam" e "pendencias que se resolveram", ele apagou tudo. Esse conteudo ja vive no relatorio de execucao e na nota de entrega; repetir aqui cria tres versoes da mesma coisa pra desatualizar em ritmos diferentes. **A nota do dia fecha apontando, nao recontando.**
* **A data do titulo e a do DIA da nota** (`## Relatório de execução - 26/08` numa nota `Retomada 26-08-26`), nao a do dia em que a sessao foi encerrada. Ela pertence ao dia que a nota registra.
* **O relatorio de execucao entra como linha unica em negrito.** Um so, porque e um por plano.
* **Entrega e desenho entram como lista aninhada, indexada por seção.** E o que faz a secao ACUMULAR: a sessao seguinte acrescenta `Seção 2:` embaixo de cada uma, em vez de sobrescrever. Sem o indice, a segunda sessao apagaria o rastro da primeira.
* **Escreva `Seção N` como ele escreve.** O disco ganha do template (`reuso_de_padrao_de_nota.md`); nao "corrija" a nota dele.
* Bloco que nao existir naquela sessao simplesmente nao entra, nunca deixar rotulo vazio esperando preenchimento.

Substitui o antigo `Entrega do dia:` opcional, que linkava so uma coisa e nao acumulava.

## Referencias

- A referencia viva e a nota do dia mais recente e mais completa de qualquer OP do vault
  (`reuso_de_padrao_de_nota.md`).
- Ajustado com o fundador: tirado "Processos de
  apoio" do bloco de topo, Pendencias abertas simplificada (sem numeracao, ultima coluna virou
  "Desbloqueia o que"), Fases restantes amarrada ao Plano do projeto, e Trabalho de hoje sem
  campo de Prazo.
- O plano em dois niveis, o orcamento, o criterio de corte e o `Fica fora do bloco de hoje`
  foram aprovados pelo fundador como padrao das proximas notas.
- A secao de fecho segue o formato que o proprio fundador escreveu por cima da versao da
  skill: e a referencia do encerramento de sessao. Ver tambem
  `template_relatorio_de_execucao.md`, que e a nota pra onde este fecho aponta.
