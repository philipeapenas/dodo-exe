# Playbook de Modo Escuro e Troca de Tema

**Versao:** 1.0 | **Data:** 15/08/2026 | **Owner:** frontend-expert
**Origem:** nascido num site de vendas, a partir do efeito de gota de troca de tema de um checkout (classe `.dark-mode-circle`).

Companheiro do `movimento_playbook.md`: la esta a coreografia de rolagem, aqui esta a troca de tema. Consulte sempre que um site levar modo escuro.

---

## 1. Antes de tudo: o CSS aceita classe nova?

Site montado com Tailwind **compilado e purgado** (tipico de espelho de site baixado, ou de build entregue sem o projeto) so contem as classes que o site original usava. Escrever `dark:bg-slate-900` ali nao gera erro: gera **elemento sem estilo**, e nada avisa.

**Sempre confira antes de escrever a primeira linha:**

```
python tools/conferir_classes.py site
```

Esse script (precedente em `Projetos/Dominio/vitrine-rapida/tools/`) extrai todo seletor de classe do CSS compilado e compara com o que o HTML usa. Ele ja pegou `ml-1` e `pb-20` que simplesmente nao existiam - o logo estava com as duas palavras grudadas e ninguem tinha visto.

**Consequencia pratica:** em site purgado, o modo escuro **nao** usa variante `dark:`. Ele mora num arquivo proprio (`tema.css`), com seletores sob `:root[data-tema="escuro"]`.

---

## 2. A regra de traducao pro escuro

Tailwind compilado grava a cor em `rgb()` cravado, nao em variavel. Nao existe "virar um token e pronto": cada classe que carrega cor precisa ser reescrita. Sao dezenas de regras, e sem um criterio unico vira tentativa e erro.

**O criterio e um so, e resolve todos os casos:**

> Superficie que **continua clara** mantem borda e sombra escuras.
> Superficie que **escurece** ganha borda e sombra claras.

A relacao entre o elemento e o fundo dele e preservada; o que virou foi o fundo da pagina.

Na pratica, tres grupos:

| Grupo | O que fazer | Exemplo |
| --- | --- | --- |
| Superficie que segue clara (cartao da cor da marca) | **Nao mexe no desenho.** So trave a cor do texto, porque a regra global de texto claro vaza pra dentro dele | cartao amarelo continua amarelo com texto preto |
| Superficie que escurece (cartao branco, campo de formulario) | Fundo escuro, borda e sombra claras, texto claro | cartao branco vira grafite com contorno claro |
| Peca de fundo escuro sobre pagina escura | Ganha **contorno claro**, senao some no fundo | selo preto, chip de icone, numero de passo |

**A cor de destaque da marca nao muda.** E ela que mantem o site reconhecivel nos dois modos.

**Nao inverta o preto puro pro branco puro.** Use um escuro quente/frio coerente com a paleta clara (ex: creme `#fbefe3` vira `#14120e`, nao `#000`).

---

## 3. A gota: as tres precondicoes

O efeito e um circulo que cresce do centro com `clip-path`, revelando o tema novo **atras do conteudo**. Quem ja tentou colocar por cima sabe que fica errado: a gota tapa o texto.

Pra ela correr atras, **as tres coisas precisam ser verdade ao mesmo tempo**. Faltando uma, ou a gota nao aparece, ou ela cobre o conteudo:

1. **O fundo tem que estar no `html`, nao so no `body`.**
   Um elemento com `z-index` negativo e pintado **depois** do fundo do `html` e **antes** do fundo do `body`. Cor so no body = body tapa a gota.

2. **O `body` fica transparente durante a troca.**
   Pelo mesmo motivo do item 1.

3. **O `html` segura a cor ANTIGA enquanto a gota corre.**
   Congelado por estilo direto no elemento, via JS. Se o html ja assumir a cor nova quando o tema virar, nao sobra contraste nenhum pra gota revelar - ela fica invisivel e parece que o efeito nao existe.

```css
:root { background-color: <claro>; }
:root[data-tema="escuro"] { background-color: <escuro>; }

:root.trocando-tema body { background-color: transparent; }

.gota-tema {
  position: fixed; inset: 0;
  z-index: -1;
  pointer-events: none;
  background: <cor do tema de destino>;
  clip-path: circle(0% at 50% 50%);
  transition: clip-path .8s cubic-bezier(.4, 0, .2, 1);
  will-change: clip-path;
}
.gota-tema.expandir { clip-path: circle(150% at 50% 50%); }
```

---

## 4. O timing de 80ms (o erro mais facil de cometer)

**O tema vira aos 80ms, quase junto com o inicio da gota. NAO quando ela termina.**

E contraintuitivo e a intuicao erra feio aqui. Trocar aos 420ms "pra esperar a gota cobrir" produz exatamente o defeito que o fundador reportou: durante a varredura a headline fica **escura sobre fundo escuro**, e a cor do site parece mudar com atraso.

O motivo e estrutural: a gota corre **atras** do conteudo. O texto tem que ja estar na cor nova enquanto o fundo novo varre por tras dele. Nao existe momento "seguro" pra esperar.

```js
var TROCA = 80;    // tema vira aqui
var FIM = 1480;    // gota sai de cena aqui
```

---

## 5. A cor derrete, nao salta

So a gota nao basta. Sem transicao, todo elemento troca de cor no mesmo quadro e o corte fica **seco**, brigando com a suavidade da varredura. Com transicao, a cor derrete enquanto a gota corre e as duas coisas viram um movimento so.

```css
:root.trocando-tema *:not(.gota-tema),
:root.trocando-tema *:not(.gota-tema)::before,
:root.trocando-tema *:not(.gota-tema)::after {
  transition: background-color .45s ease, color .45s ease,
              border-color .45s ease, box-shadow .45s ease !important;
}
```

**Duas coisas nao negociaveis nessa regra:**

- **So durante a troca**, sob a classe temporaria. Transicao global permanente encarece todo hover e toda animacao da pagina pra sempre.
- **A gota fica de fora.** Ela anima `clip-path`; o seletor universal sobrescreveria a transicao dela e o efeito inteiro morreria.

---

## 6. Dois modos, e nada de piscada

**Piscada de tema errado:** a decisao do tema vai num script curto no `<head>`, antes da pagina pintar. Se ficar junto do resto do JS, o visitante ve o site claro aparecer e escurecer em seguida.

```html
<script>(function(){try{var t=localStorage.getItem("chave");
if(t!=="claro"&&t!=="escuro"){t=matchMedia("(prefers-color-scheme: dark)").matches?"escuro":"claro";}
document.documentElement.setAttribute("data-tema",t);}catch(e){}})();</script>
```

**Menos movimento:** quem pede `prefers-reduced-motion` troca direto, sem gota. Diferente da coreografia de rolagem, aqui **desligar e correto** - a troca instantanea ainda entrega o modo escuro inteiro, nao entrega uma pagina morta.

**Quem nunca escolheu acompanha o sistema**, inclusive se ele mudar com a aba aberta (`matchMedia().addEventListener("change")`).

**Clique repetido nao empilha gota.** Guarda simples: se ja existe `.gota-tema` no documento, ignora.

---

## 7. Em pagina hidratada por React

Se o site e espelho estatico hidratado (HTML tem que bater com o bundle), o botao de troca e criado por JS e pendurado no `<body>`, **fora da arvore do React**. Elemento estranho dentro da arvore quebra a hidratacao.

---

## 8. O caminho nativo: View Transitions API

Hoje existe caminho nativo pra esse efeito: `document.startViewTransition()` com `::view-transition-new(root)` recortado por `clip-path` de `circle(0)` a `circle(raio maximo)`. E **Baseline para fluxo de mesma pagina**, com suporte em Chrome, Edge e Opera a partir da versao 111.

**A vantagem estrutural:** o navegador tira um instantaneo do estado antigo e revela o novo por cima. Como o snapshot antigo continua na tela, **o problema do item 4 simplesmente nao existe** - nao ha texto na cor errada durante a varredura, e nao ha timing pra acertar.

**Quando usar cada um:**

- **Nativo** em projeto novo, onde da pra assumir navegador atual e o fallback e a troca seca (aceitavel).
- **A gota manual** deste playbook quando o efeito precisa valer em qualquer navegador, ou quando o site e espelho editado a mao e voce quer controle total do que acontece em cada milissegundo.

Nos dois casos, refinamento que vale: centrar o circulo **no botao clicado** em vez do centro da tela, usando as coordenadas do clique.

---

## Checklist antes de entregar

- [ ] Rodou o conferidor de classes e nenhuma classe usada esta fora do CSS?
- [ ] Recarregou a pagina no escuro e ela **nao** piscou clara antes?
- [ ] Durante a varredura, o texto ja esta na cor nova (nao escuro sobre escuro)?
- [ ] A gota aparece mesmo, ou o fundo do body esta tapando ela?
- [ ] A transicao de cor sai junto da gota, sem corte seco?
- [ ] Ligou "reduzir movimento" e a troca acontece direto, sem gota?
- [ ] Clicou varias vezes seguidas e nao empilhou gota?
- [ ] Peca de fundo escuro (selo, chip) continua visivel sobre o fundo escuro?
