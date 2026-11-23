---
name: frontend-design-cards-with-character
description: 'Sub-skill of frontend-design: Cards with Character (+1).'
version: 2.0.0
category: business
type: reference
scripts_exempt: true
---

# Cards with Character (+1)

## Cards with Character

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


## Navigation with Presence

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
