---
name: mkdocs-entity-relationship
description: 'Sub-skill of mkdocs: Entity Relationship.'
version: 1.0.0
category: _internal
type: reference
scripts_exempt: true
---

# Entity Relationship

## Entity Relationship


```mermaid
erDiagram
    USER ||--o{ POST : creates
    USER ||--o{ COMMENT : writes
    POST ||--|{ COMMENT : contains
    POST }|..|{ TAG : has
```
