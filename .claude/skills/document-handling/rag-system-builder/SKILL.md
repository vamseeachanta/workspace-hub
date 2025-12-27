---
name: rag-system-builder
description: Build Retrieval-Augmented Generation (RAG) Q&A systems with Claude or OpenAI. Use for creating AI assistants that answer questions from document collections, technical libraries, or knowledge bases.
---

# RAG System Builder Skill

## Overview

This skill creates complete RAG (Retrieval-Augmented Generation) systems that combine semantic search with LLM-powered Q&A. Users can ask natural language questions and receive accurate answers grounded in your document collection.

## When to Use

- Building AI assistants for technical documentation
- Creating Q&A systems for standards libraries
- Developing chatbots with domain expertise
- Enabling natural language queries over knowledge bases
- Adding AI-powered search to existing document systems

## Architecture

```
User Question
      │
      ▼
┌─────────────────┐
│ 1. Embed Query  │  sentence-transformers
└────────┬────────┘
         ▼
┌─────────────────┐
│ 2. Vector Search│  Cosine similarity
└────────┬────────┘
         ▼
┌─────────────────┐
│ 3. Retrieve Top │  Top-K relevant chunks
└────────┬────────┘
         ▼
┌─────────────────┐
│ 4. Build Prompt │  Context + Question
└────────┬────────┘
         ▼
┌─────────────────┐
│ 5. LLM Answer   │  Claude/OpenAI
└─────────────────┘
```

## Prerequisites

- Knowledge base with extracted text (see `knowledge-base-builder`)
- Vector embeddings for semantic search (see `semantic-search-setup`)
- API key: `ANTHROPIC_API_KEY` or `OPENAI_API_KEY`

## Implementation

### Step 1: Vector Embeddings Table

```python
import sqlite3
import numpy as np

def setup_embeddings_table(db_path):
    conn = sqlite3.connect(db_path, timeout=30)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS embeddings (
            id INTEGER PRIMARY KEY,
            chunk_id INTEGER UNIQUE,
            embedding BLOB,
            model_name TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (chunk_id) REFERENCES chunks(id)
        )
    ''')

    conn.commit()
    return conn
```

### Step 2: Generate Embeddings

```python
from sentence_transformers import SentenceTransformer
import numpy as np

class EmbeddingGenerator:
    def __init__(self, model_name='all-MiniLM-L6-v2'):
        self.model = SentenceTransformer(model_name)
        self.dimension = 384  # all-MiniLM-L6-v2

    def embed_text(self, text):
        """Generate embedding for text."""
        embedding = self.model.encode(text, normalize_embeddings=True)
        return embedding.astype(np.float32)

    def embed_batch(self, texts, batch_size=100):
        """Generate embeddings for multiple texts."""
        embeddings = self.model.encode(
            texts,
            batch_size=batch_size,
            normalize_embeddings=True,
            show_progress_bar=True
        )
        return embeddings.astype(np.float32)
```

### Step 3: Semantic Search

```python
def semantic_search(db_path, query, model, top_k=5):
    """Find most similar chunks to query."""
    conn = sqlite3.connect(db_path, timeout=30)
    cursor = conn.cursor()

    # Embed query
    query_embedding = model.embed_text(query)

    # Get all embeddings
    cursor.execute('''
        SELECT e.chunk_id, e.embedding, c.chunk_text, d.filename
        FROM embeddings e
        JOIN chunks c ON e.chunk_id = c.id
        JOIN documents d ON c.doc_id = d.id
    ''')

    results = []
    for chunk_id, emb_blob, text, filename in cursor.fetchall():
        embedding = np.frombuffer(emb_blob, dtype=np.float32)
        score = np.dot(query_embedding, embedding)  # Cosine similarity
        results.append({
            'chunk_id': chunk_id,
            'score': float(score),
            'text': text,
            'filename': filename
        })

    # Sort by similarity
    results.sort(key=lambda x: x['score'], reverse=True)
    return results[:top_k]
```

### Step 4: RAG Query Engine

```python
import anthropic
import openai

class RAGQueryEngine:
    def __init__(self, db_path, embedding_model):
        self.db_path = db_path
        self.model = embedding_model

    def query(self, question, top_k=5, provider='anthropic'):
        """Answer question using RAG."""

        # 1. Retrieve relevant context
        results = semantic_search(self.db_path, question, self.model, top_k)

        # 2. Build context string
        context = "\n\n---\n\n".join([
            f"Source: {r['filename']}\n{r['text']}"
            for r in results
        ])

        # 3. Build prompt
        prompt = f"""Based on the following technical documents, answer the question.
If the answer is not in the documents, say so.

DOCUMENTS:
{context}

QUESTION: {question}

ANSWER:"""

        # 4. Get LLM response
        if provider == 'anthropic':
            return self._query_claude(prompt), results
        else:
            return self._query_openai(prompt), results

    def _query_claude(self, prompt):
        client = anthropic.Anthropic()
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text

    def _query_openai(self, prompt):
        client = openai.OpenAI()
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
```

### Step 5: CLI Interface

```python
#!/usr/bin/env python3
"""RAG Query CLI - Ask questions about your documents."""

import argparse
import os

def main():
    parser = argparse.ArgumentParser(description='RAG Q&A System')
    parser.add_argument('question', nargs='?', help='Question to ask')
    parser.add_argument('-i', '--interactive', action='store_true')
    parser.add_argument('-k', '--top-k', type=int, default=5)
    parser.add_argument('--provider', choices=['anthropic', 'openai'], default='anthropic')

    args = parser.parse_args()

    engine = RAGQueryEngine(DB_PATH, EmbeddingGenerator())

    if args.interactive:
        print("RAG Q&A System (type 'quit' to exit)")
        while True:
            question = input("\nQuestion: ").strip()
            if question.lower() == 'quit':
                break
            answer, sources = engine.query(question, args.top_k, args.provider)
            print(f"\nAnswer: {answer}")
            print(f"\nSources: {[s['filename'] for s in sources]}")
    else:
        answer, sources = engine.query(args.question, args.top_k, args.provider)
        print(f"Answer: {answer}")
        print(f"\nSources:")
        for s in sources:
            print(f"  - {s['filename']} (score: {s['score']:.3f})")

if __name__ == '__main__':
    main()
```

## Prompt Engineering Tips

### System Prompt Template

```python
SYSTEM_PROMPT = """You are a technical expert assistant. Your role is to:
1. Answer questions based ONLY on the provided documents
2. Cite specific sources when possible
3. Acknowledge when information is not available
4. Be precise with technical terminology
5. Provide practical, actionable answers

If asked about topics not covered in the documents, say:
"I don't have information about that in the available documents."
"""
```

### Multi-Turn Conversations

```python
def query_with_history(self, question, history=[]):
    """Support follow-up questions."""
    context = self.get_relevant_context(question)

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    # Add conversation history
    for h in history[-4:]:  # Last 4 turns
        messages.append({"role": "user", "content": h['question']})
        messages.append({"role": "assistant", "content": h['answer']})

    # Add current question with context
    messages.append({
        "role": "user",
        "content": f"Context:\n{context}\n\nQuestion: {question}"
    })

    return self.llm.query(messages)
```

## Performance Optimization

### 1. Cache Embeddings
```python
# Load all embeddings into memory at startup
self.embedding_cache = self._load_all_embeddings()
```

### 2. Use FAISS for Large Collections
```python
import faiss

# Build FAISS index for fast similarity search
index = faiss.IndexFlatIP(dimension)  # Inner product for cosine sim
index.add(embeddings)
```

### 3. Batch Queries
```python
# Process multiple questions efficiently
questions = ["Q1", "Q2", "Q3"]
query_embeddings = model.embed_batch(questions)
```

## Best Practices

1. **Chunk size matters** - 500-1500 chars optimal for context
2. **Retrieve enough context** - top_k=5-10 for comprehensive answers
3. **Include source attribution** - Always show which documents were used
4. **Handle edge cases** - Empty results, API errors, timeouts
5. **Monitor token usage** - Track costs and optimize prompts
6. **Use SQLite timeout** - `timeout=30` for concurrent access

## Example Usage

```bash
# Single question
./rag "What are the fatigue design requirements for risers?"

# Interactive mode
./rag -i

# With OpenAI
./rag --provider openai "Explain API 2RD requirements"
```

## Related Skills

- `knowledge-base-builder` - Build the document database first
- `semantic-search-setup` - Generate vector embeddings
- `pdf-text-extractor` - Extract text from PDFs
