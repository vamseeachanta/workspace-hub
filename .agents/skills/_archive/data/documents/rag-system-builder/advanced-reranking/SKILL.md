---
name: rag-system-builder-advanced-reranking
description: 'Sub-skill of rag-system-builder: Advanced: Reranking.'
version: 1.2.0
category: data
type: reference
scripts_exempt: true
---

# Advanced: Reranking

## Advanced: Reranking


Add a reranking step for improved precision:

```python
from sentence_transformers import CrossEncoder

class Reranker:
    def __init__(self, model_name='cross-encoder/ms-marco-MiniLM-L-6-v2'):
        self.model = CrossEncoder(model_name)

    def rerank(self, query, candidates, top_k=5):
        """Rerank candidates using cross-encoder."""
        pairs = [(query, c['text']) for c in candidates]
        scores = self.model.predict(pairs)

        for i, score in enumerate(scores):
            candidates[i]['rerank_score'] = float(score)

        reranked = sorted(candidates, key=lambda x: x['rerank_score'], reverse=True)
        return reranked[:top_k]

# Usage in RAG pipeline
def query_with_rerank(self, question, initial_k=20, final_k=5):
    # First pass: retrieve more candidates
    candidates = semantic_search(self.db_path, question, self.model, top_k=initial_k)

    # Second pass: rerank for precision
    reranked = self.reranker.rerank(question, candidates, top_k=final_k)

    return reranked
```
