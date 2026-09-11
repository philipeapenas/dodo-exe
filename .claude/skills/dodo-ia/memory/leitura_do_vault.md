# Leitura do Vault - de onde vem o estado vigente

**Versao:** 3.0 | **Data:** 08/09/2026 | **Owner:** dodo-ia

Este playbook diz exatamente onde ler o que o fundador pensa HOJE. Ele existe por
um motivo medido no fundador que criou este sistema: em dois meses o proposito dele
mudou cinco vezes e a meta foi multiplicada por cinco. Qualquer valor congelado em
arquivo de skill fica errado em duas semanas.

**Divisao de responsabilidade:** este playbook e o `identidade_e_principios.md`
guardam a INTERPRETACAO (o que cada principio significa, que peso tem, de onde
veio). O vault guarda o VALOR ATUAL. Nunca confunda os dois.

---

## 1. Cinco notas, cinco relogios

Ate 18/08/2026 tudo morava numa nota so: a autopsia do dia, de ~22 KB, copiada
inteira todo dia. O fundador reorganizou em 18-19/08/2026 porque tres relogios
diferentes estavam no mesmo arquivo - identidade (muda quando ele decide), listas
que acumulam (mudam quando entra item novo) e o diario (muda todo dia). Hoje sao
cinco notas, e **cada campo tem UMA casa**:

| Nota | Caminho | Muda quando | O que tem |
|---|---|---|---|
| **Identidade** | `Vault/Vida Pessoal/Identidade.md` | ele decide mudar | Proposito, Meta, Medalha, Proposito Maior, Dons, Talentos, Principios, Habitos (Rotina mestre + Principios de conduta, ver secao 1.1), Recursos/Habilidades |
| **Ativos** | `Vault/Vida Pessoal/Ativos.md` | entra ou sai operacao | Operacoes que ele toca, agrupadas: decisoes estrategicas, projetos, ferramentas |
| **Semana** | `Vault/Vida Pessoal/Semana/Semana DD-MM-AA.md` | uma por semana | Metas de Ano, Mes e os 7 dias (com o esqueleto de horario, checkbox e tag de area - a FONTE do que ele fez) + Pendencias, Ideias, Desejos, Perguntas |
| **Autopsia do dia** | `Vault/Vida Pessoal/Rotina/<Mes>/Autopsia das intencoes DD-MM-AA.md` | todo dia | Meta do dia, Metas (embed), Rotina e tarefas de hoje (embed), Pendencias / Perguntas / Desejos (embed), Insights. **Ate 29/08/2026** tinha o checklist "Rotina nas 7 areas da vida" (placar `N/M`) - saiu em 30/08/2026, ver secao 1.1. **Ate 01/09/2026** tinha a Resolucao de Problemas - saiu em 02/09/2026, ver secao 1.2. |
| **Insights Geral** | `Vault/Insights/Insights Geral.md` | no fechamento do dia | Conhecimento tirado da experiencia dele, por tema |

**Onde ler cada campo:**

| Campo | Nota | Formato |
|---|---|---|
| Proposito Definido, Meta, Medalha, Proposito Maior | Identidade | linha de citacao `> Campo: valor`; Medalha e Proposito Maior continuam em `> - item` abaixo |
| Dons, Talentos, Principios, Habitos, Recursos/Habilidades | Identidade | `### <Secao>` seguida de lista |
| Rotina mestre (com horario) | Identidade | `#### Rotina mestre (com horario)` dentro de Habitos - ver secao 1.1 |
| Metas de Ano e de Mes | Semana | `#### Ano` / `#### Mes` |
| Tarefas do dia (com horario, checkbox, tag de area) | Semana | `#### <Dia>`, `> Meta do dia:` e `> Acordar:` logo abaixo, blocos com tag de area |
| Pendencias, Ideias, Desejos, Perguntas | Semana **ou** Autopsia do dia | `### <Secao>`. Elas VIAJAM: ver secao 1.5. Pergunte ao `cofre.dono_da_secao()`, nunca assuma |
| Meta do dia da autopsia | Autopsia do dia | `### Meta do dia:` (copiada da Semana na criacao) |
| Placar/adesao da area | **Semana**, nao mais a Autopsia (desde 30/08/2026) | fracao de checkbox `#area` feito/total no bloco do dia; ver `tools/dissecar_autopsia.py` (secao "Adesao por area pos-reestruturacao") e `tools/equilibrio_das_areas.py` |
| Metas de Ano, Mes e Semana | Autopsia do dia | `### Metas:`, com TRES embeds da Semana nesta ordem: `#### Ano`, `#### Mes`, `#### Semana - por prioridade`. Ano e Mes entraram em 07/09/2026 - o corte de 31/08 era contra arrastar o `### Metas:` inteiro, nao contra o conteudo. Continuam embed porque ele so LE essas secoes durante o dia |
| Rotina e tarefas do dia | Autopsia do dia **enquanto o dia corre**, Semana fora dele | `### Rotina e tarefas de hoje:` na autopsia, `#### <Dia>` na semana. **Nao e mais embed** desde 07/09/2026: o texto MUDA DE CASA. Ver secao 1.5 |
| Resolucao de problemas | Semana **ou** Autopsia do dia | `### Resolucao de Problemas:` na semana guarda um item por dia (`- <Dia>:`); em 07/09/2026 esse ITEM passou a viajar pra autopsia junto com o resto do dia. A secao continua morando na semana - o que viaja e a linha do dia. Ver 1.2 e 1.5 |
| Insight cru do dia | Autopsia do dia | `### Insights:` |
| Conhecimento consolidado por tema | Insights Geral | `## <Tema>` |

### 1.1 A rotina mestre (desde 30/08/2026)

O `### Habitos` de Identidade virou duas partes - **nunca confunda as duas**:

* **`#### Rotina mestre (com horario)`** - acao agendavel, organizada nas 7 janelas
  biologicas (o estudo que as define, quando o fundador escrever, mora em `Estudos/`), tratadas
  como offset puro desde o horario de acordar (`Todo dia - Hora X-Y (<nome da janela>) -
  Foco: <ate 3 areas>:`, seguido dos itens `- <tarefa> - <duracao opcional> - #<area>`).
  Fecha com "Por dia da semana" (o que muda por dia, ex: grupo muscular do treino - texto
  livre, nao estruturado) e, quando ele quiser, "Fora da rotina mestre" (itens que nao entraram, com o porque).
* **`#### Principios de conduta (sem horario)`** - disposicao de carater, sem horario, nao
  tem slot na rotina.

`tools/montar_esqueleto_dia.py` le a Rotina mestre e gera o esqueleto do bloco `#### <Dia>`
da Semana (so a parte "Todo dia" - o "Por dia da semana" fica como lembrete pra ajuste a
mao, de proposito, porque e texto livre demais pra parsear com seguranca).

**DOIS FORMATOS de item convivem na Rotina mestre, e os dois valem (07/09/2026).**
Ele reescreveu a Inercia e a Janela de Ouro num formato mais curto e deixou as
outras janelas no antigo:

```
- Treino fisico - 1h30 - #fisico                     (campos separados por ' - ')
- Reprogramacao mental ao acordar (5m) #espiritual   (duracao em parentese, tag colada)
```

O `montar_esqueleto_dia.py` le os dois, por PARTE do item, nunca detectando um
formato pro bloco inteiro - porque o arquivo esta metade em cada um.

**Por que isso virou regra:** o parser so conhecia o formato antigo, e quando ele
mudou a Inercia o resultado nao foi erro. Foi silencio: o item inteiro virou
"nome", com duracao e area `None`, e o dia sairia com 21 itens sem hora e 14 sem
tag de area. Parser que nao reconhece o formato novo nao reclama, ele empobrece o
dado. Sempre que a Identidade mudar de forma, rode
`montar_esqueleto_dia.py --dia <dia> --dry-run` e confira se algum item aparece na
lista de "sem duracao" ou "sem #area" sem merecer.

### 1.2 A Resolucao de Problemas mora na SEMANA (desde 02/09/2026)

Ela saiu da autopsia do dia. A razao: nem todo dia da pra resolver os problemas, e
centralizar os problemas da semana deixa mais claro o que foi resolvido ou nao.

**Consequencia pra skill:** nao procure resolucao de problema na autopsia do dia -
ela nao tem mais essa secao. A fonte e `Vida Pessoal/Semana/Semana DD-MM-AA.md`, na
secao `### Resolucao de Problemas:`, com um item por dia (`- Segunda:`, `- Terca:`...)
e o detalhe aninhado embaixo. Item resolvido leva uma linha de citacao dizendo quando
e como; item em aberto diz do que depende.

Autopsia antiga que ainda tenha a secao e historico. **Nao trate a secao antiga como
pendencia viva** - confira na semana antes.

Ganho pratico: o bloco de fechamento de domingo le a semana inteira de uma vez, em vez
de abrir sete notas.

### 1.3 O bloco do dia sai agrupado por janela (desde 02/09/2026)

O `#### <Dia>` da Semana deixou de ser lista corrida. Ele sai agrupado pelas janelas
biologicas, com a faixa ja convertida pra hora de relogio a partir do acordar:

```
#### Quinta
- Meta operacional:
	- Loja: publicar a pagina nova e disparar as abordagens
	- Consultoria: apresentacao do projeto

- Meta pessoal: Dormir cedo.

> Acordar: 05h

##### 07h-11h (Janela de Ouro) - Foco: Espiritual, Fisico, Financeiro

- [ ] Gerir ativos - parte logica (4h -> ): 08h #financeiro
- [ ] Alongamento (5m -> ): 12h #fisico
```

Regras de forma, todas fixadas por ele em 02/09/2026:

* **Nao existe mais `> Meta do dia:`.** No lugar entram `- Meta operacional:`, que e
  uma LISTA com um sub-item por operacao que o dia toca, e `- Meta pessoal:`, que e
  uma linha so. Sao itens de lista (`- `), nao citacao (`> `).
* **`> Acordar:` fica isolado**, depois de uma linha em branco, e e a unica ancora de
  horario do dia.
* **Tarefas coladas** dentro da janela. A linha em branco so cerca o cabecalho.
* **Todos os itens da Rotina mestre saem no bloco**, nao um recorte.
* **Sem wikilink e sem sub-lista "Todo dia".** Ele removeu por nao serem necessarios.
  Detalhe especifico do dia (o alvo da operacao, o grupo muscular do treino) continua
  entrando a mao embaixo da tarefa.
* **Item sem duracao sai SEM hora**, so `- [ ] Nome #area`, e nao ocupa slot na
  janela. Sao os que, na palavra dele, "realmente nao existem tempo definido e nem
  horario fixo pra serem feitas": oracao, poder do agora, olhar a vista, alongamento.
  Nunca invente duracao pra eles - inventar enche o dia de compromisso que nao existe.
  Como o `recalcular_dia.py` acha tarefa pelo `: HORA`, eles ficam de fora dos
  recalculos, que e o certo.
* Hora do formato `05h` e `07h30`, com zero a esquerda, nos tres lugares: cabecalho de
  janela, linha de tarefa e `> Acordar:`.

### 1.4 Mudou o acordar? Uma linha, um comando

Pedido do fundador: ajustar so o valor do `> Acordar:` e o resto dos blocos recalcular
corretamente sozinho.

Ele edita **so** a linha `> Acordar:` na nota e roda:

```
python recalcular_dia.py --dia Quarta --pelo-acordar
```

Sem repetir a hora no comando. A ancora velha vem da PRIMEIRA tarefa do bloco, que
por desenho fica no offset zero do acordar; o delta e a diferenca. Desliza as
tarefas E as faixas dos cabecalhos de janela, que tambem sao hora de relogio.
Tarefa com `> Hora marcada` embaixo nunca desliza.

**A janela e a ancora do `--realinhar`**, nao a tarefa anterior: ao cruzar um
cabecalho, o cursor volta pro inicio daquela janela, e atraso de uma nao contamina
a seguinte. Janela que nao comporta os proprios itens imprime `ESTOUROU ... passou
N min`. Esse aviso e informacao pro fundador, nao erro do script: quem conserta e a
**Identidade**.

**Os comandos prontos, pra ele copiar e rodar na mao, vivem em
`tools/comandos_da_rotina.md`**, junto dos scripts.

Os outros tres modos continuam: `--acordar HH:MM` (informando a hora), `--apartir-de`
(so o resto do dia) e `--realinhar` (recalcula tudo pelas duracoes reais).

**A regra de onde se ajusta o que** (declarada por ele em 02/09/2026): estrutura e
organizacao da rotina se ajustam na **Identidade**, nunca na nota da semana. A
Identidade e o mestre; a Semana e o dia ja instanciado. Mudou janela, tarefa, duracao
ou area? Mexe na Identidade e regera o dia. Mexer direto na Semana cria divergencia
que ninguem consegue rastrear depois.

Quem gera: `tools/montar_esqueleto_dia.py`, lendo a Rotina mestre. O cabecalho e nivel
5 de proposito: `criar_autopsia.py` e `recalcular_dia.py` delimitam o bloco do dia por
`#### ` e `### `, e `##### ` nao casa com nenhum dos dois.

### 1.5 A secao do dia MUDA DE CASA (desde 07/09/2026)

**Pare de assumir que o bloco do dia esta na nota da semana. Pergunte.**

Ate 06/09/2026 a autopsia era vitrine: `![[Semana 07-09-26#Segunda]]`. Embed do
Obsidian e SO LEITURA, entao pra marcar um checkbox ou escrever o tempo real ele
tinha que abrir a semana, editar la e voltar - o dia inteiro indo e vindo entre
duas notas. O pedido dele: um lugar so como fonte de verdade, e um painel com
somente as informacoes necessarias.

A saida NAO foi copiar. Duas copias vivas do mesmo texto viram merge, e merge e
onde se perde linha. A secao **se muda**:

```
de manha   criar_autopsia.py RECORTA a secao da semana e cola na autopsia.
           Na semana fica um ponteiro: `> Em posse da autopsia do dia:`
a noite    fechar_dia.py DEVOLVE a secao pra semana, no lugar do ponteiro
```

Em qualquer instante **um arquivo so e dono daquele texto**. Sem duas copias,
sem conflito, sem reconciliar.

**O que viaja** (`cofre.secoes_moveis`): o bloco do dia (`#### <Dia>` na semana
vira `### Rotina e tarefas de hoje` na autopsia), Pendencias, Perguntas, Desejos
e Ideias. Mais a linha `- <Dia>:` da Resolucao de Problemas.

**O que NAO viaja:** Proposito, Ano, Mes e Semana por prioridade. Ele so LE essas
durante o dia, entao continuam embed. Materializar a meta do mes criaria 30
copias por mes, e marcar um item numa quarta deixaria as outras 29 mentindo.
A regra: **materializa o que ele edita naquele dia, compoe na hora o que ele so le.**

**Como achar o dono, sempre:**

```python
import cofre
caminho, corpo = cofre.bloco_do_dia(dia)          # a rotina do dia
caminho, corpo = cofre.dono_da_secao(u"Pendencias", dia)
```

Ele olha a autopsia primeiro e a semana depois. Essa ordem nao e detalhe: se o
fechamento de ontem nao rodou (PC desligado, madrugada virada), o texto continua
na autopsia de ONTEM, e e la que ele tem que ser lido.

**O preco de assumir, medido em 08/09/2026.** O `vigia_rotina.py` nasceu vigiando
a nota da semana num caminho fixo e passando `--semana` pro `recalcular_dia`. As
05h00 a posse virou, ele foi olhar a semana, achou o bloco ja esvaziado e falhou
com *"O bloco de Terca nao tem a linha '> Acordar: HHhMM'"*. **Passou o dia
inteiro morto**, sem uma janela na tela pra denunciar, enquanto o fundador
trabalhava na autopsia. Ferramenta que fixa o arquivo em vez de perguntar o dono
nao da erro: ela emudece.

### 1.6 A data e a identidade da nota da semana, o nome nao

**`Semana DD-MM-AA.md` NUNCA pode ser ordenada como texto.** A comparacao le o
dia antes do mes, entao `Semana 31-08-26` vem depois de `Semana 07-09-26` no
alfabeto. Toda virada de mes inverte a ordem, em silencio.

Medido em 07/09/2026: tres ferramentas (`recalcular_dia.py`,
`montar_esqueleto_dia.py`, `sincronizar_areas.py`) estavam operando na semana
PASSADA. Nenhuma deu erro - elas achavam um bloco `#### Segunda` valido, so que
o da semana errada.

Ferramenta nova escolhe UM dos dois, nunca o nome cru:

* **Deriva da data** - `segunda = hoje - timedelta(days=hoje.weekday())`. E o
  jeito do `criar_autopsia.py` e do `cofre.semana_do_dia()`. Prefira este.
* **Parseia a data do nome** e ordena por ela (`cofre.data_da_semana`,
  `cofre.semana_mais_recente`).

As tres ferramentas que buscam por containment (`0 <= (dia - segunda).days <= 6`)
nunca sofreram disso: o teste de conter o dia sobrevive a ordem errada.

### A tag de area

Cada bloco de tarefa da semana carrega a area da vida que ele serve:
`#espiritual`, `#emocional`, `#fisico`, `#intelectual`, `#relacionamento`,
`#lazer`, `#financeiro`. Desde 30/08/2026 e TAMBEM a fonte do placar de cada area (antes
vinha de uma nota subjetiva `N/M` na Autopsia) - `tools/equilibrio_das_areas.py` cruza os
dois e mostra area fraca sem tarefa; `tools/dissecar_autopsia.py` tem a serie historica.

### Navegacao entre as notas

A autopsia do dia abre com a barra de links (`[[Identidade]] - [[Ativos]] -
[[Semana DD-MM-AA]] - [[Insights Geral]]`), embute o proposito
(`![[Identidade#Proposito]]`) e embute o bloco do dia
(`![[Semana DD-MM-AA#<Dia>]]`). Os dias sao **titulos de nivel 4** na nota da
semana - nao use id de bloco (`^segunda`), foi descartado por poluir a nota.

---

## 2. Cadencia e nome dos arquivos

**Uma autopsia por dia.** A nota de hoje e a fonte de hoje - ler a de ontem
quando a de hoje existe e responder com dado errado, nao com dado velho.

O nome do arquivo varia - ja apareceu como "Autopsia das intencoes DD-MM-AA",
"Autopsia das Intencoes DD-MM-AA" e "Autopeia das intencoes DD-MM-AA" (erro de
digitacao que ficou nas notas de julho). **Nao filtre por nome exato: pegue todos
os `.md` da pasta do mes e ordene pela DATA no nome.** A data e a identidade da
nota, o titulo deriva.

**A nota da semana leva a data da SEGUNDA que abre a semana**, no mesmo formato
DD-MM-AA. Para achar a semana de um dia: a nota cujo nome esta entre 0 e 6 dias
antes dele.

**As autopsias sao so o que esta em `Vida Pessoal/Rotina/<Mes>/`.** `Identidade.md`,
`Ativos.md` e `Semana/` vivem um nivel acima, em `Vida Pessoal/`, justamente pra nao
contaminarem contagem historica. Nunca varra `Vida Pessoal/` inteira atras de autopsia.

**Nao confie na data de modificacao do arquivo** - uma fusao do cofre do celular ja
reescreveu o timestamp de dezenas de notas antigas.

---

## 3. Fontes de apoio

| Caminho | O que tem | Quando ler |
|---|---|---|
| `Vault/Estudos/Areas da Vida/<Area>/` | O estudo por tras dos principios de vida | Quando precisar do porque de um principio |
| `Vault/Estudos/<Tema>/` | Os temas que o fundador estuda (dev, vendas, redes, ferramentas) | Criterio tecnico e comercial |
| `Vault/Tarefas/<Mes>/` | Nota de tarefa, com o plano tecnico completo | Estado de um projeto |
| `Vault/Operações/OP <Nome>/` | Documento por operacao | Decisao dentro de uma OP |
| `Vault/Processos/` | Processo repetivel ja escrito | Antes de propor processo novo |
| `Vault/Problemas/` | Erro que ja foi resolvido | Antes de debugar de novo |

**`Insights Geral.md` nao serve como fonte de origem de principio.** E uma nota
guarda-chuva de ~22 KB que casa com quase qualquer termo por busca de texto. Usar
ela como origem gera falso positivo (verificado em 17/08/2026).

---

## 4. Ritual de leitura antes de responder

1. Leia `Vida Pessoal/Identidade.md` por inteiro. Dali saem proposito, meta, medalha,
   proposito maior, dons, talentos, principios, habitos e recursos.
2. Ache a nota da semana que cobre o dia de hoje e leia `#### Ano`, `#### Mes` e o
   `#### <Dia>` de hoje, mais Pendencias, Ideias, Desejos e Perguntas.
3. **Confira se existe a autopsia de HOJE** em `Vida Pessoal/Rotina/<Mes>/`:
   * Existe -> use ela pra Meta do dia e os insights do dia. Pro placar das 7 areas, desde
     30/08/2026 a fonte e o bloco do dia da Semana (ver secao 1.1), nao mais a Autopsia.
   * Nao existe ainda -> use a mais recente e **avise com a data** que a de hoje
     nao foi escrita. Nao presuma que o dia esta vazio, e nao apresente o placar
     de ontem como se fosse o de hoje.
   * Nao existe e o Obsidian esta fechado no PC -> pode ser a autopsia escrita no
     celular que ainda nao sincronizou. O Sync so roda com o app aberto. Sugira
     abrir o Obsidian no PC antes de concluir que ele nao escreveu.
4. Se a decisao envolver operacao de cliente, leia `Vida Pessoal/Ativos.md`.
5. Compare a lista de Principios da Identidade com a de `identidade_e_principios.md`:
   * Principio na nota e nao na memoria -> **entrou agora.** Trate como nivel
     forte e avise que entrou.
   * Principio na memoria e nao na nota -> **saiu.** Nao aplique mais. Cheque se
     e mesmo abandono ou se e reescrita (secao de refinamento na memoria).

---

## 5. Fechamento do dia

Quando o fundador fechar um dia, os insights daquela autopsia **saem dela e vao
para `Insights/Insights Geral.md`**, cada um sob o tema correspondente e com a
data na frente (`- DD/MM/AA: texto`). A autopsia fica com uma linha de citacao
apontando para onde foram. A autopsia guarda o dia; o Insights Geral guarda o
conhecimento.

---

## 6. Quando a estrutura mudar

A autopsia ja cresceu de 12 para 20 secoes em dois meses e depois foi partida nas
cinco notas da secao 1. Ela vai continuar mudando.

Quando a estrutura mudar:

1. Rode `tools/dissecar_autopsia.py` para regenerar os dados.
2. Atualize `identidade_e_principios.md` com o resultado.
3. Confira que `tools/agendar_autopsia.py`, `tools/registrar_na_autopsia.py` e
   `tools/equilibrio_das_areas.py` continuam achando o que leem - todos dependem
   do formato das notas. Rode cada um com `--dry-run` antes de confiar.
4. **Nao reescreva a nota por conta propria.** A estrutura dela e decisao do
   fundador. Se voce vir problema, aponte - so mexa quando ele mandar.
