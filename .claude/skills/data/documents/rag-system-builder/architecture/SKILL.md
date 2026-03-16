---
name: rag-system-builder-architecture
description: 'Sub-skill of rag-system-builder: Architecture.'
version: 1.2.0
category: data
type: reference
scripts_exempt: true
---

# Architecture

## Architecture


```
User Question
      |
      v
+------------------+
| 1. Embed Query   |  sentence-transformers
+--------+---------+
         v
+------------------+
| 2. Vector Search |  Cosine similarity
+--------+---------+
         v
+------------------+
| 3. Retrieve Top  |  Top-K relevant chunks
+--------+---------+
         v
+------------------+
| 4. Build Prompt  |  Context + Question
+--------+---------+
         v
+------------------+
| 5. LLM Answer    |  Claude/OpenAI
+------------------+
```
