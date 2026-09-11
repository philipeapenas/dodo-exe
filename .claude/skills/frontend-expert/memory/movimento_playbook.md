# Playbook de Movimento - Coreografia de Rolagem

**Versao:** 1.0 | **Data:** 14/08/2026 | **Owner:** frontend-expert
**Origem:** padrao nascido no primeiro site de cliente e replicado no seguinte a pedido do fundador.

Este e o padrao de movimento dos sites da Dodo. Nao e biblioteca nova por projeto: e **um sistema so**, copiado e adaptado. Consulte junto com `direcao_estetica_playbook.md` - a direcao estetica define a aparencia, este define o comportamento.

---

## A pilha

Tres arquivos, servidos do proprio projeto em `assets/js/vendor/` - **nunca de CDN**:

| Arquivo | Papel |
| --- | --- |
| `gsap.min.js` | motor de animacao |
| `ScrollTrigger.min.js` | dispara animacao conforme a rolagem |
| `lenis.min.js` | rolagem suave |

Mais um `assets/js/movimento.js` proprio do projeto, com a coreografia.

**Ordem obrigatoria no HTML** (todos com `defer`, antes do `main.js`):

```
gsap -> ScrollTrigger -> lenis -> movimento.js -> main.js
```

---

## As quatro regras inegociaveis

### 1. Dois modos, nunca "desligado"

Aparelho que pede menos movimento **nao pode receber a pagina morta**. No Android a economia de bateria liga esse pedido sozinho - o visitante perderia a pagina inteira sem nunca ter escolhido isso.

```js
var calmo = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
```

- **COMPLETO:** coreografia inteira, rolagem suave, deriva/parallax.
- **CALMO:** o conteudo ainda aparece, so que **por transparencia** - sem deslocamento, sem escala, sem deriva, sem rolagem suave.

Quem tem sensibilidade se incomoda com **movimento**, nao com mudanca de transparencia. Na pratica: `y: calmo ? 0 : 24`, `scale: calmo ? 1 : .97`, e o bloco de parallax inteiro dentro de `if (!calmo)`.

### 2. Grade anima por ITEM, nunca pela grade

```js
ScrollTrigger.batch(".grade > *", { start: "top 90%", once: true, onEnter: ... });
```

Com o gatilho na grade inteira, no celular (onde a grade vira uma coluna alta) os itens de baixo animam **fora da tela** e chegam parados no olho de quem rola. O `batch` da um gatilho por item e ainda agrupa quem entra junto, preservando o escalonamento.

### 3. Estado inicial por JS, nunca por CSS

```js
gsap.set(pecas, { opacity: 0, y: 20 });
```

Se o estado inicial invisivel morar no CSS e o GSAP nao carregar, a pagina fica **permanentemente em branco**. Aplicado por JS, o pior caso e a pagina aparecer inteira sem animacao - que e um resultado aceitavel.

O arquivo inteiro comeca com a guarda:

```js
if (typeof window.gsap === "undefined" || typeof window.ScrollTrigger === "undefined") return;
```

### 4. Conteudo que chega por rede avisa quando chegou

Vitrine, catalogo ou lista que vem de API **nao existe** quando o `movimento.js` roda. Quem renderiza dispara o aviso; o movimento escuta:

```js
// no main.js, depois de montar
document.dispatchEvent(new CustomEvent('catalogo:pronto'));

// no movimento.js
document.addEventListener('catalogo:pronto', animarVitrine);
```

Sem isso os itens entram na tela sem animacao nenhuma, e o resto da pagina parece quebrado por comparacao.

---

## Quem manda no transform (29/08/2026)

**Esta e a quinta regra inegociavel, e a que custou mais caro ate hoje.**

O GSAP escreve `transform` como **estilo inline**. Estilo inline vence qualquer
regra de folha de estilo, sempre. Entao, no instante em que uma animacao toca um
elemento, TODA regra de CSS que mexa em transform naquele elemento deixa de
existir - **sem erro, sem aviso, sem nada no console**.

E pior do que parece: o `gsap.from` deixa o transform inline la DEPOIS de
terminar. O elemento fica marcado pra sempre.

### Os dois estragos que isso ja fez, no mesmo projeto

1. **O leque de lancamentos nao se armava.** Clicar num cartao mudava sombra e
   camada (que nao sao transform) e nao movia nada. O fundador descreveu como
   "esta so sobrepondo o video clicado". O arranjo inteiro - posicao, giro,
   tamanho - vivia em transform, e a animacao de entrada tinha apagado tudo.
2. **O levantar dos cards de produto no hover estava morto**, pelo mesmo motivo,
   e ninguem tinha percebido. Foi descoberto por acidente, consertando o item 1.

### A regra: UM dono de transform por elemento, declarado

Antes de escrever, decida quem manda no transform daquele elemento e escreva no
comentario. Sao dois casos, e a saida e diferente em cada um:

**Caso A - o CSS manda na posicao** (arranjo, grade, leque, qualquer coisa que o
estado do elemento define). A entrada NAO pode tocar em transform: anima so
opacidade.

```js
gsap.from(lote, { opacity: 0, duration: .8, clearProps: "opacity" });
```

**Caso B - a animacao manda na entrada e o CSS so faz hover.** A entrada devolve
o controle no fim:

```js
gsap.from(lote, { opacity: 0, y: 30, duration: .8, clearProps: "transform" });
```

`clearProps: "transform"` e o que ressuscita hover, foco e qualquer estado de
CSS que dependa de transform. **Sem ele, todo card animado na entrada perde o
hover em silencio.**

### Como identificar em dois minutos, sem chutar

O truque: leia uma propriedade que venha da MESMA regra de CSS mas **nao seja
transform** - `cursor`, `z-index`, `box-shadow`.

- A outra propriedade mudou e o `transform` nao -> **a regra casou; alguem esta
  escrevendo transform por cima.** Procure a animacao.
- Nenhuma das duas mudou -> o problema e de cascata, nao de dono. Vai pro
  `css_cascata_playbook.md`.

Foi essa leitura que fechou o diagnostico em 29/08, depois de duas tentativas
erradas que pareciam certas.

---

## O vocabulario (o que animar, e so isso)

**Abertura** - uma sequencia so, orquestrada, na ordem em que a pessoa precisa ler. Ex.: marca -> assinatura -> divisor -> promessa -> subtitulo -> acao. A foto de fundo abre com escala de 1.08 pra 1 em ~2,4s, devagar o bastante pra nao competir com o texto.

**Divisor que se desenha** - se o projeto tem um elemento-assinatura (filete, risco, linha), ele **cresce** em vez de aparecer: `scaleX: .3 -> 1`. E a marca se assinando.

**Entradas na rolagem** - uma funcao `revelar()` unica, curta, igual na pagina inteira: `opacity 0 -> 1`, `y 24 -> 0`, `start: "top 88%"`, `once: true`. **Nao invente efeito diferente por bloco** - vira ruido.

**Parallax: no maximo UM no corpo do site.** Escolha a imagem que mais importa (retrato, foto do sobre). Em pagina que vende, movimento demais atrapalha quem esta avaliando.

**Barra de progresso** - `scaleX: 0 -> 1` com `scrub`. Vale nos dois modos: e medidor, nao elemento se deslocando. Use a cor do elemento-assinatura pra amarrar com a identidade.

**Escala sempre entra por BAIXO de 1** (`.97 -> 1`). Crescer passa da moldura arredondada do card.

---

## Ancoras com rolagem suave

Quando o Lenis assume, `scroll-behavior` do CSS briga com ele. Desligue e roteie as ancoras:

```js
document.documentElement.style.scrollBehavior = "auto";
link.addEventListener("click", e => { e.preventDefault(); lenis.scrollTo(destino, { offset: -respiro(destino) }); });
```

O `offset` negativo desconta o topo fixo - sem ele a secao para **embaixo** do cabecalho.

**O quanto descontar NAO se escreve aqui.** O CSS ja declara isso, em
`scroll-margin-top` da secao (que e quem manda quando o Lenis nao esta no
circuito). Repetir o numero no JS cria duas fontes pra mesma medida, e elas
divergem calado - aconteceu em 29/08, com 92px no CSS e 76 no JS. O JS le:

```js
function respiro(destino) {
  const declarado = parseFloat(getComputedStyle(destino).scrollMarginTop);
  return Number.isFinite(declarado) && declarado > 0 ? declarado : 76;
}
```

---

## Recarregar: quem desfaz o seu scroll forcado

Em pagina com cena presa a rolagem, recarregar precisa voltar pro topo. Se voce
mandar pro topo e a pagina **piscar o topo e voltar pro lugar antigo**, o culpado
nao e o seu comando: e alguem reposicionando DEPOIS dele.

Sao dois suspeitos, e desligar so o primeiro nao resolve:

1. **O navegador**, com a restauracao de rolagem. Desliga com
   `history.scrollRestoration = "manual"`.
2. **O ScrollTrigger**, que mantem memoria PROPRIA de posicao, separada da do
   navegador, e reaplica ela no refresh. Desliga com
   `ScrollTrigger.clearScrollMemory("manual")`.

E o refresh de uma pagina com cena acontece **tarde**, quando a sequencia de
fotos termina de baixar - por isso o topo tem que ser garantido de novo depois
dele, e nao so na carga:

```js
ScrollTrigger.refresh();
if (recarregou() && !location.hash) irProTopo();
```

`recarregou()` distingue F5 de chegada nova
(`performance.getEntriesByType("navigation")[0].type === "reload"`): recarregar
sempre volta pro topo, mas link com ancora continua honrando o lugar pedido.
Pular a regra inteira quando ha `location.hash` NAO serve - basta um clique no
menu pra ancora ficar na URL e todo recarregamento seguinte cair no meio.

---

## Checklist antes de entregar

- [ ] Desligou o GSAP (renomeou o arquivo) e a pagina continua legivel e inteira?
- [ ] Ligou "reduzir movimento" no sistema e o conteudo ainda aparece?
- [ ] No celular, os itens de baixo da lista animam **quando chegam** na tela?
- [ ] Ancora do menu para na altura certa, sem sumir atras do topo fixo?
- [ ] Cada elemento animado tem UM dono de transform, e esta escrito qual e?
- [ ] Todo `gsap.from` que mexe em transform devolve o controle com `clearProps`?
- [ ] Card com hover que levanta continua levantando DEPOIS da entrada tocar?
- [ ] O desconto da ancora sai do CSS, e nao de um numero repetido no JS?
- [ ] Recarregando no meio da pagina, ela volta pro topo E fica (nao pisca e volta)?
- [ ] Conteudo que vem de API dispara o aviso e anima?
