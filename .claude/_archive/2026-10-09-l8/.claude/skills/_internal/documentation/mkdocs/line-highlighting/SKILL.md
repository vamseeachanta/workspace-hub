---
name: mkdocs-line-highlighting
description: 'Sub-skill of mkdocs: Line Highlighting.'
version: 1.0.0
category: _internal
type: reference
scripts_exempt: true
---

# Line Highlighting

## Line Highlighting


```python hl_lines="2 4"
def process_data(data):
    validated = validate(data)  # highlighted
    transformed = transform(validated)
    return save(transformed)  # highlighted
```
