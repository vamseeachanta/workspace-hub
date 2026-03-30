---
name: instrument-data-allotrope-pre-parsing-checklist
description: 'Sub-skill of instrument-data-allotrope: Pre-Parsing Checklist.'
version: 1.0.0
category: science
type: reference
scripts_exempt: true
---

# Pre-Parsing Checklist

## Pre-Parsing Checklist


Before writing a custom parser, ALWAYS:

1. **Check if allotropy supports it** - Use native parser if available
2. **Find a reference ASM file** - Check `references/examples/` or ask user
3. **Review instrument-specific guide** - Check `references/instrument_guides/`
4. **Validate against reference** - Run `validate_asm.py --reference <file>`
