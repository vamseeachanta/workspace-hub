---
name: elite-frontend-ux-contrast-wcag-21-aa
description: 'Sub-skill of elite-frontend-ux: Contrast (WCAG 2.1 AA) (+4).'
version: 1.0.0
category: development
type: reference
scripts_exempt: true
---

# Contrast (WCAG 2.1 AA) (+4)

## Contrast (WCAG 2.1 AA)

| Element | Minimum ratio |
|---------|--------------|
| Body text | 4.5:1 |
| Large text (18pt+ or 14pt bold) | 3:1 |
| UI components, icons | 3:1 |
| Focus indicators | 3:1 |


## Touch Targets

- Minimum size: 44×44px
- Minimum spacing between adjacent targets: 8px


## Interactive Elements

- ALL interactive elements MUST have visible focus states
- NEVER use `outline: none` without a replacement
- Tab order must be logical; avoid `tabindex > 0`


## Forms

- Every input MUST have an associated `<label>` (not just placeholder)
- Error messages: use `aria-describedby` to associate with input
- Don't disable submit buttons before first submission attempt
- Use `autocomplete` attributes


## Semantic HTML (first rule of ARIA: don't use ARIA if native HTML works)

```html
<!-- CORRECT -->
<button type="button">Action</button>
<a href="/page">Navigate</a>

<!-- WRONG -->
<div onclick="...">Action</div>
<span class="link">Navigate</span>
```

---
