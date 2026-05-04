---
name: frontend-design-typography
description: 'Sub-skill of frontend-design: Typography (+3).'
version: 2.0.0
category: business
type: reference
scripts_exempt: true
---

# Typography (+3)

## Typography


**Prioritize characterful, unexpected font selections:**

```css
/* Good: Distinctive choices */
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;600;700&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Crimson+Pro:ital,wght@0,400;0,600;1,400&display=swap');

/* Avoid: Overused defaults */
/* Inter, Roboto, Arial, system fonts */
```

**Font Pairing Examples:**
- Headlines: Space Grotesk / Body: Source Serif Pro
- Headlines: Playfair Display / Body: Work Sans
- Headlines: Sora / Body: Spectral


## Color


**Commit to cohesive palettes:**

```css
:root {
  /* Bold, intentional palette */
  --primary: #1a1a2e;
  --secondary: #16213e;
  --accent: #e94560;
  --highlight: #0f3460;
  --text: #eaeaea;

  /* Not: Generic blue gradients on white */
}
```

**Palette Strategies:**
- Monochromatic with sharp accent
- Analogous with deliberate contrast
- Split-complementary for energy
- Dark mode as default, not afterthought


## Motion


**Employ CSS animations strategically:**

```css
/* Subtle entrance */
@keyframes fadeSlideIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.card {
  animation: fadeSlideIn 0.6s ease-out;
}

/* Micro-interaction */
.button {
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.button:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
}
```

**Scroll-triggered effects:**
```javascript
const observer = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.classList.add('animate-in');
    }
  });
}, { threshold: 0.1 });

document.querySelectorAll('.animate-on-scroll').forEach(el => {
  observer.observe(el);
});
```


## Spatial Design


**Embrace asymmetry and grid-breaking:**

```css
.hero {
  display: grid;
  grid-template-columns: 1fr 1.5fr;
  gap: 4rem;
  align-items: end; /* Intentional misalignment */
}

.feature-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 2rem;
}

/* Break the grid for emphasis */
.feature-grid .featured {
  grid-column: span 2;
  grid-row: span 2;
}
```

**Overlap and layering:**
```css
.overlapping-section {
  position: relative;
  margin-top: -100px;
  z-index: 10;
}

.floating-element {
  position: absolute;
  transform: translate(-20%, -50%);
}
```
