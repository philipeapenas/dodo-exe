# Template - Relatorio de execucao (o livro das sessoes de um plano)

Formato canonico do relatorio que acompanha um plano ao longo das sessoes.
Vive em `Tarefas/<Mes>/<OP>/Relatorio de execucao - <Nome do plano> DD-MM-AA.md`
e e linkado na nota do dia.

**Aprovado pelo fundador como padrao.** Ao aprovar, ele **renomeou o arquivo** pra incluir o
nome do plano - o que fixou a convencao de nome abaixo.

## A regra que rege este template

**Uma nota por PLANO, acumulando SESSOES. Nao uma nota por sessao.**

O fundador travou a divisao em 27/08/2026, corrigindo os papeis que estavam invertidos:

| Nota | Responde | Escopo |
|---|---|---|
| **Relatorio de execucao** (esta) | *Onde o plano esta?* | Uma por plano. Acumula: "Sessao 1 cobriu os processos 1, 2 e 3", "Sessao 2 cobriu..." |
| **Nota de entrega** | *O que foi feito?* | Uma por sessao. O detalhe concreto do que foi construido. Ver `template_entrega.md` |

Na definicao do fundador: o relatorio e o livro das sessoes ("Sessao 1: religar a busca de
conteudo..."), e a nota de entrega e o que foi feito tecnicamente dentro de cada sessao.

**Por que a distincao importa:** o plano tem processos numerados e leva varias sessoes.
Sem o livro das sessoes, ninguem sabe em que ponto o plano parou sem reler todas as notas
de dia.

### Na sessao seguinte do mesmo plano, NAO crie relatorio novo

Abra o que ja existe, acrescente a secao `## Sessao N` e **atualize a tabela de estado no
topo**. Relatorio novo a cada dia devolve exatamente o problema que este documento resolve.

## Convencao de nome

`Relatorio de execucao - <Nome do plano> DD-MM-AA.md`

A data e a da criacao (primeira sessao), nao a da ultima. O nome do plano no titulo e o
que permite distinguir dois relatorios da mesma OP na mesma pasta.

## Esqueleto

```
# Relatorio de execucao - <Nome do plano>

plano: [[<Plano ...> DD-MM-AA]]
meta: [[<decisao estrategica> DD-MM-AA]]
inicio: DD/MM/AAAA

> Este relatorio acumula as sessoes de execucao do plano acima. Cada sessao registra
> quais processos do plano foram cobertos e o que ficou de pe. O detalhe do que foi
> feito dentro de cada uma vive na nota de entrega da sessao.

---

## Onde o plano esta

| Processo do plano | Estado | Sessao |
| --- | --- | --- |
| 1. <processo, copiado do plano> | Feito / Em andamento / Nao iniciado | Sessao N ou travessao |
| ... uma linha por processo do plano, na ordem dele |

<uma linha dizendo quais processos do plano fecharam e quais seguem abertos>

---

## Material de referencia usado na execucao

<so quando houver. Uma linha por nota, dizendo o que ela era e onde entrou>

---

## Sessao N - DD e DD/MM/AAAA

**Cobriu:** processos X, Y e Z.
**Nota do dia:** [[<Titulo> DD-MM-AA]]
**Entrega:** [[<slug-da-entrega>-DD-MM-AA]]
**Desenho aprovado:** <link, quando houver>

### O que foi coberto
<um marcador por processo coberto, em linguagem de negocio>

### O que mudou no escopo, durante a execucao
<so quando o escopo mudou de verdade. Diga o que o fundador decidiu e por que>

### Frentes que entraram sem estar no plano
<so quando houver. Diga que apareceram como achado, nao como escolha de escopo>

### O que ficou de pe ao fim da sessao
### O que a sessao deixou pendente

---

## O que atravessou as sessoes

<FATO do periodo, nao licao: o que aconteceu por cima de mais de uma sessao. Duas
frentes que colidiram, publicacao que ficou represada, dado que mudou no meio da
execucao. Sem moral da historia - isso e da secao seguinte>

---

## Aprendizados que atravessam as sessoes

<LICAO generalizavel, o que vale pra alem daquela sessao. Nao repetir o que ja esta
na entrega>

---

## Sessao N+1

_A escrever. Proxima frente: <processos que faltam>._
```

## O que NAO vai aqui

- **Detalhe do que foi construido.** Isso e da nota de entrega. Aqui fica o mapa, nao o terreno.
- **Prazo, nota de 0 a 10 e justificativa.** Sao campos da nota de plano e quem preenche
  e o fundador (mesma regra de `template_nota_de_plano.md`).
- **Bloco de codigo, caminho de arquivo, nome de funcao ou endpoint** (Regra de Ouro 13).

## Detalhes que o fundador aprovou e valem repetir

- **A tabela de estado abre a nota**, antes das sessoes. E a primeira pergunta de quem
  volta ao plano depois de dias.
- **A secao da proxima sessao ja nasce aberta**, com a frente seguinte nomeada. Ela vira o
  ponto de partida da retomada.
- **Frente que entrou fora do plano e marcada como ACHADO**, com o motivo. Isso separa
  descoberta de execucao de escopo que inchou sem controle.

### Aprovados depois, num plano de otimizacao e publicacao de pagina

- **`## Material de referencia usado na execucao`.** Pedido dele: linkar a nota de
  referencia do material que foi usado pro codigo. A secao
  existe pra separar INSUMO de RESULTADO - a nota de referencia e o canvas sao o que
  existia ANTES e virou codigo, nao o que a sessao produziu. Sem ela, essas notas
  acabam listadas junto das entregas, como se fossem produto da sessao.
- **`## O que atravessou as sessoes`, separada dos Aprendizados.** Uma carrega FATO do
  periodo (duas frentes colidiram nos mesmos arquivos, a publicacao ficou represada por
  cinco rodadas, o catalogo mudou de tres pra quatro produtos no meio); a outra carrega
  LICAO. Misturadas, o fato vira moral da historia e some.

**Lembrete que o primeiro caso real cobrou na pratica:** quatro sessoes executaram aquele
plano e as tres primeiras nao escreveram nada aqui. A regra de acrescentar `## Sessao N`
ja estava neste documento - o que faltou foi cumprir. **Toda sessao escreve
a sua parte, no mesmo padrao**, e nao ha sessao que escreva pelas outras.
