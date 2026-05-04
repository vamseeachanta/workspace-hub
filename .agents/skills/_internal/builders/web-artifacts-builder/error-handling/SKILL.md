---
name: web-artifacts-builder-error-handling
description: 'Sub-skill of web-artifacts-builder: Error Handling.'
version: 2.0.0
category: _internal
type: reference
scripts_exempt: true
---

# Error Handling

## Error Handling


### Common Issues


**Issue: CDN library not loading**
- Cause: Network issue or wrong URL
- Solution: Pin version, add fallback, test offline

**Issue: File doesn't open in browser**
- Cause: Browser blocking local file access
- Solution: Use a simple HTTP server or data: URLs

**Issue: Charts not rendering**
- Cause: DOM not ready when script runs
- Solution: Use DOMContentLoaded event

**Issue: Styles not applying**
- Cause: CSS specificity or load order
- Solution: Use more specific selectors, check order
