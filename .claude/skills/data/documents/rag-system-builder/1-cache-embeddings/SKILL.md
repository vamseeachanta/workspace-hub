---
name: rag-system-builder-1-cache-embeddings
description: 'Sub-skill of rag-system-builder: 1. Cache Embeddings (+2).'
version: 1.2.0
category: data
type: reference
scripts_exempt: true
---

# 1. Cache Embeddings (+2)

## 1. Cache Embeddings


```python
# Load all embeddings into memory at startup
self.embedding_cache = self._load_all_embeddings()
```

## 2. Use FAISS for Large Collections


```python
import faiss

# Build FAISS index for fast similarity search
index = faiss.IndexFlatIP(dimension)  # Inner product for cosine sim
index.add(embeddings)
```

## 3. Batch Queries


```python
# Process multiple questions efficiently
questions = ["Q1", "Q2", "Q3"]
query_embeddings = model.embed_batch(questions)
```
