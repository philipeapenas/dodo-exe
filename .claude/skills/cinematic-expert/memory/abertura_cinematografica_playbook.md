# Abertura cinematografica - o padrao que ficou de pe

**Versao:** 1.0 | **Data:** 29/08/2026 | **Owner:** cinematic-expert
**Origem:** o site de um pet shop, construido e aprovado em quatro sessoes. Tudo aqui foi
conferido na tela e, quando envolve leitura de texto, MEDIDO. Nao e gosto.

Este playbook descreve a abertura que o fundador aprovou e as regras que
sustentam ela. Leia antes de montar a
abertura de qualquer site cinematografico.

---

## 1. A tese: a abertura e uma CENA, nao uma foto com texto

A pagina abre num quadro onde alguma coisa ACONTECE, e quem conduz e a rolagem
da pessoa, nao um relogio. No caso de referencia (um pet shop): um cachorro
entra andando, para, encara a camera e late.

Tres consequencias que mandam em tudo que vem depois:

1. **A cena e uma sequencia de fotos desenhada num canvas**, nao um `<video>`.
   Video corre no proprio relogio; sequencia obedece o dedo de quem rola. Ja
   tentamos video e voltamos atras no dia seguinte pelo mesmo motivo.
2. **A secao PRENDE a rolagem enquanto a cena toca** (pin do ScrollTrigger) e
   solta no fim.
3. **Existe uma sequencia POR FORMATO.** Nao se recorta 16:9 por CSS pra virar
   9:16: o recorte perde o assunto. Ver secao 4.

---

## 2. Onde o conteudo assenta

O bloco da abertura tem quatro pecas, nesta ordem de leitura: **trava da marca,
manchete, subtitulo, botao**.

| | Computador | Celular |
|---|---|---|
| Alinhamento horizontal | **ESQUERDA** | **CENTRO** |
| Ancoragem vertical | topo, abaixo da capsula | **CENTRO da tela** |
| Quem ocupa o resto | a cena, no terco/area livre | a cena, atras do bloco |

**Por que a esquerda no computador:** a cena reserva o centro do quadro pro
assunto (o cachorro para no meio). Texto centralizado cai em cima da cara dele.
Sair pra esquerda nao e estetica, e o unico lugar vazio que a cena deixa - e a
medicao confirma: no centro a manchete dava 4.13:1, na esquerda da 5.15:1.

**Por que o centro no celular:** em 9:16 nao existe terco vazio; o assunto ocupa
a largura toda. Centralizado e a unica posicao que nao briga, e o halo por letra
e quem sustenta a leitura.

**A trava da marca entra pelo SCROLL, num quadro escolhido.** No caso de
referencia, no quadro do latido (60 de 85). Ela nao aparece na carga: a abertura comeca com
a cena e a marca assina no momento de maior atencao. Se existir rede de
seguranca por tempo (pra logo nao ficar escondida se as fotos falharem), ela tem
que ser **cancelada quando a cena monta** - senao a logo aparece sozinha sem
ninguem rolar, que foi reclamacao direta do fundador.

**Respiro entre o subtitulo e o botao e maior do que parece necessario.** Foi
aumentado duas vezes a pedido dele. Referencia atual: `clamp(48px, 8vh, 88px)`.

---

## 3. O sistema de vidro (capsula do topo e botao)

O que da elegancia aqui e UM material so, usado em duas pecas: a capsula
flutuante do topo e o botao da chamada.

### 3.1 A capsula do topo substitui a barra

Nao existe barra de largura total. Existe uma **capsula arredondada flutuando**
sobre o conteudo, centralizada, com os itens de menu dentro e os canais
(WhatsApp, Instagram) separados por um fio vertical. Item aceso vira pilula
clara dentro da capsula escura.

Consequencias tecnicas de virar flutuante, todas ja pagas:
- O header vira `fixed` e **deixa de ocupar espaco de layout**: quem guarda o
  lugar dela passa a ser o respiro de topo da secao de abertura.
- As secoes precisam de `scroll-margin-top`, senao ancora de menu leva o titulo
  pra debaixo da capsula.
- **Esse respiro mora em UM lugar so.** Se a rolagem suave tambem calcula
  deslocamento de ancora, ela LE o valor do CSS (`getComputedStyle(...).scrollMarginTop`)
  em vez de repetir o numero. Dois numeros pra mesma medida foi defeito real
  (92px no CSS, 76 no JS).
- O header ocupa a largura toda pra centralizar a capsula, mas so a capsula
  recebe clique (`pointer-events`), senao ele vira tampa invisivel sobre o topo
  da cena.

### 3.2 As tres coisas que fazem vidro parecer vidro

Vidro so LE como vidro quando as tres acontecem juntas:

1. **Da pra ver o que passa atras** (opacidade que deixa passar de verdade).
2. **O que passa atras chega desfocado** (`backdrop-filter: blur`).
3. **A quina de cima pega luz** (`inset 0 1px 0 rgba(255,255,255,...)`).

Faltando a primeira, o resultado e "translucido no papel, solido na tela" - foi
exatamente o que o fundador viu quando a capsula estava em `.88`.

### 3.3 A regra de cor que nao se negocia

**Vidro CLARO com tinta escura nao fecha leitura sobre foto clara.** Testado e
medido: tinta bordo sobre vidro branco sobre a foto da abertura deu de **1.13:1
a 3.25:1**, contra o minimo de 4.5:1. E subir a opacidade nao resolve - so mata
o vidro antes de chegar no numero.

**A inversao e a saida: o vidro carrega a propria cor e a letra e branca.**

E quando a cor do vidro for escura mas pouco cromatica (bordo, marinho, verde
musgo), some com ela em cima de foto bege: o resultado vira cinza. A correcao
nao e escurecer, e **aumentar o croma** e subir `saturate()` do desfoque pra
~200%, que reforca a cor do que passa atras em vez de so borrar. No caso de
referencia isso levou a saturacao de 27% pra 38% e ainda melhorou o contraste.

### 3.4 Quem sustenta a leitura depois que o vidro afina

**A sombra da propria letra, nao a opacidade do fundo.** E o mesmo mecanismo do
halo por letra usado no texto sobre foto, so que escuro. E o que permite ter
vidro fino E leitura aprovada ao mesmo tempo.

Ordem de calculo, sempre nesta sequencia: `foto -> vidro -> sombra da letra`.

### 3.5 Numeros de referencia do primeiro site

Sao ponto de partida, nao lei - cada foto pede a sua medicao.

| Peca | Fundo | Sombra da letra | Pior leitura medida |
|---|---|---|---|
| Capsula do topo | degrade `.54` a `.70` | `.35` | 5.8:1 (sobre secao branca) |
| Botao da abertura | degrade `.58` a `.76` | `.35` | 6.1:1 (sobre o corte do celular) |

A capsula pode ser mais densa que o botao por um motivo objetivo: **ela cruza a
pagina inteira** (secao branca, rosa, azul, faixa colorida) e tem que aguentar o
pior fundo; o botao so assenta sobre a foto, que e clara e previsivel.

---

## 4. Continuidade da cena: as duas regras que evitam salto

### 4.1 A foto de espera E o primeiro quadro da cena

Enquanto a sequencia baixa, alguma coisa segura a tela. **Essa imagem tem que
ser o quadro 1 da propria sequencia.**

Se for outra foto, acontece o que o fundador descreveu: "aparece a foto
antiga do pet parado por alguns segundos". Nao era lentidao, era TROCA DE
IMAGEM - a espera mostrava o assunto posado e a cena comecava no cenario vazio.

Com as duas pontas iguais, a troca acontece de uma imagem pra ela mesma e
ninguem ve.

**Cuidado com o modo calmo:** quem pediu menos movimento nunca vera a cena. Pra
essa pessoa o certo NAO e o cenario vazio do quadro 1: e uma foto com o assunto.
A condicao no CSS tem que repetir exatamente a condicao do JS que liga a cena
(largura E `prefers-reduced-motion`).

### 4.2 Uma sequencia por formato

16:9 recortado por CSS pra 9:16 perde 68% da largura e joga o assunto pra fora.
Gere a sequencia vertical a partir do mesmo video, e **o recorte acompanha o
assunto**: no caso de referencia o cachorro entra pela direita e caminha ate o centro,
entao o recorte comeca deslocado e desliza pro centro nos primeiros 3 segundos.
Recorte parado teria perdido a entrada inteira.

```
crop=w=405:h=720:x='if(lt(t,3),700-(700-437)*(t/3),437)':y=0,scale=540:960,fps=<n/duracao>
```

**Peso:** 85 quadros em 540x960 dao ~1.7MB (contra 3.6MB dos 1400x788 do
computador). Conferir qualidade antes de escolher a compressao: no caso de
referencia `-q:v 8` e `-q:v 5` eram indistinguiveis nesse tamanho, e o leve economizou
500KB. **Diga o peso em voz alta pro fundador** - foi escolha, nao descuido.

A pasta da sequencia e escolhida UMA VEZ na carga. Trocar ao girar o aparelho
obrigaria a baixar a outra sequencia inteira no meio da visita.

---

## 5. Recarregar tem que voltar pro topo

Numa pagina cuja abertura e uma cena, recarregar no meio larga a pessoa num
quadro solto. Ela precisa voltar pro topo pra rever.

Isso custou TRES tentativas. As duas primeiras falharam por motivos diferentes,
e vale conhecer os dois:

1. **Pular quando ha ancora na URL nao serve.** Basta clicar num item de menu
   uma vez pra `#secao` ficar na URL, e dali em diante todo recarregamento cai
   no meio. Separe as situacoes: **recarregamento sempre volta pro topo**;
   chegada nova com ancora honra a ancora. A deteccao e
   `performance.getEntriesByType("navigation")[0].type === "reload"`.

2. **`history.scrollRestoration = "manual"` nao alcanca o ScrollTrigger.** Ele
   mantem uma memoria PROPRIA de posicao de rolagem, separada da do navegador, e
   reaplica ela no refresh. Como o refresh de uma pagina com cena acontece TARDE
   (so quando as fotos terminam de baixar), o sintoma e exatamente o que o
   fundador relatou: **"pisca o topo, mas o usuario continua onde esta"**.

   A saida sao duas linhas, nao uma:
   ```js
   if (recarregou()) ScrollTrigger.clearScrollMemory("manual");
   // ... e, DEPOIS do ScrollTrigger.refresh():
   if (recarregou() && !location.hash) irProTopo();
   ```

**Regra geral que sai daqui:** quando um scroll forcado "pisca e volta", o
culpado nao e o comando, e alguem reposicionando DEPOIS. Procure quem recalcula
tarde.

---

## 6. Peso: o que so o celular paga

`display: none` **nao impede download**. Elemento escondido por CSS com `src` no
HTML e baixado por todo mundo. Se um recurso e so de um formato, pendure a fonte
por JS depois de conferir a condicao - senao todo visitante de computador paga
por um arquivo que nunca vera.

O mesmo vale ao contrario: a sequencia de quadros e escolhida por pasta, entao
cada formato baixa so a sua.

---

## 7. A conferencia (o que roda antes de dizer que esta pronto)

`tools/validar_abertura.py`, no diretorio desta skill. Ele mede a leitura do
texto sobre a imagem **nos dois formatos** e cobra o pior quadro da sequencia,
nao a media.

Tres principios que a ferramenta carrega, e que vieram de erros reais:

1. **A ferramenta mede ONDE O TEXTO ESTA.** Quando o texto mudou de lugar e ela
   nao acompanhou, passou a reprovar medindo o pedaco onde ele nao esta mais -
   uma mentira com cara de reprovacao legitima. A faixa de amostragem e por
   formato e sai da conta do layout, nao de tentativa.
2. **Sequencia se mede pelo PIOR quadro.** Fundo que se mexe nao pode viver na
   margem: no caso de referencia o subtitulo dava 4.52:1 contra o minimo de 4.5, e o
   halo foi reforcado ate 6.2:1.
3. **Quando nao consegue medir, ela AVISA e nao aprova em silencio.**
   Conferencia que se cala quando falha e pior que conferencia nenhuma.

**O portao final continua sendo o aparelho do fundador.** Chrome sem emulacao
desenha numa largura minima maior que a pedida e so recorta o print, entao o
corte que aparece em print de celular headless e da ferramenta, nao do site.
