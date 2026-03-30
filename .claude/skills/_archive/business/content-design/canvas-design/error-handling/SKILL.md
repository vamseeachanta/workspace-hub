---
name: canvas-design-error-handling
description: 'Sub-skill of canvas-design: Error Handling.'
version: 2.0.0
category: business
type: reference
scripts_exempt: true
---

# Error Handling

## Error Handling


### Common Issues


**Issue: Artifacts appear pixelated**
- Cause: Low resolution or aggressive compression
- Solution: Use 300+ DPI, quality=95 for PNG

**Issue: Colors print differently than screen**
- Cause: RGB to CMYK conversion
- Solution: Design in CMYK for print, or soft-proof

**Issue: Elements appear misaligned**
- Cause: Floating-point rounding errors
- Solution: Use integer coordinates, snap to grid

**Issue: File size too large**
- Cause: High resolution bitmap
- Solution: Use vector (SVG/PDF) where possible
