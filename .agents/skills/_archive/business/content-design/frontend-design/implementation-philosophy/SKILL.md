---
name: frontend-design-implementation-philosophy
description: 'Sub-skill of frontend-design: Implementation Philosophy.'
version: 2.0.0
category: business
type: reference
scripts_exempt: true
---

# Implementation Philosophy

## Implementation Philosophy


**Match complexity to vision:**

**Maximalist Design:**
```css
/* Elaborate, intentional complexity */
.hero {
  background:
    linear-gradient(135deg, rgba(26, 26, 46, 0.9), rgba(22, 33, 62, 0.8)),
    url('texture.png'),
    radial-gradient(ellipse at 20% 50%, #e94560 0%, transparent 50%);
  backdrop-filter: blur(10px);
}
```

**Minimalist Design:**
```css
/* Restraint and precision */
.hero {
  background: #fafafa;
  padding: 8rem 2rem;
}

.hero h1 {
  font-weight: 300;
  letter-spacing: -0.02em;
  line-height: 1.1;
}
```
