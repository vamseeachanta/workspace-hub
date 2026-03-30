---
name: rag-system-builder-step-1-vector-embeddings-table
description: 'Sub-skill of rag-system-builder: Step 1: Vector Embeddings Table (+4).'
version: 1.2.0
category: data
type: reference
scripts_exempt: true
---

# Step 1: Vector Embeddings Table (+4)

## Step 1: Vector Embeddings Table


```python
import sqlite3
import numpy as np

def setup_embeddings_table(db_path):
    conn = sqlite3.connect(db_path, timeout=30)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS embeddings (

*See sub-skills for full details.*

## Step 2: Generate Embeddings


```python
from sentence_transformers import SentenceTransformer
import numpy as np

class EmbeddingGenerator:
    def __init__(self, model_name='all-MiniLM-L6-v2'):
        self.model = SentenceTransformer(model_name)
        self.dimension = 384  # all-MiniLM-L6-v2

    def embed_text(self, text):

*See sub-skills for full details.*

## Step 3: Semantic Search


```python
def semantic_search(db_path, query, model, top_k=5):
    """Find most similar chunks to query."""
    conn = sqlite3.connect(db_path, timeout=30)
    cursor = conn.cursor()

    # Embed query
    query_embedding = model.embed_text(query)

    # Get all embeddings

*See sub-skills for full details.*

## Step 4: RAG Query Engine


```python
import anthropic
import openai

class RAGQueryEngine:
    def __init__(self, db_path, embedding_model):
        self.db_path = db_path
        self.model = embedding_model

    def query(self, question, top_k=5, provider='anthropic'):

*See sub-skills for full details.*

## Step 5: CLI Interface


```python
#!/usr/bin/env python3
"""RAG Query CLI - Ask questions about your documents."""

import argparse
import os

def main():
    parser = argparse.ArgumentParser(description='RAG Q&A System')
    parser.add_argument('question', nargs='?', help='Question to ask')

*See sub-skills for full details.*
