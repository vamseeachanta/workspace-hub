---
name: frontend-design
description: Create distinctive, production-grade web interfaces with high design quality. Use for components, pages, dashboards, and full applications that need to stand out from generic AI aesthetics.
---

# Frontend Design Skill

## Overview

This skill enables creation of distinctive, production-grade web interfaces that prioritize high design quality and avoid generic aesthetics. It applies to components, pages, dashboards, and full applications.

## Before Coding: Design Direction

Establish a bold aesthetic direction by considering:

1. **Purpose**: What is this interface trying to accomplish?
2. **Tone**: Professional? Playful? Minimalist? Bold?
3. **Constraints**: Technical requirements, brand guidelines, accessibility?
4. **Differentiation**: How will this stand out?

**Key Principle**: Choose a clear conceptual direction and execute it with precision.

## Visual Execution

### Typography

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

### Color

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

### Motion

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

### Spatial Design

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

## Critical Warnings: What to Avoid

### Generic AI Aesthetics
- Overused font families (Inter, Roboto, Arial)
- Purple gradients on white backgrounds
- Uniform rounded corners everywhere
- Centered everything
- Cookie-cutter card layouts

### Predictable Patterns
- Hero with centered text + button + stock photo
- 3-column equal grids
- Default shadows and border-radius
- Lack of visual hierarchy
- No personality or context-specific character

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

## Component Patterns

### Cards with Character
```html
<div class="card">
  <div class="card-accent"></div>
  <div class="card-content">
    <span class="card-tag">Featured</span>
    <h3>Card Title</h3>
    <p>Description text with purpose.</p>
  </div>
</div>

<style>
.card {
  position: relative;
  background: #1a1a2e;
  border-radius: 0; /* Intentional sharp corners */
  overflow: hidden;
}

.card-accent {
  position: absolute;
  top: 0;
  left: 0;
  width: 4px;
  height: 100%;
  background: linear-gradient(180deg, #e94560, #0f3460);
}

.card-content {
  padding: 2rem;
}

.card-tag {
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: #e94560;
}
</style>
```

### Navigation with Presence
```html
<nav class="nav">
  <a href="/" class="nav-logo">Brand</a>
  <div class="nav-links">
    <a href="#" class="nav-link active">Home</a>
    <a href="#" class="nav-link">Work</a>
    <a href="#" class="nav-link">About</a>
    <a href="#" class="nav-cta">Contact</a>
  </div>
</nav>

<style>
.nav {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem 4rem;
  background: transparent;
  position: fixed;
  width: 100%;
  z-index: 100;
  mix-blend-mode: difference;
}

.nav-logo {
  font-weight: 700;
  font-size: 1.25rem;
  color: white;
}

.nav-link {
  color: white;
  text-decoration: none;
  position: relative;
}

.nav-link::after {
  content: '';
  position: absolute;
  bottom: -4px;
  left: 0;
  width: 0;
  height: 2px;
  background: #e94560;
  transition: width 0.3s ease;
}

.nav-link:hover::after,
.nav-link.active::after {
  width: 100%;
}
</style>
```

## Framework Integration

### Tailwind CSS (Custom Config)
```javascript
// tailwind.config.js
module.exports = {
  theme: {
    extend: {
      fontFamily: {
        'display': ['Space Grotesk', 'sans-serif'],
        'body': ['Spectral', 'serif'],
      },
      colors: {
        'midnight': '#1a1a2e',
        'navy': '#16213e',
        'coral': '#e94560',
        'ocean': '#0f3460',
      },
      animation: {
        'fade-in': 'fadeIn 0.6s ease-out',
        'slide-up': 'slideUp 0.6s ease-out',
      },
    },
  },
}
```

### React Components
```jsx
const Button = ({ children, variant = 'primary', ...props }) => {
  const baseStyles = `
    px-6 py-3 font-display font-semibold
    transition-all duration-300
    focus:outline-none focus:ring-2 focus:ring-offset-2
  `;

  const variants = {
    primary: 'bg-coral text-white hover:bg-opacity-90 focus:ring-coral',
    secondary: 'bg-transparent border-2 border-coral text-coral hover:bg-coral hover:text-white',
    ghost: 'bg-transparent text-coral hover:underline',
  };

  return (
    <button className={`${baseStyles} ${variants[variant]}`} {...props}>
      {children}
    </button>
  );
};
```

## Design Checklist

- [ ] Established clear design direction before coding
- [ ] Selected distinctive typography (not defaults)
- [ ] Created intentional color palette
- [ ] Added purposeful motion and interaction
- [ ] Broke visual monotony with asymmetry/variation
- [ ] Avoided generic AI aesthetic patterns
- [ ] Matched complexity to design vision
- [ ] Tested across viewport sizes

## Philosophy

**Claude is capable of extraordinary creative work. Don't hold back.**

Design complexity should match the aesthetic vision—maximalist designs warrant elaborate animations; minimalist approaches require restraint and precision. The right amount of design is whatever serves the purpose with distinction.

---

## Version History

- **1.0.0** (2024-10-15): Initial release with typography, color, motion, spatial design patterns, component examples, Tailwind/React integration
