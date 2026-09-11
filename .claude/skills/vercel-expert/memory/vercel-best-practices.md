# Vercel & Vanilla JS Best Practices

## Recommended Directory Structure
For projects that do not use frameworks (React, Vue, etc.), Vercel serves static files perfectly. Clear separation makes it easier for the server to read and for future maintainers to understand:

- `index.html`: Project entry point.
- `css/`: All page styling. Modularize if the project starts to grow (e.g., `reset.css`, `layout.css`).
- `js/`: Client-side logic.
- `assets/`: Static images, short videos, icons, and local fonts.

## Configuration: `vercel.json`
Although Vercel auto-detects static files in the root, having an explicit `vercel.json` is excellent practice for:

1. **Clean URLs (Remove `.html` extensions from the URL):**
```json
{
  "cleanUrls": true,
  "trailingSlash": false
}
```

2. **Headers and Caching:** To optimize the loading of static assets (fonts, images).
```json
{
  "cleanUrls": true,
  "headers": [
    {
      "source": "/assets/(.*)",
      "headers": [
        {
          "key": "Cache-Control",
          "value": "public, max-age=31536000, immutable"
        }
      ]
    }
  ]
}
```

## HTML/CSS/JS Practices (Vanilla)
- **HTML:** Always use HTML5 semantic tags (`<header>`, `<main>`, `<section>`, `<footer>`, `<nav>`). Add important SEO meta tags and viewport configuration in the `<head>` tag.
- **CSS:** Avoid inline styles. Centralize styling in a main style file (`style.css`), or import small CSS modules via at-rules (e.g., `@import`), always aiming for clarity.
- **JS:** Insert your scripts at the bottom of the `<body>` or in the `<head>` specifying the `defer` attribute (`<script src="js/main.js" defer></script>`), ensuring DOM loading isn't blocked by the script download.

**Note for this Skill:** When structuring new static projects, apply these guidelines strictly, ensuring a clean, performant repository immediately prepared for deployment on Vercel (Production-Ready).
