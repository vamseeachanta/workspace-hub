---
name: semantic-search-setup
description: Setup vector embeddings and semantic search for document collections.
  Use for AI-powered similarity search, finding related documents, and preparing knowledge
  bases for RAG systems.
version: 1.1.0
last_updated: 2026-01-02
category: data
related_skills:
- knowledge-base-builder
- rag-system-builder
- pdf-text-extractor
capabilities: []
requires: []
see_also:
- semantic-search-setup-how-semantic-search-works
- semantic-search-setup-model-selection
- semantic-search-setup-step-1-install-dependencies
- semantic-search-setup-1-cpu-vs-gpu
- semantic-search-setup-status-monitoring
- semantic-search-setup-example-usage
tags: []
---

# Semantic Search Setup

## Overview

This skill sets up vector embedding infrastructure for semantic search. Unlike keyword search (FTS5), semantic search finds conceptually similar content even without exact word matches.

## Quick Start

```python
from sentence_transformers import SentenceTransformer
import numpy as np

model = SentenceTransformer('all-MiniLM-L6-v2')

# Generate embeddings
texts = ["How to fix a bug", "Debugging software issues"]
embeddings = model.encode(texts, normalize_embeddings=True)

# Compute similarity
similarity = np.dot(embeddings[0], embeddings[1])
print(f"Similarity: {similarity:.3f}")  # ~0.85
```

## When to Use

- Adding AI-powered search to document collections
- Finding conceptually related documents
- Preparing knowledge bases for RAG Q&A systems
- Building recommendation systems
- Enabling "more like this" functionality

## Related Skills

- `knowledge-base-builder` - Build the document database first
- `rag-system-builder` - Add AI Q&A on top of semantic search
- `pdf-text-extractor` - Extract text from PDFs

## Version History

- **1.1.0** (2026-01-02): Added Quick Start, Execution Checklist, Error Handling, Metrics sections; updated frontmatter with version, category, related_skills
- **1.0.0** (2024-10-15): Initial release with sentence-transformers, cosine similarity search, batch processing

## Sub-Skills

- [Best Practices](best-practices/SKILL.md)

## Sub-Skills

- [Execution Checklist](execution-checklist/SKILL.md)
- [Error Handling](error-handling/SKILL.md)
- [Metrics](metrics/SKILL.md)
- [Dependencies](dependencies/SKILL.md)

## Sub-Skills

- [How Semantic Search Works](how-semantic-search-works/SKILL.md)
- [Model Selection](model-selection/SKILL.md)
- [Step 1: Install Dependencies (+5)](step-1-install-dependencies/SKILL.md)
- [1. CPU vs GPU (+3)](1-cpu-vs-gpu/SKILL.md)
- [Status Monitoring](status-monitoring/SKILL.md)
- [Example Usage](example-usage/SKILL.md)
