---
name: semantic-search-setup-1-cpu-vs-gpu
description: 'Sub-skill of semantic-search-setup: 1. CPU vs GPU (+3).'
version: 1.1.0
category: data
type: reference
scripts_exempt: true
---

# 1. CPU vs GPU (+3)

## 1. CPU vs GPU


```python
# Force CPU (more stable, sufficient for most cases)
os.environ['CUDA_VISIBLE_DEVICES'] = ''

# Use GPU if available
# Remove the above line and ensure CUDA is installed
```

## 2. Batch Processing


```python
# Larger batches = faster but more memory
batch_size = 100  # Default
batch_size = 500  # If you have 16GB+ RAM
batch_size = 50   # If memory constrained
```

## 3. Progress Tracking


```python
from tqdm import tqdm

for i in tqdm(range(0, total, batch_size)):
    # Process batch
    pass
```

## 4. Incremental Updates


```python
# Only embed new chunks
cursor.execute('''
    SELECT c.id, c.chunk_text
    FROM chunks c
    LEFT JOIN embeddings e ON c.id = e.chunk_id
    WHERE e.id IS NULL
''')
```
