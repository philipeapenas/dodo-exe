# Playbook de Estudo em Livro (insights do fundador)

**Versao:** 1.0 | **Data:** 29/07/2026 | **Owner:** estudos-expert

Modo LIVRO da skill. Aqui a fonte nao e um autor externo: e o proprio fundador lendo e anotando.
Leia na integra antes de executar. O modo AULA (video e audio) esta em `extracao_playbook.md`.

---

## 1. A inversao fundamental: quem e o autor

No modo aula, a fala sagrada e a do autor do video. **No modo livro, a fala sagrada e a do
fundador.** Ele ja pescou os insights - o trabalho aqui e dar estrutura ao que ele pescou.

**Permitido:** agrupar por tema, dar titulo ao grupo, ordenar, conectar com outras notas,
escrever frase de ligacao curta em texto normal.

**Proibido:**

- Reescrever o insight dele "melhor". Se reescreveu, sumiu a voz dele e a nota virou resumo
  generico de livro - exatamente o que nao serve pra nada.
- Completar a nota com resumo do livro tirado da internet ou da sua memoria de treino. **O que
  ele nao anotou ainda nao e conhecimento dele.** A nota tem que ser espelho honesto do que ele
  de fato absorveu.
- Descartar insight por parecer obvio ou mal formulado. Ele escreveu, ele fica.

Frase de ligacao sua vai como texto normal. O que e dele vai em citacao. A fronteira entre as
duas coisas nunca pode ficar dubia.

---

## 2. Estrutura de pastas

```
Estudos/Livros/<Nome do livro>/
    Insights DD-MM-AA.md      <- captura crua do fundador (INTOCAVEL)
    <Nome do livro>.md        <- a nota-sintese (esta skill escreve)
```

- **As notas diarias sao intocaveis.** Nem reordenar, nem corrigir typo, nem agrupar. Elas sao o
  registro cru, na ordem em que as ideias vieram - isso tem valor proprio.
- A sintese e nota NOVA, batizada com o nome do livro, sem data.
- Rodar de novo = **reescrever a sintese do zero** a partir de todas as diarias, inclusive as
  novas. Nao remendar a sintese antiga: tema novo pode reorganizar tudo.
- Respeite o nome literal da pasta no wikilink, inclusive prefixo esquisito (`+ Esperto que o
  diabo` linka como `[[+ Esperto que o diabo]]`).

---

## 3. Formato da nota-sintese

```
Livro: <titulo completo> - <autor, se o fundador mencionou>
Insights de: [[Insights 29-07-26]], [[Insights 31-07-26]]

# <Nome do livro>

## O que este livro te deu

<1 a 3 frases, em linguagem de negocio, sintetizando o conjunto>

## <Tema 1>

> <insight literal do fundador>

> <outro insight dele, de outro dia, sobre a mesma ideia>

<frase de ligacao curta, se necessario - texto normal>

## <Tema 2>
...

## Solto

> <insight que nao casou com nenhum tema - nunca descartar>

## Perguntas em aberto

<so quando o proprio fundador deixou duvida anotada. Sem duvida anotada, corte a secao.>

## Notas relacionadas

- [[nota existente]] - por que conecta
```

Cabecalho `Insights de:` linka as diarias que entraram - e a rastreabilidade da sintese, o
equivalente da linha `Video:` no modo aula.

---

## 4. Como agrupar por tema

- Alvo: **3 a 6 temas**. Tema nasce do que ELE escreveu, nunca da estrutura de capitulos do livro.
- Nome do tema sai do vocabulario dele. Se ele escreve "medo da pobreza", o tema nao vira
  "insegurança financeira".
- **Insight sobre a mesma ideia aparecendo em dias diferentes e o achado mais valioso da sintese.**
  Junte no mesmo tema e diga isso ao fundador no chat: "voce voltou 3 vezes nesse ponto em dias
  diferentes". E o sinal de onde a cabeca dele esta trabalhando de verdade.
- Marque o dia de origem quando o insight so faz sentido no contexto daquele dia.
- Se ele refinou o mesmo insight depois, use a versao mais completa e cite as duas datas.

---

## 5. A nota-mapa (visao transversal)

**O que e:** nota-indice que cruza LIVRO e VIDEO por tema. Ela nao carrega conteudo - carrega
link mais uma frase dizendo o que tem la. E ela que responde "o que eu de fato sei sobre X".

**Onde:** `Estudos/Mapas/Mapa - <Tema>.md`. Se a pasta `Mapas/` ainda nao existir, crie na
primeira vez e **avise o fundador no chat** que criou.

```
# Mapa - <Tema>

## <Sub-tema>

- [[Domine o jogo da riqueza 27-07-26]] - a escassez aparece no detalhe da casa
- [[+ Esperto que o diabo]] - seu insight sobre medo da pobreza como mecanismo

## <Sub-tema>
...
```

**Regras do mapa:**

- **Todo link leva comentario.** Link sem comentario e busca por tag disfarcada - o comentario e
  a curadoria, e e ele que da valor ao mapa.
- Minimo 3 notas por mapa. Mapa com 2 links e ruido, nao mapa.
- Ordem: do mais fundamental pro mais aplicado.
- Atualizar = reescrever a secao do tema, preservando os links que continuam validos.
- Uma nota pode aparecer em varios mapas. Isso e recurso, nao duplicacao.
- Quando o mapa revelar um tema que o fundador atravessou em varias fontes sem perceber,
  **diga isso a ele no chat** - esse e o produto real do mapa.

---

## 6. Casos de borda

| Situacao | O que fazer |
|---|---|
| Nota `Insights` vazia | Avise e pare. Nao invente insight nem complete com resumo do livro. |
| Livro com uma unica diaria e pouco material | Diga que ainda e cedo pra sintese. Nota fraca poluindo o vault e pior que nota nao escrita. |
| Insight que e citacao do AUTOR do livro | O fundador as vezes copia uma frase do livro junto com o pensamento dele. Se estiver marcado (aspas, "ele diz", "segundo o autor"), preserve como fala do autor do livro - NUNCA atribua ao fundador, nem o contrario. Se ficar dubio, pergunte. |
| Insight contradiz outro de dia anterior | Mantenha os dois no mesmo tema e aponte a contradicao no chat. Pensamento que mudou e informacao, nao erro. |
| Fundador pediu mapa mas so tem 1 livro e 1 video no tema | Diga que ainda nao da massa critica. Sugira quais notas fariam o tema fechar. |
| Livro que ele tambem estudou em video | Cruze na secao de notas relacionadas e no mapa. Sao fontes diferentes do mesmo conteudo. |
