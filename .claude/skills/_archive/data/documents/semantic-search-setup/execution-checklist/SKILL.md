---
name: semantic-search-setup-execution-checklist
description: 'Sub-skill of semantic-search-setup: Execution Checklist.'
version: 1.1.0
category: data
type: reference
scripts_exempt: true
---

# Execution Checklist

## Execution Checklist


- [ ] Install sentence-transformers and numpy
- [ ] Choose appropriate embedding model for use case
- [ ] Create embeddings table in database
- [ ] Generate embeddings for all text chunks
- [ ] Test semantic search with sample queries
- [ ] Compare results with keyword search (FTS5)
- [ ] Optimize batch size for available memory
- [ ] Set up background service for continuous updates
