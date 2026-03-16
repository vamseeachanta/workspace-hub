---
name: algorithmic-art-error-handling
description: 'Sub-skill of algorithmic-art: Error Handling.'
version: 2.0.0
category: business
type: reference
scripts_exempt: true
---

# Error Handling

## Error Handling


### Common Issues


**Issue: Different output on reload**
- Cause: Missing randomSeed/noiseSeed call
- Solution: Always call both at start of generate()

**Issue: Performance is slow**
- Cause: Too many particles or per-pixel operations
- Solution: Reduce count, use noLoop() for static art

**Issue: Canvas not rendering**
- Cause: p5.js not loaded or syntax error
- Solution: Check CDN link, open browser console

**Issue: Downloaded image is black**
- Cause: saveCanvas called before render complete
- Solution: Call saveCanvas after all drawing completes
