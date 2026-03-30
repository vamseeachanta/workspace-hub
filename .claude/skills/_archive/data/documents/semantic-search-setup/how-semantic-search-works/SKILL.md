---
name: semantic-search-setup-how-semantic-search-works
description: 'Sub-skill of semantic-search-setup: How Semantic Search Works.'
version: 1.1.0
category: data
type: reference
scripts_exempt: true
---

# How Semantic Search Works

## How Semantic Search Works


```
Text Chunk                    Query
    |                           |
    v                           v
+---------+               +---------+
| Embed   |               | Embed   |
| Model   |               | Model   |
+----+----+               +----+----+
     |                         |
     v                         v
[0.12, -0.34, ...]       [0.15, -0.31, ...]
     |                         |
     +------------+------------+
                  |
                  v
           Cosine Similarity
                  |
                  v
             0.847 (similar!)
```
