---
name: elite-frontend-ux-9-pre-delivery-checklist
description: 'Sub-skill of elite-frontend-ux: 9. Pre-Delivery Checklist.'
version: 1.0.0
category: development
type: reference
scripts_exempt: true
---

# 9. Pre-Delivery Checklist

## 9. Pre-Delivery Checklist


Before delivering any frontend code, verify all items:

**Accessibility**
- [ ] Color contrast ≥4.5:1 text / ≥3:1 UI components
- [ ] Touch targets ≥44×44px
- [ ] All images have `alt` text (decorative: `alt=""`)
- [ ] All form fields have `<label>`
- [ ] Visible focus states on all interactive elements
- [ ] No color-only information conveyance

**Visual Design**
- [ ] Clear typographic hierarchy (3–5 levels)
- [ ] Consistent spacing from token scale
- [ ] Max 2–3 typefaces
- [ ] Cohesive 60/30/10 color palette
- [ ] ONE memorable design element present

**Technical**
- [ ] Mobile-first responsive approach
- [ ] Animations use only `transform`/`opacity`
- [ ] No dynamic Tailwind class names
- [ ] `cn()` helper used for class merging
- [ ] Dark mode support via CSS variables
- [ ] `prefers-reduced-motion` respected

**UX Integrity**
- [ ] Single primary goal per page
- [ ] No dark patterns or confirmshaming
- [ ] Footer always accessible
- [ ] Error states are descriptive and helpful
- [ ] Loading states exist for all async operations
- [ ] Empty states have helpful action prompts

---
