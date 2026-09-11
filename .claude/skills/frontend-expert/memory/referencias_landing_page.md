# Referencias de Landing Page - Onde Buscar Antes de Desenhar

**Versao:** 1.0 | **Data:** 14/08/2026 | **Owner:** frontend-expert
**Origem:** metodo observado num estudo de landing page com IA + pesquisa de validacao das fontes em 14/08/2026.

Este arquivo responde uma pergunta so: **onde eu pego referencia quando preciso montar uma landing page elegante.** Ele nao define criterio estetico - isso e o `direcao_estetica_playbook.md`, que continua sendo o padrao e roda depois desta busca.

---

## Regra 1 - Referencia se COLA, nao se descreve

O achado central do estudo. Descrever estilo em palavras ("moderno, clean, premium") produz o default generico de qualquer IA. Colar um print de uma pagina real dentro do prompt produz direcao.

**Como fazer:**

1. Ache a pagina de referencia numa das galerias abaixo.
2. Copie a IMAGEM (print da pagina, nao o link).
3. Cole junto com a copy, no mesmo prompt.
4. Nao explique o estilo em texto. A imagem ja e a instrucao.

Vale para geracao via Stitch MCP, via Claude Design ou para qualquer ferramenta que aceite imagem no contexto.

**O que a referencia transfere:** estrutura, ritmo de secao, densidade, hierarquia, uso de espaco.
**O que a referencia NAO transfere e voce nao deve deixar transferir:** identidade de marca de terceiro (logotipo, nome, paleta proprietaria, texto). Referencia e esqueleto, nunca copia.

---

## Regra 2 - Escolher a fonte pelo que esta faltando

Nao varra tudo. Identifique o que falta e va na prateleira certa.

### Falta o layout da pagina inteira

Galerias curadas de landing page real, no ar, com screenshot.

| Fonte | Quando usar |
|---|---|
| **land-book.com** | O mais util pra LP de venda e de SaaS. Da pra filtrar por SECAO isolada (bloco de preco, grade de comparacao, prova social) quando voce esta travado so numa parte. Atualiza diario. |
| **lapa.ninja** | Volume grande de LP por ano, com filtro por categoria. Bom pra varrer rapido e achar padrao de mercado. |
| **saaslandingpage.com** | So SaaS, curadoria focada em conversao. Bom pra produto digital e ferramenta. |
| **godly.website** | Lista curta e implacavel. Serve pra calibrar teto de qualidade em 10 minutos, nao pra buscar volume. |
| **awwwards.com** | Teto visual e experimentacao. Cuidado: premia ousadia, nao conversao - referencia daqui costuma custar performance. |
| **muz.li** | Agregador amplo, bom quando o assunto e nichado e as galerias de LP nao tem exemplo. |

**Combinacao que funciona:** uma referencia ambiciosa (godly, awwwards) + uma referencia de conversao (land-book, saaslandingpage). So a primeira produz pagina bonita que nao vende; so a segunda produz pagina correta e esquecivel.

### Falta o componente pronto de codigo

Bibliotecas de componente React + Tailwind, majoritariamente gratuitas, para colar efeito e bloco especifico.

| Fonte | Quando usar |
|---|---|
| **21st.dev** | Ja e o padrao desta skill (Passo 2 da Cadeia de Pensamento). Registro comunitario de componente, com categorias por tipo (`/heros`, `/pricing`, `/buttons`). E onde se pega fundo animado, secao de heroi e bloco de preco. |
| **ui.aceternity.com** | Efeito visual forte: card 3D, holofote, fundo animado, revelacao. Use com a trava do item 4 - e facil exagerar aqui. |
| **magicui.design** | Mais de 150 componentes animados de marketing (marquee, feixe animado, grade bento, efeito de texto). Feito pra landing page, encaixa em base shadcn. |
| **ui.shadcn.com** | A base sobria: formulario, dialogo, tabela, navegacao. Nao e efeito, e fundacao. |
| **float-ui.com / heroui.com** | Alternativas quando as de cima nao tem o bloco. Float UI e Tailwind puro; HeroUI e conjunto coeso com movimento embutido. |

### Falta o conceito visual, nao o codigo

| Fonte | Quando usar |
|---|---|
| **dribbble.com** | Conceito, paleta e composicao. E a fonte usada no estudo: achar um layout que agrada, copiar a imagem, colar no prompt. Aviso: muita peca do Dribbble e conceito que nunca virou site - nao serve como referencia de comportamento nem de responsividade. |
| **behance.net** | Projeto completo com racional de marca. Util quando o cliente ainda nao tem identidade definida. |

---

## Regra 3 - Quantas referencias

**Duas, no maximo tres.** Uma para o esqueleto da pagina, uma para o elemento-assinatura, e no maximo uma para tipografia ou paleta.

Referencia demais nao soma, mistura. Pagina construida a partir de cinco referencias vira colcha de retalhos - o mesmo defeito que o `direcao_estetica_playbook.md` chama de default generico, so que mais caro de consertar.

---

## Regra 4 - A trava anti "cara de IA" continua valendo

Componente pronto resolve acabamento, nao resolve identidade. Fundo animado bonito colado numa pagina sem tese e enfeite.

Antes de aplicar qualquer componente das bibliotecas acima:

1. Passe pelo `direcao_estetica_playbook.md` - o assunto real, a hero como tese, o elemento-assinatura.
2. Gaste a ousadia em **um lugar so**. O componente chamativo e o elemento-assinatura, nao o padrao da pagina inteira.
3. Cheque os 3 cliches de cara de IA listados naquele playbook antes de fechar a paleta.
4. Excesso de animacao e o sinal mais forte de pagina gerada. Biblioteca de efeito torna esse erro barato de cometer - por isso a trava vem aqui.

---

## Regra 5 - Onde isso entra no fluxo

Esta busca acontece no **Passo 2** da Cadeia de Pensamento do `SKILL.md` (Avaliar a Necessidade e Pesquisa de Componentes), ANTES do Passo 3 (Definir Direcao Estetica).

Sequencia completa de uma LP:

```
copy aprovada (copywriter-expert)
  -> buscar referencia aqui (Passo 2)
  -> direcao estetica autoral (Passo 3, direcao_estetica_playbook.md)
  -> gerar/montar (Passo 4)
  -> autocritica e portao de qualidade
```

**A copy vem primeiro, sempre.** Landing page sem copy aprovada nao entra em montagem - o texto define quantas secoes existem, qual e o pico da pagina e onde o CTA cai. Montar antes obriga a remontar depois. Se chegar pedido de LP sem copy, devolva pra `copywriter-expert` antes de desenhar qualquer coisa.

---

## Regra 6 - Limitacoes conhecidas

- **Ferramenta que gera pagina nem sempre publica.** O Claude Design, por exemplo, exporta HTML mas nao tem botao de publicar. O caminho de publicacao no ecossistema continua sendo a Vercel (`vercel-expert`).
- **Componente de biblioteca costuma vir React + Tailwind.** Em projeto estatico de HTML e CSS puro do ecossistema, o componente e referencia de comportamento e visual, nao codigo pra colar direto. Portar exige a `dev-expert` para a parte de JS.
- **Referencia de galeria premiada e pesada.** Video de fundo, sequencia de quadros e animacao continua custam carregamento. Em pagina de trafego pago, velocidade e conversao - calibre antes de copiar o efeito.
