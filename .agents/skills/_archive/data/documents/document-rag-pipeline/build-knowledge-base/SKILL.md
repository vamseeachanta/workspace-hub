---
name: document-rag-pipeline-build-knowledge-base
description: 'Sub-skill of document-rag-pipeline: Build Knowledge Base (+2).'
version: 1.1.0
category: data
type: reference
scripts_exempt: true
---

# Build Knowledge Base (+2)

## Build Knowledge Base


```bash
# Full pipeline with OCR and embeddings
python build_knowledge_base.py /path/to/documents --embed

# Skip OCR (faster, text PDFs only)
python build_knowledge_base.py /path/to/documents --no-ocr --embed

# Just build inventory (no extraction)
python build_knowledge_base.py /path/to/documents
```


## Search Documents


```bash
# Semantic search
python build_knowledge_base.py /path/to/documents --search "subsea wellhead design"

# More results
python build_knowledge_base.py /path/to/documents --search "fatigue analysis" --top-k 20
```


## Quick Search Script


```bash
#!/bin/bash
# search_docs.sh - Quick semantic search

DB_PATH="${1:-/path/to/_inventory.db}"
QUERY="$2"

CUDA_VISIBLE_DEVICES="" python3 -c "
import sqlite3, pickle, numpy as np
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')
query_emb = model.encode('$QUERY', normalize_embeddings=True)

conn = sqlite3.connect('$DB_PATH')
cursor = conn.cursor()
cursor.execute('''
    SELECT tc.chunk_text, tc.embedding, d.filename
    FROM text_chunks tc
    JOIN documents d ON tc.document_id = d.id
    WHERE tc.embedding IS NOT NULL
    ORDER BY RANDOM() LIMIT 50000
''')

results = []
for text, emb_blob, filename in cursor.fetchall():
    emb = pickle.loads(emb_blob)
    sim = float(np.dot(query_emb, emb))
    results.append((sim, filename, text[:200]))

for score, fname, text in sorted(results, reverse=True)[:10]:
    print(f'[{score:.3f}] {fname}')
    print(f'  {text}...\n')
"
```
