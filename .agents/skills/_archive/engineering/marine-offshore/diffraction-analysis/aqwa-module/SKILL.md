---
name: diffraction-analysis-aqwa-module
description: 'Sub-skill of diffraction-analysis: AQWA Module (+2).'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# AQWA Module (+2)

## AQWA Module


```bash
# (Uses existing AQWA CLI if available)
```

## BEMRosetta Module


```bash
bemrosetta convert analysis.LIS -o ./output
bemrosetta convert analysis.LIS --qtf analysis.QTF -o ./output
bemrosetta info analysis.LIS
bemrosetta validate analysis.LIS --strict --causality
bemrosetta convert-mesh hull.gdf -o hull.stl
bemrosetta status
```

## Diffraction Module


```bash
# Batch processing
python -m digitalmodel.diffraction.batch_processor config.yml
```
