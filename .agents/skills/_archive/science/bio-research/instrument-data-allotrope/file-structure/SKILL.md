---
name: instrument-data-allotrope-file-structure
description: 'Sub-skill of instrument-data-allotrope: File Structure.'
version: 1.0.0
category: science
type: reference
scripts_exempt: true
---

# File Structure

## File Structure


```
instrument-data-to-allotrope/
├── SKILL.md                          # This file
├── scripts/
│   ├── convert_to_asm.py            # Main conversion script
│   ├── flatten_asm.py               # ASM -> 2D CSV conversion
│   ├── export_parser.py             # Generate standalone parser code
│   └── validate_asm.py              # Validate ASM output quality
└── references/
    ├── supported_instruments.md     # Full instrument list with Vendor enums
    ├── asm_schema_overview.md       # ASM structure reference
    ├── field_classification_guide.md # Where to put different field types
    └── flattening_guide.md          # How flattening works
```
