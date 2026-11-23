---
name: pptx-unpack-presentation
description: 'Sub-skill of pptx: Unpack Presentation (+2).'
version: 1.1.0
category: data
type: reference
scripts_exempt: true
---

# Unpack Presentation (+2)

## Unpack Presentation


```bash
unzip presentation.pptx -d presentation_extracted/
```

## Edit XML


Navigate to `ppt/slides/` and edit `slide1.xml`, etc.

## Repack


```bash
cd presentation_extracted
zip -r ../modified.pptx .
```
