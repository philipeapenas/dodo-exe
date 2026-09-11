# Playbook de Extracao de Estudos

**Versao:** 1.0 | **Data:** 29/07/2026 | **Owner:** estudos-expert

Conhecimento operacional completo da extracao. Leia na integra antes de executar.

---

## 1. O que esta skill entrega (e o que ela NAO entrega)

Ela entrega uma **nota-literatura**: o conteudo da fonte organizado por argumento, com a
citacao literal do autor como prova. Fiel a fonte, sem opiniao.

Ela NAO entrega a **nota-permanente** (o conteudo reescrito com as palavras do fundador).
Esse passo e dele, e e onde o conhecimento gruda de verdade. A skill existe pra que ele
receba a materia-prima perfeita e nao gaste tempo garimpando fala em video de 20 minutos.

**Consequencia pratica:** nao "melhore" o autor. Se ele foi confuso, a nota mostra o argumento
confuso do jeito que ele fez. A nota e um espelho da fonte, nao um upgrade dela.

---

## 2. A ferramenta

```
py .agents/skills/estudos-expert/tools/extrair_transcricao.py "<link ou arquivo>"
```

Flags: `--forcar-scribe` (pula a legenda), `--out <pasta>`, `--lang por`.

Ela imprime `FONTE=`, `ARQUIVO=` e `CARACTERES=`. Leia o `ARQUIVO=` gerado, nao tente
transcrever por conta propria.

**Ordem das fontes:**

1. **Legenda do YouTube** (padrao). Gratis, instantanea. E a fala crua do autor.
2. **ElevenLabs Scribe** (fallback automatico). Entra quando o video nao tem legenda, quando
   o material e arquivo local do fundador, ou com `--forcar-scribe`. **Consome credito.**
   O tool reusa o `transcribe_video.py` da voice-expert (Regra de Ouro 6) - nunca
   reimplementar transcricao aqui.

**Quando forcar o Scribe mesmo tendo legenda:** so quando a legenda vier tao quebrada que as
citacoes ficariam inutilizaveis. Antes de forcar em lote, avise o fundador do custo.

---

## 3. NotebookLM: decidido contra (nao reabrir)

Verificado na pratica: o NotebookLM **nao transcreve video do YouTube**. Ele importa a
mesma faixa de legenda que o tool ja le, e recusa a importacao quando o video nao tem legenda
("transcript not available") - nao existe fallback de audio nele.

Ou seja: passar por ele nao melhora uma palavra do resultado, e ainda adiciona dependencia de
MCP comunitario dirigindo um Chrome logado. Decisao do fundador: fora do pipeline.

Uso legitimo dele, fora do escopo desta skill: conversar com o acervo de estudos ja extraido.

---

## 4. Formato canonico da nota

Nota de referencia: leia uma nota de estudo ja extraida da mesma pasta antes de escrever, para calibrar o tom. Se for a primeira, siga o formato abaixo a risca.

```
Video: <link original, intacto>

# <Titulo, igual ao nome do arquivo sem a data>

## Tese central

<1 a 3 frases de sintese, em linguagem de negocio>

> "<citacao que sustenta a tese>"

## <Nome do argumento 1>

<contexto curto quando a citacao nao se explica sozinha>

> "<citacao>"

## <Nome do argumento 2>
...

## Acoes diretas que ele manda fazer

1. <acao>
2. <acao>

## Notas relacionadas

- [[nota existente]] - por que ela se conecta
```

**Regras de forma:**

- A linha `Video:` fica no topo, **intacta**. Ela e a rastreabilidade da nota.
- Titulo da secao = **o argumento**, nao o minuto do video. Organize por tese, nunca em ordem
  cronologica de fala.
- Quando o proprio autor numera ("primeira regra", "segunda coisa"), respeite a numeracao dele
  no nome da secao (`## Regra 3: as armadilhas de consumo`).
- Negrito para sub-blocos dentro de uma secao (`**Supermercado**`, `**Cartao de credito**`).
- A nota do vault mantem acentuacao normal - e conteudo do fundador, nao arquivo de agente.
- Sem emoji (Regra de Ouro 11).
- Secao de acoes so existe se o autor de fato mandou fazer algo. Se ele nao mandou, corte a
  secao - nao invente tarefa.

---

## 5. Citacao: as regras sagradas

**Permitido:**

- Consertar erro obvio de legenda automatica: "mega cena" -> "mega-sena", "Iqueza" -> "riqueza",
  nome do autor grafado errado. O criterio e: a palavra que ele falou esta clara pelo contexto.
- Cortar trecho no meio com `(...)`.
- Tirar vicio de fala e repeticao gaguejada quando nao muda o sentido.
- Normalizar pontuacao (a legenda vem sem virgula em lugar nenhum).

**Proibido:**

- Parafrasear dentro das aspas. Se voce reescreveu, tire as aspas e vire texto normal.
- Colar duas falas distantes do video numa citacao unica sem `(...)`.
- Inventar citacao que "resume bem" o que ele quis dizer. Nunca.
- Corrigir o autor dentro da nota (ver item 7).

**Teste mental antes de fechar cada citacao:** essa frase aparece no arquivo de transcricao?
Se nao aparece exatamente assim (fora as limpezas acima), ela nao pode estar entre aspas.

---

## 6. Como escolher o que entra

Alvo: **3 a 7 secoes**. Criterio de corte por secao: o argumento se sustenta sozinho se alguem
ler so aquele bloco?

**Entra:** tese, analogia que explica a tese, distincao conceitual, exemplo pessoal que prova o
ponto, numero/regra que ele nomeia, ordem direta ao espectador.

**Fica de fora:** saudacao, pedido de like e inscricao, descricao de paisagem, propaganda do
proprio canal, anedota sem conclusao, repeticao da mesma ideia ja coberta por outra secao.

Quando o autor repete a mesma ideia varias vezes ao longo do video, use a **versao mais
completa** da fala, nao a primeira que aparecer.

---

## 7. Afirmacao duvidosa do autor

Se o autor afirmar algo factualmente errado ou suspeito (autoria de livro, dado historico,
numero), a nota registra **o que ele disse**, atribuindo a ele ("ele atribui", "segundo ele").
Nunca corrija dentro da nota e nunca apague.

O alerta vai **no chat**, em uma linha, ao entregar. Exemplo: o autor atribui a um terceiro um
papel historico que nao se confirma. Na nota fica registrado como afirmacao dele; no chat, a
duvida e sinalizada ao fundador.

---

## 8. Notas relacionadas (minimo 2)

Regra da literatura de notas permanentes: nota sem link vira ilha e morre. **Toda nota fecha com
no minimo 2 wikilinks.**

Como montar, na ordem:

1. **Liste a pasta** do estudo e a pasta do mes antes de escrever qualquer link.
2. Linke **apenas nota que existe** - o nome do wikilink e o nome do arquivo sem `.md`, com
   acentuacao e data exatamente como estao no disco.
3. Escreva **por que** conecta, depois do hifen. Link sem motivo nao ajuda o fundador depois.
4. Se a pasta so tiver essa nota (autor novo), linke notas de tema proximo em outros meses. Se
   nao houver nenhuma, avise no chat em vez de inventar link quebrado.

---

## 9. Onde as notas vivem

```
Vault/Estudos/<Tema>/<Autor>/<Titulo> DD-MM-AA.md
```

A subpasta por autor existe quando ha varios estudos da mesma pessoa (ex: `Vendas/<Autor>/`).
Estudo avulso fica direto na pasta do tema.

**Nunca cace arquivo no vault.** O fundador reorganiza o vault sozinho: se o caminho da nota nao
estiver claro, PARE e pergunte (Karpathy §1).

---

## 10. Casos de borda

| Situacao | O que fazer |
|---|---|
| Video sem legenda | O tool cai sozinho no Scribe. Avise o fundador que gastou credito. |
| Legenda so em outro idioma | O tool pega a primeira faixa disponivel. Confira se serve; se a traducao estiver ruim, `--forcar-scribe`. |
| Nota ja tem texto do fundador | NUNCA sobrescreva. O texto dele fica; a extracao entra abaixo. |
| Transcricao acima de ~60k caracteres | Leia o arquivo em partes. Nao resuma por cima sem ter lido tudo - citacao inventada nasce dai. |
| Varias notas no mesmo pedido | Extraia uma por vez e escreva uma por vez. Lote inteiro na cabeca mistura citacao de video diferente. |
| Video e so conversa sem tese | Diga isso ao fundador. Nota fraca poluindo o vault e pior que nota nao escrita. |
