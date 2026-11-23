---
name: theme-factory-error-handling
description: 'Sub-skill of theme-factory: Error Handling.'
version: 2.0.0
category: business
type: reference
scripts_exempt: true
---

# Error Handling

## Error Handling


### Common Issues


**Issue: Fonts not loading**
- Cause: Missing Google Fonts import or network issue
- Solution: Verify import URL, add fallback fonts in font-family

**Issue: Colors look washed out**
- Cause: Theme designed for dark mode used on light background
- Solution: Swap primary/text colors or choose light-mode theme

**Issue: Poor contrast ratio**
- Cause: Using accent color for body text
- Solution: Use text color for body, accent only for highlights

**Issue: Theme doesn't match brand**
- Cause: Using preset without customization
- Solution: Generate custom theme with brand colors as inputs
