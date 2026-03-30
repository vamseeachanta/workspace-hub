---
name: clean-code-god-object-detection
description: 'Sub-skill of clean-code: God Object Detection.'
version: 2.1.0
category: workspace
type: reference
scripts_exempt: true
---

# God Object Detection

## God Object Detection


A "God Object" knows or does too much. Signs:

1. File >600 lines with >8 classes or >15 functions
2. Class that imports from 5+ different domain modules
3. Function >50 lines with >3 different concerns
4. File name that ends in `_utils.py`, `_helpers.py`, `_common.py` with >200 lines

```bash
# Files with many class definitions (God Object candidates)
grep -l "^class " src/**/*.py | xargs -I{} bash -c \
  'count=$(grep -c "^class " {}); [ $count -gt 3 ] && echo "$count classes: {}"' | sort -rn

# Files with many function definitions
grep -l "^def \|^    def " src/**/*.py | xargs -I{} bash -c \
  'count=$(grep -cE "^def |^    def " {}); [ $count -gt 15 ] && echo "$count funcs: {}"' | sort -rn
```

---
