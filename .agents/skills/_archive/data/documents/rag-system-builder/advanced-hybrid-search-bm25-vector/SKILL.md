---
name: rag-system-builder-advanced-hybrid-search-bm25-vector
description: 'Sub-skill of rag-system-builder: Advanced: Hybrid Search (BM25 + Vector).'
version: 1.2.0
category: data
type: reference
scripts_exempt: true
---

# Advanced: Hybrid Search (BM25 + Vector)

## Advanced: Hybrid Search (BM25 + Vector)


Combine keyword and semantic search for better results:

```python
import sqlite3
from rank_bm25 import BM25Okapi
import numpy as np

class HybridSearch:
    def __init__(self, db_path, embedding_model):
        self.db_path = db_path
        self.model = embedding_model
        self._build_bm25_index()

    def _build_bm25_index(self):
        """Build BM25 index from chunks."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT id, chunk_text FROM chunks')

        self.chunk_ids = []
        tokenized_corpus = []
        for chunk_id, text in cursor.fetchall():
            self.chunk_ids.append(chunk_id)
            tokenized_corpus.append(text.lower().split())


*See sub-skills for full details.*
