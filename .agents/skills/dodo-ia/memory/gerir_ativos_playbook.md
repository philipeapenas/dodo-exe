# Gerir Ativos - o mapa, nao a copia

**Owner:** dodo-ia

Este playbook e um **mapa**: diz onde o conhecimento esta no segundo cerebro, em vez de
copiar o texto dele. Segue a Regra de Ouro 17 - aponta, nunca copia.

**O neuronio:** a nota de estudo em que o fundador define o que e gerir ativos, em
`Vault/Estudos/Areas da Vida/Financeiro/O que e gerir ativos DD-MM-AA.md`.

**Numa instalacao nova ela ainda nao existe.** O estudo e dele: peca pra ele escrever (a
`estudos-expert` ajuda a organizar se ele partir de uma aula ou livro). Ate la, os cinco
pilares abaixo servem de esqueleto. Quando a nota existir, ela manda, e a tabela da secao 1
passa a usar os titulos dela.

---

## 1. Os cinco pilares e onde cada um cai no dia

O bloco "Gerir ativos" e o corpo do dia de operacao dele. A nota da semana diz qual pilar
entra em qual hora, por wikilink de titulo. Distribuicao de referencia (a real vem da Rotina
mestre da Identidade):

| Momento | Pilar | Link que a nota da semana usa |
|---|---|---|
| Parte logica | Visibilidade (inventario e mapeamento) | `[[O que e gerir ativos DD-MM-AA#Visibilidade]]` |
| Parte logica | Gestao de riscos e seguranca | `[[O que e gerir ativos DD-MM-AA#Gestao de Riscos e Seguranca]]` |
| Parte logica | Desempenho e valor (ROI) | `[[O que e gerir ativos DD-MM-AA#Desempenho e Valor]]` |
| Parte criativa | Ciclo de vida (governanca operacional) | `[[O que e gerir ativos DD-MM-AA#Ciclo de Vida]]` |
| Parte criativa | Automacao e integracao (escalabilidade) | `[[O que e gerir ativos DD-MM-AA#Automacao e Integracao]]` |

**A ordem nao e decorativa.** Visibilidade primeiro porque nao se otimiza o que nao se
sabe que existe; automacao por ultimo porque ela consome o dado dos outros quatro.
Dentro de Ciclo de Vida cabem tres ancoras de bloco (`^Provisionamento`, `^Manutencao`,
`^Descomissionamento`), criadas na propria nota de estudo quando precisar apontar pra elas.

**Consequencia pra skill:** quando a parte logica nao rodar, o que faltou foi
VISIBILIDADE - e e ela que produz o "Onde paramos" da nota do dia. Se ela caiu, a
abertura da parte criativa levanta o estado antes de qualquer execucao, e isso fica
registrado.

---

## 2. O fluxo de "Otimizar documentos da operacao"

E o item do checklist `Processos: <papel>` da nota do dia que fecha o ritual (Regra de
Ouro 18). **A dodo-ia e a cabeca que sabe o fluxo; ela nao escreve nota e nao decide
sozinha a meta.**

```
dodo-ia          le o vault, aponta a decisao estrategica vigente e o estado real
   |             (Passo 1 da Cadeia de Pensamento). Entrega CRITERIO, nao texto.
   v
ceo-dodo         analisa a meta pelo strategic_os: qual e a restricao real, qual o ROI,
   |             o que muda no corte. Especifica EXATAMENTE o que deve ser anotado.
   v
assistente-expert  escreve a nota no padrao ja documentado nos templates dela.
```

Nenhuma etapa pula. Se a dodo-ia escrever a nota, ela viola a propria restricao; se o
ceo-dodo escrever, ele viola a Regra 1 dele (orquestra, nao executa).

---

## 2.1 Sessao estrategica = as duas notas

Quando o fundador pede **"sessao estrategica"**, ele NAO esta pedindo um evento avulso. Ele
esta abrindo a parte logica do bloco Gerir ativos, com os tres primeiros pilares da secao 1.

A materializacao formal desse bloco sao **duas notas, sempre as duas**:

1. A **decisao estrategica** do dia, em `Operações/OP <Nome>/Decisões estratégicas/`.
2. A **nota do dia**, em `Tarefas/<Mes>/<OP>/`.

Uma sem a outra significa bloco pela metade. A cadeia e a mesma da secao 2.

**Consequencia pra skill:** ao ouvir "sessao estrategica", nao pergunte qual e o escopo. Rode
o bloco inteiro e produza as duas notas. A proxima frente de execucao so abre depois disso.

---

## 2.2 Adiantamento: pesquisar o passo incerto antes de executar

Entra **depois do plano escrito e antes da execucao real**, quando algum passo do plano tem
mecanica ainda incerta.

**O gatilho:** o plano cita um passo que ninguem sabe exatamente como fazer. Em vez de comecar
a executar e descobrir no meio, roda-se a pesquisa na mesma sessao.

| Tipo de incerteza | Quem pesquisa | Como |
|---|---|---|
| Sistema EXTERNO (API de plataforma, produto de terceiro) | quem estiver no papel de dodo-ia ou ceo-dodo | Busca e leitura na documentacao oficial |
| Sistema INTERNO (codigo do proprio ecossistema) | dev-expert | deep-dive no codigo (Regra de Ouro 10), e ele mesmo escreve a secao tecnica |

**Onde o resultado mora:** secao dedicada `## Adiantamento - <assunto> (DD/MM)` na nota do
dia, com achado principal, passo a passo numerado e as fontes citadas.

**O que acontece depois, e e o ponto todo:** decisao estrategica e plano sao ATUALIZADOS pra
refletir o que a pesquisa corrigiu. Na sessao que gerou o padrao, dois adiantamentos
derrubaram duas suposicoes erradas do plano, e a sessao fechou antes do horario previsto.
Pesquisar antes sai mais barato que descobrir no meio.

**Por que e regra de skill e nao Regra de Ouro:** a Regra de Ouro 18 ja cobre a abertura
do bloco de operacao. O Adiantamento e um refinamento dela dentro do ritual do fundador, e o
ritual dele mora aqui na dodo-ia, nao em `regras_de_ouro.md`.

---

## 3. A hierarquia das notas de uma OP

| Nota | Papel | Onde vive |
|---|---|---|
| Decisao estrategica | **E a meta do dia.** Direcao + consequencia + o que continua aberto | `Operações/OP <Nome>/Decisões estratégicas/<decisao> - <Projeto> - DD-MM-AA.md` |
| Plano | **E o plano do dia.** Nasce da decisao estrategica acima | `Operações/OP <Nome>/Planos/<Plano ...> DD-MM-AA.md` |
| Nota do dia | Onde paramos, pendencias, fases, trabalho de hoje | `Tarefas/<Mes>/<OP>/<Titulo> DD-MM-AA.md` |
| Entrega | O relatorio do que ficou pronto | `Operações/OP <Nome>/Projetos/<projeto>/03_Entregas/<DD-MM-AA>/` |

O topo da nota do dia:

```
Contexto: [[Tudo sobre <OP> DD-MM-AA]]

**Meta do dia:** [[<decisao estrategica> DD-MM-AA]]
**Plano do dia:** [[<Plano ...> DD-MM-AA]]
**Ultima entrega:** [[...]] - leia esta primeiro, e o relatorio de onde o projeto parou
**Entrega anterior:** [[...]]
**Registro do dia anterior** (arquivado na pasta da OP): [[...]]
```

A cadeia de leitura que isso cria: **decisao estrategica -> plano -> nota do dia ->
entrega**. Cada uma responde uma pergunta diferente - por que, como, o que aconteceu
hoje, e o que ficou pronto.

---

## 4. O orcamento do dia e o recalculo do resto

**O orcamento do bloco de operacao e a duracao declarada na Rotina mestre da Identidade.**
Quando o bloco abre fora da hora, **o orcamento NAO encolhe** - o que desliza e o resto do
dia.

**O gatilho:** ele declara a hora real de inicio de uma tarefa ("comecei as 15h45"). Ai:

```
python recalcular_dia.py --dia Segunda --apartir-de "Gerir ativos - parte criativa" --inicio 15:45
```

O script soma a duracao declarada, acha a proxima tarefa **nao concluida** e empurra dali
pra frente por um delta constante. **Tarefa ja marcada `[x]` nunca e tocada** - ela ficou
na hora em que aconteceu, e reescrever isso apagaria o dado de cumprimento que sustenta o
sistema inteiro.

Depois de rodar, **conferir a linha de nota embaixo de `Descansar`**: ela declara a hora
de acordar do dia seguinte e o script nao a reescreve. E confrontar com as ancoras do dia
seguinte - compromisso com terceiro nao desliza.

### A tarefa que nao pode cair

Se o fundador declarar uma tarefa como inegociavel no dia (estudo, por exemplo), ela e a
primeira candidata natural a ser cortada quando o dia estoura, porque fica no fim da fila.
Ao recalcular, **diga em voz alta a que horas ela caiu.** Se ela cair num horario em que ele
nao vai fazer de verdade, o problema nao e a tarefa: e o tamanho do bloco de operacao, e
isso e decisao dele.

---

## 5. Auto conhecimento vigente

O papel que ele veste no bloco de gerir ativos e a definicao que ele da de si mesmo em
`## Quem sou:` da Identidade. E ela que vira o rotulo do checklist da nota do dia
(`Processos: <papel>`).

A lista do checklist (Regra de Ouro 18) e dele: **confira sempre no disco, ele mexe nesta
lista.** O que ele declarar sobre si mesmo desce pra `identidade_e_principios.md` (secao
Auto conhecimento declarado) e sobe pra `Vida Pessoal/Identidade.md` quando ele mesmo
escrever la - a skill nao escreve na Identidade dele.
