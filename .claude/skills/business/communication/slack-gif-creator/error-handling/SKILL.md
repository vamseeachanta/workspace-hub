---
name: slack-gif-creator-error-handling
description: 'Sub-skill of slack-gif-creator: Error Handling.'
version: 2.0.0
category: business
type: reference
scripts_exempt: true
---

# Error Handling

## Error Handling


### Common Issues


**Issue: GIF not animating in Slack**
- Cause: Only one frame or corrupted file
- Solution: Verify multiple frames saved with `save_all=True`

**Issue: File too large for emoji**
- Cause: Too many frames or high resolution
- Solution: Reduce to 64x64, limit to 10-15 frames, use gifsicle

**Issue: Transparency not working**
- Cause: Missing transparency and disposal settings
- Solution: Add `transparency=0, disposal=2` to save()

**Issue: Colors look wrong**
- Cause: Palette reduction too aggressive
- Solution: Increase color count in gifsicle or use dithering
