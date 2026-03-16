---
name: document-rag-pipeline-metrics
description: 'Sub-skill of document-rag-pipeline: Metrics.'
version: 1.1.0
category: data
type: reference
scripts_exempt: true
---

# Metrics

## Metrics


| Metric | Typical Value |
|--------|---------------|
| Text extraction | ~50 pages/second |
| OCR processing | ~2-5 pages/minute |
| Embedding generation | ~100 chunks/second (CPU) |
| Search latency | <2 seconds (50K chunks) |
| Memory usage | ~2GB for embeddings |
