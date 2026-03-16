---
name: rag-system-builder
description: Build Retrieval-Augmented Generation (RAG) Q&A systems with Claude or
  OpenAI. Use for creating AI assistants that answer questions from document collections,
  technical libraries, or knowledge bases.
version: 1.2.0
last_updated: 2026-01-02
category: data
related_skills:
- knowledge-base-builder
- semantic-search-setup
- pdf-text-extractor
- document-rag-pipeline
capabilities: []
requires: []
see_also:
- rag-system-builder-architecture
- rag-system-builder-step-1-vector-embeddings-table
- rag-system-builder-system-prompt-template
- rag-system-builder-1-cache-embeddings
- rag-system-builder-example-usage
- rag-system-builder-advanced-hybrid-search-bm25-vector
- rag-system-builder-advanced-reranking
- rag-system-builder-streaming-responses
tags: []
---

# Rag System Builder

## Overview

This skill creates complete RAG (Retrieval-Augmented Generation) systems that combine semantic search with LLM-powered Q&A. Users can ask natural language questions and receive accurate answers grounded in your document collection.

## Quick Start

```python
from sentence_transformers import SentenceTransformer
import anthropic

# Setup
model = SentenceTransformer('all-MiniLM-L6-v2')
client = anthropic.Anthropic()

# Retrieve context (simplified)
query = "What are the safety requirements?"
query_embedding = model.encode(query, normalize_embeddings=True)
# ... search for similar chunks ...

# Generate answer
response = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=1024,
    messages=[{"role": "user", "content": f"Context: {context}\n\nQuestion: {query}"}]
)
print(response.content[0].text)
```

## When to Use

- Building AI assistants for technical documentation
- Creating Q&A systems for standards libraries
- Developing chatbots with domain expertise
- Enabling natural language queries over knowledge bases
- Adding AI-powered search to existing document systems

## Prerequisites

- Knowledge base with extracted text (see `knowledge-base-builder`)
- Vector embeddings for semantic search (see `semantic-search-setup`)
- API key: `ANTHROPIC_API_KEY` or `OPENAI_API_KEY`

## Related Skills

- `knowledge-base-builder` - Build the document database first
- `semantic-search-setup` - Generate vector embeddings
- `pdf-text-extractor` - Extract text from PDFs
- `document-rag-pipeline` - Complete end-to-end pipeline

## Version History

- **1.2.0** (2026-01-02): Added Quick Start, Execution Checklist, Error Handling, Metrics sections; updated frontmatter with version, category, related_skills
- **1.1.0** (2025-12-30): Added hybrid search (BM25+vector), reranking, streaming responses
- **1.0.0** (2025-10-15): Initial release with basic RAG implementation

## Sub-Skills

- [Best Practices](best-practices/SKILL.md)

## Sub-Skills

- [Execution Checklist](execution-checklist/SKILL.md)
- [Error Handling](error-handling/SKILL.md)
- [Metrics](metrics/SKILL.md)
- [Dependencies](dependencies/SKILL.md)

## Sub-Skills

- [Architecture](architecture/SKILL.md)
- [Step 1: Vector Embeddings Table (+4)](step-1-vector-embeddings-table/SKILL.md)
- [System Prompt Template (+1)](system-prompt-template/SKILL.md)
- [1. Cache Embeddings (+2)](1-cache-embeddings/SKILL.md)
- [Example Usage](example-usage/SKILL.md)
- [Advanced: Hybrid Search (BM25 + Vector)](advanced-hybrid-search-bm25-vector/SKILL.md)
- [Advanced: Reranking](advanced-reranking/SKILL.md)
- [Streaming Responses](streaming-responses/SKILL.md)
