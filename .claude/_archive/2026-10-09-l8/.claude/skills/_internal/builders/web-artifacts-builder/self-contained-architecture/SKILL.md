---
name: web-artifacts-builder-self-contained-architecture
description: 'Sub-skill of web-artifacts-builder: Self-Contained Architecture (+1).'
version: 2.0.0
category: _internal
type: reference
scripts_exempt: true
---

# Self-Contained Architecture (+1)

## Self-Contained Architecture


Everything in one HTML file:
- HTML structure
- CSS styles (inline or in `<style>` tags)
- JavaScript functionality (inline or in `<script>` tags)
- Data (embedded JSON or JavaScript objects)
- Assets (inline SVG, base64 images, or CDN links)

## No External Dependencies Required


```html
<!-- Use CDN for libraries when needed -->
<script src="https://cdn.jsdelivr.net/npm/library@version"></script>

<!-- Or embed everything inline -->
<script>
// All JavaScript here
</script>
```
