---
name: semantic-search-setup-step-1-install-dependencies
description: 'Sub-skill of semantic-search-setup: Step 1: Install Dependencies (+5).'
version: 1.1.0
category: data
type: reference
scripts_exempt: true
---

# Step 1: Install Dependencies (+5)

## Step 1: Install Dependencies


```bash
pip install sentence-transformers numpy
# or
uv pip install sentence-transformers numpy
```

## Step 2: Database Schema


```python
import sqlite3

def create_embeddings_table(db_path):
    conn = sqlite3.connect(db_path, timeout=30)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS embeddings (
            id INTEGER PRIMARY KEY,

*See sub-skills for full details.*

## Step 3: Embedding Generator


```python
from sentence_transformers import SentenceTransformer
import numpy as np
import os

class EmbeddingGenerator:
    def __init__(self, model_name='all-MiniLM-L6-v2'):
        # Force CPU for stability
        os.environ['CUDA_VISIBLE_DEVICES'] = ''


*See sub-skills for full details.*

## Step 4: Batch Processing


```python
def generate_all_embeddings(db_path, batch_size=100):
    """Generate embeddings for all chunks."""
    conn = sqlite3.connect(db_path, timeout=30)
    cursor = conn.cursor()

    generator = EmbeddingGenerator()

    # Get chunks without embeddings
    cursor.execute('''

*See sub-skills for full details.*

## Step 5: Semantic Search


```python
def semantic_search(db_path, query, top_k=10):
    """Find most similar chunks to query."""
    conn = sqlite3.connect(db_path, timeout=30)
    cursor = conn.cursor()

    generator = EmbeddingGenerator()
    query_embedding = generator.embed_text(query)

    # Get all embeddings

*See sub-skills for full details.*

## Step 6: Background Service


```bash
#!/bin/bash
# embed-service.sh - Background embedding service

DB_PATH="${1:-./knowledge.db}"
BATCH_SIZE="${2:-100}"
LOG_FILE="/tmp/embed.log"
PID_FILE="/tmp/embed.pid"

start() {

*See sub-skills for full details.*
