---
name: office-docs-document-generation-pipeline
description: 'Sub-skill of office-docs: Document Generation Pipeline (+2).'
version: 1.0.0
category: data
type: reference
scripts_exempt: true
---

# Document Generation Pipeline (+2)

## Document Generation Pipeline


```
Data Source --> Template Selection --> Rendering --> Post-processing --> Output
     |                 |                   |              |               |
     +-- Database     +-- By type         +-- Variables +-- Convert     +-- Save
     +-- API          +-- By language     +-- Loops     +-- Combine     +-- Email
     +-- Form         +-- By recipient    +-- Images    +-- Sign        +-- Archive
```

## Batch Processing Pattern


```
Input Files --> Validation --> Processing --> Quality Check --> Output
     |              |              |               |              |
     +-- Queue     +-- Format    +-- Transform   +-- Verify     +-- Organize
     +-- Watch     +-- Content   +-- Extract     +-- Log        +-- Notify
```

## Template Management


```
Template Repo --> Version Control --> Environment --> Runtime
      |               |                  |              |
      +-- Design     +-- Review         +-- Dev/Prod   +-- Hot reload
      +-- Test       +-- Approve        +-- Variables  +-- Fallbacks
```
