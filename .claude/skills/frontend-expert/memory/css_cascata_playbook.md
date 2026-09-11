# Playbook de Cascata e Especificidade

**Versao:** 1.0 | **Data:** 29/08/2026 | **Owner:** frontend-expert
**Origem:** postmortem de um site de cliente (Regra de Ouro 12). Correcao escrita, revisada, dada como pronta, e sem nenhum efeito no navegador por dois dias.

Este playbook existe por causa de um defeito que nao parece defeito de codigo. Leia antes de escrever qualquer bloco `@media` de sobrescrita.

---

## 1. O defeito: media query nao acrescenta especificidade

Envolver uma regra em `@media` NAO deixa ela mais forte. A especificidade continua sendo a do seletor.

```css
/* base, no meio do arquivo */
.hero-titulo { margin: 0 auto; }          /* (0,1,0) */

/* sobrescrita escrita ANTES da base */
@media (min-width: 701px) {
  .hero-titulo { margin-left: 0; }        /* (0,1,0) tambem */
}
```

Empate em `(0,1,0)`. No empate ganha **quem vem depois no arquivo**. Como o bloco `@media` estava antes, a base venceu e a sobrescrita nunca existiu na pratica.

---

## 2. A regra de posicao (inegociavel)

**Todo bloco `@media` de sobrescrita mora DEPOIS das regras base que ele sobrescreve.**

Ao mover um bloco pra sua posicao correta, deixe o comentario travando o motivo:

```css
/* Este bloco precisa ficar DEPOIS das bases do hero.
   @media nao acrescenta especificidade: se as bases voltarem pra baixo daqui,
   o defeito original volta junto. */
@media (min-width: 701px) { ... }
```

Sem o comentario, a proxima reorganizacao de arquivo reintroduz o bug e ninguem lembra por que.

---

## 3. O sintoma que denuncia cascata (e nao gosto)

Este e o atalho de diagnostico que teria economizado dois dias.

No caso real, o bloco morto mexia em duas coisas: `margin-left` no titulo e `text-align` no container. O botao andou pra esquerda, o titulo continuou centralizado.

Por que: `text-align` e **herdada** e chegava no titulo por outro caminho; `margin` **nao e herdada** e dependia da regra que perdeu o empate.

> **Quando parte de uma mudanca de layout pegou e outra parte nao, e cascata, nao e desalinho de design.** Elemento que anda junto com propriedade herdada e o dedo apontando pro empate de especificidade.

Sintoma tipico: a tela parece "quase certa", com um elemento no lugar novo e outro no lugar velho. Isso nunca e erro de gosto.

---

## 4. Como provar que pegou

**Reler o codigo nao e prova.** A regra original estava correta linha a linha e nao valia nada.

A prova e uma das duas:

1. **Ver a tela** no navegador real, na largura em que a media query dispara.
2. **Devtools**, painel de estilos: a regra que voce escreveu aparece riscada? Entao ela perdeu. Riscado e a resposta, nao a presenca da regra no arquivo.

Vale a regra do fundador que ja governa o resto: quem fecha o portao visual e ele, olhando a tela. Nao anuncie pronto sem ter visto.

---

## 5. Checklist antes de dizer que uma sobrescrita esta pronta

1. O bloco `@media` esta depois de todas as bases que ele sobrescreve?
2. Se ha empate de especificidade, quem vem por ultimo no arquivo e o que eu quero que ganhe?
3. Toda propriedade que eu mexi mudou na tela, ou so as herdadas mudaram?
4. Eu vi a tela na largura certa, ou so reli o codigo?
5. A regra aparece riscada no devtools?

---

## 6. Variavel de CSS dentro de propriedade em transicao nao recalcula (29/08/2026)

Parece o caminho elegante e nao funciona. Vale saber ANTES de escrever, porque a
tentativa parece certa e o defeito e mudo.

**O desenho tentado:** compor o `transform` a partir de variaveis e, no evento,
so trocar o valor delas. O CSS decide a aparencia, o JS so declara o estado.

```css
.cartao { transform: translateX(var(--mover)) rotate(var(--girar)); transition: transform .3s; }
.cartao[data-slot="0"] { --girar: 0deg; }
.cartao[data-slot="-1"] { --girar: -8deg; }
```

**O que acontece de verdade:** trocar o `data-slot` faz a regra nova casar - da
pra provar, porque qualquer propriedade normal da mesma regra (`cursor`,
`z-index`) muda na hora. Mas o `transform` **fica com o valor antigo**. O
elemento nao se mexe.

Medido no navegador em 29/08, e **registrar as variaveis com `@property` nao
resolveu**. O sintoma na tela foi um cartao que ganhava destaque sem sair do
lugar.

### A saida

Quando o valor muda em tempo de execucao e a propriedade esta em `transition`,
**nao passe por variavel**: escreva o valor final direto. Na pratica isso quer
dizer deixar a biblioteca de animacao escrever (ver `movimento_playbook.md`, a
secao de quem manda no transform), que ainda entrega a suavidade de graca.

Variavel de CSS continua otima pro que NAO muda em tempo de execucao: paleta,
espacamento, medida repetida.

### O teste que separa este defeito dos outros dois

Leia, no mesmo instante, uma propriedade da mesma regra que nao seja a
transicionada:

| A outra propriedade | O transform | O que e |
|---|---|---|
| mudou | nao mudou | **este defeito**, ou alguem escrevendo inline por cima |
| nao mudou | nao mudou | cascata: a regra nao esta ganhando (secao 1) |
| mudou | mudou | nao e nenhum dos dois; o problema e o valor |

---

## 7. Aviso cruzado: ferramenta de auditoria envelhece

Achado do mesmo dia, registrado tambem no `senior_dev_playbook.md` da dev-expert.

O projeto tinha `tools/audita_hero.py`, que media a faixa central da foto pra julgar o hero. Depois que o texto saiu do centro, a ferramenta passou a reprovar medindo o pedaco onde o texto nao esta mais: mentira silenciosa, com cara de reprovacao legitima.

**Quando uma mudanca move um elemento de lugar, confira se alguma ferramenta de auditoria assume a posicao antiga.** Auditoria que le posicao fixa precisa ser atualizada junto com o layout, ou vira ruido que atrapalha mais do que ajuda.
