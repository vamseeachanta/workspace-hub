---
name: mkdocs-flowchart
description: 'Sub-skill of mkdocs: Flowchart.'
version: 1.0.0
category: _internal
type: reference
scripts_exempt: true
---

# Flowchart

## Flowchart


```mermaid
flowchart TD
    A[Start] --> B{Is it valid?}
    B -->|Yes| C[Process Data]
    B -->|No| D[Show Error]
    C --> E[Save Results]
    D --> F[Log Error]
    E --> G[End]
    F --> G
```
