# Prompts Stitch: Por Página

Prompts pré-aprovados para geração de design via `generate_screen_from_text`. Usar `model_id: "GEMINI_3_PRO"` para designs elaborados, `"GEMINI_3_FLASH"` para iterações rápidas.

---

## `index.html`: Página Principal

```
Mobile-first link-in-bio page. Dark background #101010.
Full-screen background slideshow with dark overlay rgba(0,0,0,0.3).
Stories-style progress bars at top (height 3px, white, animated fill).
Circular profile photo, bold white profile name, light bio text.
Instagram and TikTok SVG icons with subtle hover effect.
Glassmorphism link card: backdrop-filter blur 16px,
background rgba(255,255,255,0.08), border 1px solid rgba(255,255,255,0.12),
border-radius 16px, card background image with icon and title overlay.
Card hover: scale(1.02) with subtle glow.
Max-width 480px centered on desktop. Desktop background MUST use a full-screen, heavily blurred layer mirroring the slideshow images, positioned behind the mobile container.
Avoid Inter/Roboto fonts, use a characterful typeface.
```

---

## `presell-instagram.html`

```
Presell bridge page for Instagram in-app browser.
Dark navy background #0a0a2e. Single centered white card.
Circular profile photo at top of card. Message text below.
Large blue CTA button "Continue". Minimal, no distractions.
Single fade-in entrance animation under 300ms.
```

---

## `presell-tiktok.html`

```
Instructional page for TikTok in-app browser users.
Clean white background. Large bold title at top.
Two numbered steps with emoji icons (👆 and 📱).
Step 1: tap the ··· menu top right. Step 2: open in browser.
No redirect button, instructional only. Clear readable typography.
Mobile-optimized layout.
```
