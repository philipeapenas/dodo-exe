# Playbook: Mobile Scroll and Background Fixes

## The `background-attachment: fixed` Issue on Mobile

**Problem:** 
Using `background-attachment: fixed` along with `background-size: cover` causes severe performance issues, repainting bugs, and erratic scrolling behavior on mobile browsers (especially iOS Safari). The background image often zooms in massively or jumps around as the user scrolls.

**Solution:**
Never use `background-attachment: fixed` on the same element that has scrollable content on mobile. Instead, use a fixed pseudo-element (`::before`) or a dedicated background `div` with `position: fixed`.

### Correct Implementation
```css
/* Avoid doing this: */
.hero {
  background-image: url('bg.jpg');
  background-attachment: fixed;
  background-size: cover;
}

/* Do this instead: */
.hero-wrapper {
  position: relative;
  z-index: 1;
}

.hero-background-fixed {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  z-index: -1;
  background: url('bg.jpg') no-repeat center center;
  background-size: cover;
  will-change: transform;
}
```

## Body Scroll Locking
When opening modals or full-screen overlays, always lock the body scroll to prevent the background page from scrolling behind the modal.

```javascript
/* Lock scroll */
document.body.style.overflow = 'hidden';

/* Unlock scroll */
document.body.style.overflow = '';
```

## Best Practices
- **Use `min-height: 100vh` or `min-height: 100dvh`** for sections to ensure they dynamically account for mobile browser UI toolbars (address bar expanding/collapsing).
- **Hardware Acceleration:** Force hardware acceleration on fixed elements using `will-change: transform;` so the GPU handles the rendering.
