---
name: ai-prompting-rag-architecture
description: 'Sub-skill of ai-prompting: RAG Architecture (+2).'
version: 1.0.0
category: ai
type: reference
scripts_exempt: true
---

# RAG Architecture (+2)

## RAG Architecture


```
User Query --> Embedding --> Vector Search --> Context Assembly --> LLM --> Response
     |                            |                   |               |
     +-- Query expansion         +-- Reranking       +-- Chunking    +-- Citations
     +-- Intent detection        +-- Filtering       +-- Templates   +-- Validation
```

## Prompt Optimization Pipeline


```
Initial Prompt --> Generate Outputs --> Evaluate --> Optimize --> Deploy
      |                  |                 |            |            |
      +-- Template      +-- Test cases   +-- Metrics  +-- Search   +-- Monitor
      +-- Variables     +-- Edge cases   +-- Human    +-- Iterate  +-- A/B test
```

## Agent Architecture


```
User Request --> Plan --> Tool Selection --> Execution --> Reflection --> Response
      |           |             |                |              |             |
      +-- Parse  +-- Decompose +-- Available    +-- Retry     +-- Verify    +-- Format
      +-- Intent +-- Prioritize+-- Constraints  +-- Timeout   +-- Correct   +-- Cite
```
