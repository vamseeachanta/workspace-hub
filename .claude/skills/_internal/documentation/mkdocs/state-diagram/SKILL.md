---
name: mkdocs-state-diagram
description: 'Sub-skill of mkdocs: State Diagram.'
version: 1.0.0
category: _internal
type: reference
scripts_exempt: true
---

# State Diagram

## State Diagram


```mermaid
stateDiagram-v2
    [*] --> Draft
    Draft --> Review: Submit
    Review --> Approved: Accept
    Review --> Draft: Request Changes
    Approved --> Published: Publish
    Published --> [*]
```
