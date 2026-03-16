---
name: frontend-design-common-issues
description: 'Sub-skill of frontend-design: Common Issues.'
version: 2.0.0
category: business
type: reference
scripts_exempt: true
---

# Common Issues

## Common Issues


**Issue: Design looks generic**
- Cause: Using default fonts and colors
- Solution: Audit for Inter/Roboto/system fonts, replace with distinctive choices

**Issue: Animations feel janky**
- Cause: Using wrong easing or duration
- Solution: Use `ease-out` for entrances, keep durations 200-600ms

**Issue: Layout breaks on mobile**
- Cause: Fixed widths or no responsive breakpoints
- Solution: Use relative units, add media queries, test at 320px

**Issue: Colors clash in dark mode**
- Cause: Using light-mode palette directly
- Solution: Design dark mode first, derive light mode from it
