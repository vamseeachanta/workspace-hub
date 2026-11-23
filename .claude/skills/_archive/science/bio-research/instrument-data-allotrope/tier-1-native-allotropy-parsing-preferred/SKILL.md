---
name: allotrope-tier1-native-parsing-preferred
description: 'Sub-skill of instrument-data-allotrope: Tier 1: Native allotropy parsing
  (PREFERRED) (+2).'
version: 1.0.0
category: science
type: reference
scripts_exempt: true
---

# Tier 1: Native allotropy parsing (PREFERRED) (+2)

## Tier 1: Native allotropy parsing (PREFERRED)

**Always try allotropy first.** Check available vendors directly:

```python
from allotropy.parser_factory import Vendor

# List all supported vendors
for v in Vendor:
    print(f"{v.name}")

# Common vendors:
# AGILENT_TAPESTATION_ANALYSIS  (for TapeStation XML)
# BECKMAN_VI_CELL_BLU
# THERMO_FISHER_NANODROP_EIGHT
# MOLDEV_SOFTMAX_PRO
# APPBIO_QUANTSTUDIO
# ... many more
```

**When the user provides a file, check if allotropy supports it before falling back to manual parsing.** The `scripts/convert_to_asm.py` auto-detection only covers a subset of allotropy vendors.


## Tier 2: Flexible fallback parsing

**Only use if allotropy doesn't support the instrument.** This fallback:
- Does NOT generate `calculated-data-aggregate-document`
- Does NOT include full traceability
- Produces simplified ASM structure

Use flexible parser with:
- Column name fuzzy matching
- Unit extraction from headers
- Metadata extraction from file structure


## Tier 3: PDF extraction

For PDF-only files, extract tables using pdfplumber, then apply Tier 2 parsing.
