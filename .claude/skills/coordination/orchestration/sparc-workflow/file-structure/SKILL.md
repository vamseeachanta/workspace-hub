---
name: sparc-workflow-file-structure
description: 'Sub-skill of sparc-workflow: File Structure.'
version: 1.1.0
category: coordination
type: reference
scripts_exempt: true
---

# File Structure

## File Structure


\`\`\`
src/
└── feature_name/
    ├── __init__.py
    ├── processor.py      # Main processing logic
    ├── validator.py      # Input validation
    ├── transformer.py    # Data transformation
    └── models.py         # Data models
\`\`\`
```
