---
name: google-earth-engine-4-failure-diagnosis
description: 'Sub-skill of google-earth-engine: 4. FAILURE DIAGNOSIS.'
version: 1.0.0
category: engineering/gis
type: reference
scripts_exempt: true
---

# 4. FAILURE DIAGNOSIS

## 4. FAILURE DIAGNOSIS


| Error | Cause | Fix |
|-------|-------|-----|
| `EEException: Not authenticated` | No valid token | Re-run `ee.Authenticate()` or check service account |
| `EEException: Quota exceeded` | Computation too large | Reduce scale; use `ee.batch.Export` instead of `getInfo()` |
| `getInfo() timeout` | Request too large | Export to Drive; never call `getInfo()` on full images |
| `Dataset not found` | Wrong dataset ID | Check [developers.google.com/earth-engine/datasets](https://developers.google.com/earth-engine/datasets) |
| `Export task FAILED` | Region/scale mismatch; maxPixels exceeded | Increase `maxPixels`; check `region` is valid geometry |
| `Image.select: Band ... not found` | Wrong band name for dataset | Print `image.bandNames().getInfo()` to confirm |
| `No images in collection` | Date range or cloud filter too strict | Widen date range; relax cloud percentage filter |
| `Memory limit exceeded` | Too many pixels in reducer | Increase `scale` parameter; use tiled export |

---
