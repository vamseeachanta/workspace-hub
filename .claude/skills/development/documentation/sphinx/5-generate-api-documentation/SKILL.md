---
name: sphinx-5-generate-api-documentation
description: 'Sub-skill of sphinx: 5. Generate API Documentation (+1).'
version: 1.0.0
category: development
type: reference
scripts_exempt: true
---

# 5. Generate API Documentation (+1)

## 5. Generate API Documentation


```bash
# Auto-generate API documentation stubs
sphinx-apidoc -o docs/source/api src/mypackage -f -e -M

# Options:
# -o: Output directory
# -f: Force overwrite
# -e: Separate pages for each module
# -M: Module-first ordering
# -d 2: TOC depth

# Build HTML documentation
sphinx-build -b html docs/source docs/build/html

# Build with verbose output
sphinx-build -b html docs/source docs/build/html -v

# Clean and rebuild
rm -rf docs/build && sphinx-build -b html docs/source docs/build/html
```


## 6. MyST Markdown Support


```python
# conf.py - Enable MyST
extensions = [
    'myst_parser',
]

# MyST configuration
myst_enable_extensions = [
    'amsmath',
    'colon_fence',
    'deflist',
    'dollarmath',
    'fieldlist',
    'html_admonition',
    'html_image',
    'replacements',
    'smartquotes',
    'strikethrough',
    'substitution',
    'tasklist',
]

myst_heading_anchors = 3
myst_footnote_transition = True
```

```markdown
<!-- docs/source/guide/overview.md -->

# Overview

This guide provides an overview of MyProject.
