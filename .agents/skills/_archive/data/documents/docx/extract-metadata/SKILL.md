---
name: docx-extract-metadata
description: 'Sub-skill of docx: Extract Metadata.'
version: 1.1.0
category: data
type: reference
scripts_exempt: true
---

# Extract Metadata

## Extract Metadata


```python
from docx import Document

doc = Document("document.docx")
props = doc.core_properties

print(f"Title: {props.title}")
print(f"Author: {props.author}")
print(f"Created: {props.created}")
print(f"Modified: {props.modified}")
print(f"Last Modified By: {props.last_modified_by}")
```
