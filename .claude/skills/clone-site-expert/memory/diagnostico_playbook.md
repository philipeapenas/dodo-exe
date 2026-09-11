# Playbook de Diagnostico de Site Baixado

**Versao:** 1.0 | **Data:** 15/08/2026 | **Owner:** clone-site-expert
**Origem:** a primeira execucao completa num espelho de site real, baixado com HTTrack.

A ordem importa. Varrer no chute faz voce achar o obvio e perder o que esta escondido dentro do bundle.

---

## 1. Identificar a stack, com evidencia

Nunca declare a stack de memoria. Cada afirmacao sai de um sinal no arquivo:

| Sinal no arquivo | O que prova |
| --- | --- |
| pasta `_next/static/chunks/app/` + payload com `buildId` | Next.js com App Router |
| marcadores `$L` e `$I` no HTML, `ClientPageRoot` | React com Server Components |
| utilitario com escape (`hover\:underline`), variaveis `--tw-*` | Tailwind compilado |
| `.woff2` local com `unicode-range` por subset | `next/font` auto-hospedando |
| snippet com `vercel.live` e `deploymentId` no runtime | hospedado na Vercel |

---

## 2. Rastreamento: procurar por familia, nao por palavra solta

Varra o espelho inteiro por familia. O valor esta em relatar tambem **o que nao existe**:

```
fbq | connect.facebook.net | hotjar | clarity.ms | tiktok | doubleclick
gtag | googletagmanager | AW- | UA- | GTM- | G- | recaptcha | vercel.live
```

**Falso positivo conhecido:** `doubleclick` aparece dentro do React DOM - e o nome do evento `ondoubleclick`, nao rastreador. Sempre confirme em qual arquivo o termo caiu antes de reportar.

**Nao pare no HTML.** O disparo de evento costuma morar num modulo do bundle. Procure o helper que chama `sendGAEvent` e liste **os eventos custom por nome** (`whatsapp_click`, `briefing_submit`): e isso que revela o que o dono media de verdade.

**Procure segredo tambem:** `sk_live`, `pk_live`, `AIza...`, `eyJ...`, `Bearer`. Achar nada e resultado que vale reportar.

---

## 3. Separar rastreador de afirmacao de propriedade

Nem tudo que identifica o dono rastreia alguem. **Explique a diferenca** em vez de tratar tudo como lixo:

| Achado | Rastreia? | Por que sai mesmo assim |
| --- | --- | --- |
| GA4 / Pixel / GTM | Sim | manda a visita pro painel do dono original |
| `facebook-domain-verification` | **Nao** | e o token que prova ao Meta que o dominio e dele. Se ficar, voce afirma ao Facebook que o dominio e dele |
| Toolbar da Vercel + `deploymentId` | So pra quem tem o cookie | entrega de qual deploy o site saiu |

---

## 4. Identidade do dono

Procure e liste **onde cada coisa aparece**, porque quase sempre esta em dois lugares:

- telefone e link de WhatsApp
- dominio (canonical, `og:url`, twitter, JSON-LD, nome da pasta)
- nome da marca (logo, titulo da aba, JSON-LD)
- `og:image` **gerada em runtime** (`/opengraph-image?hash`) - ela nao vem no download. Publicar assim faz o preview puxar a imagem **do servidor dele**, e quebrar quando ele tirar do ar
- favicon

**Procure o objeto de config.** Site bem feito concentra marca, telefone, preco e prazo num modulo so. Achar isso muda o custo da modelagem inteira - vale destacar no diagnostico.

---

## 5. O que o HTTrack quebra

Confirme sempre, sao os quatro de praxe:

1. **`canonical` corrompido** - a URL absoluta vira caminho de arquivo (`href="index.html"`). Acontece tambem dentro do JSON-LD embutido no payload.
2. **Rota de servidor morta** - `POST /api/...` nao existe em site estatico. Formulario que dependia disso **nao envia nada**. Confirme com `curl`, nao suponha.
3. **Pagina alcancavel so por navegacao** (a de obrigado, tipicamente) nao foi baixada.
4. **Comentario `Mirrored from` e `Added by HTTrack`** no topo e no rodape de cada HTML.

Some `robots.txt` e `sitemap.xml`, que normalmente nao vem.

---

## 6. Onde a copy realmente mora

**Este e o achado que mais muda o rumo do projeto.**

Em site React, parte do texto so existe **dentro do bundle minificado**, nao no HTML. No precedente, as seis respostas do FAQ estavam so no JavaScript: quem lesse o HTML acharia as perguntas sem as respostas.

Duas consequencias que voce precisa reportar:

- **O React vira obrigatorio.** Nao da pra descartar o bundle sem perder conteudo.
- **A `copywriter-expert` sozinha nao ve a pagina inteira.** Entregue a ela o **mapa de onde mora cada texto**, senao ela disseca material incompleto e da nota numa pagina que nao existe.

---

## 7. Otimizacao: separar o real do ilusorio

Seja honesto sobre o ganho. Duas armadilhas classicas:

- **`polyfills.js` com `noModule`** - navegador moderno **nem baixa**. Apagar limpa o repositorio, nao acelera nada.
- **Subset de fonte fora do alfabeto usado** (cirilico, grego) - o navegador ja so baixa o subset que precisa, por `unicode-range`. De novo: economia de disco, nao de banda.

Diga isso com todas as letras. Prometer velocidade que nao vem e pior que nao otimizar.

**E confira a contrapartida:** ao apagar arquivo, **remova tambem a tag que aponta pra ele**. No precedente o `polyfills.js` foi apagado e a `<script>` ficou - um 404 em toda carga da home, que so apareceu quando o `conferir_referencias.py` passou a existir.
