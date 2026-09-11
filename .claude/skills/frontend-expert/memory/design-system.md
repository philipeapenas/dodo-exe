# Design System: Vitrine De Links

Tokens visuais, padrões de código e estrutura do projeto. Consultar antes de qualquer alteração visual.

---

## Design Principles

- **Mobile-first**: max-width ~480px, centralizado no desktop. **Background Desktop:** Nunca usar fundo preto liso ou cores sólidas; usar sempre a mesma imagem/slideshow do centro, esticada em 100vw com heavy glassmorphism blur (ex: `filter: blur(40px) brightness(0.4)`) por trás do conteúdo principal.
- **Dark backgrounds**: `#101010` padrão; navy `#0a0a2e` para presell pages
- **Glassmorphism**: `backdrop-filter: blur(16px)`, `rgba(255,255,255,0.08)`, `border-radius: 16px`
- **Overlay**: sempre `rgba(0,0,0,0.3)` sobre imagens de fundo
- **Fontes**: evitar Inter/Roboto; preferir DM Sans, Syne, Clash Display, Plus Jakarta Sans
- **Slideshow**: fade via CSS `opacity`, nunca JS transforms (mais suave no mobile)
- **Progress bars**: `@keyframes progressFill` animando `width: 0% → 100%`

---

## User-Agent Detection

Sempre manter no topo do `script.js`:

```js
(function () {
  const ua = navigator.userAgent || "";
  if (/Instagram/i.test(ua)) {
    window.location.replace("presell-instagram.html");
    return;
  }
  if (/TikTok|ByteDance|musical_ly/i.test(ua)) {
    window.location.replace("presell-tiktok.html");
    return;
  }
})();
```

---

## Estrutura do Projeto

```
project-root/
├── .agents/skills/frontend-expert/  ← skill encapsulada
│   ├── SKILL.md                    ← cérebro
│   ├── memory/                     ← memória (prompts, design tokens)
│   ├── tools/                      ← scripts e MCPs
│   └── Referencia/                 ← screenshots visuais aprovados
├── assets/photos/                  ← fotos do usuário
├── config.js                       ← fonte de verdade (nunca hardcodar fora)
├── index.html
├── style.css
├── script.js
├── presell-instagram.html
├── presell-tiktok.html
├── implementation_plan.md
└── walkthrough.md
```

Sempre ler `config.js` e `implementation_plan.md` antes de qualquer alteração.
