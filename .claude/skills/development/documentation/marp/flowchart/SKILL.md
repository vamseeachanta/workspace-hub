---
name: marp-flowchart
description: 'Sub-skill of marp: Flowchart.'
version: 1.0.0
category: development
type: reference
scripts_exempt: true
---

# Flowchart

## Flowchart


```mermaid
flowchart TD
    A[Start] --> B{Decision}
    B -->|Yes| C[Process A]
    B -->|No| D[Process B]
    C --> E[End]
    D --> E
```

---
