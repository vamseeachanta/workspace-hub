---
name: web-artifacts-builder-performance
description: 'Sub-skill of web-artifacts-builder: Performance (+2).'
version: 2.0.0
category: _internal
type: reference
scripts_exempt: true
---

# Performance (+2)

## Performance


1. **Minimize dependencies**: Only include what you need
2. **Use CDN with version pinning**: `library@4.4.0` not `library@latest`
3. **Lazy load when possible**: Defer non-critical scripts
4. **Optimize images**: Use SVG or base64 for small images


## Accessibility


```html
<!-- Always include -->
<html lang="en">
<meta name="viewport" content="width=device-width, initial-scale=1.0">

<!-- Use semantic HTML -->
<main>, <nav>, <article>, <section>, <header>, <footer>

<!-- Add ARIA labels -->
<button aria-label="Close dialog">x</button>

<!-- Ensure color contrast -->
/* Minimum 4.5:1 for normal text */
```


## Responsive Design


```css
/* Mobile-first approach */
.container {
    padding: 10px;
}

@media (min-width: 768px) {
    .container {
        padding: 20px;
    }
}

@media (min-width: 1024px) {
    .container {
        max-width: 1200px;
        margin: 0 auto;
    }
}
```
