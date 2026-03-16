---
name: orcaflex-file-conversion-adding-conversion-to-universal-cli
description: 'Sub-skill of orcaflex-file-conversion: Adding Conversion to Universal
  CLI.'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# Adding Conversion to Universal CLI

## Adding Conversion to Universal CLI


The converter can be integrated into the universal CLI for seamless workflow:

```bash
# Future integration (planned)
orcaflex-universal convert --input models/ --output models_yml/ --format yml
orcaflex-universal convert --input models_yml/ --output models/ --format dat
```
