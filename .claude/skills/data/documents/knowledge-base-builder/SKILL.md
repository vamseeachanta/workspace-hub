---
name: knowledge-base-builder
description: Build searchable knowledge bases from document collections (PDFs, Word,
  text files). Use for creating technical libraries, standards repositories, research
  databases, or any large document collection requiring full-text search.
version: 1.1.0
last_updated: 2026-01-02
category: data
related_skills:
- pdf-text-extractor
- semantic-search-setup
- rag-system-builder
capabilities: []
requires: []
see_also:
- knowledge-base-builder-execution-checklist
- knowledge-base-builder-error-handling
- knowledge-base-builder-metrics
- knowledge-base-builder-best-practices
- knowledge-base-builder-dependencies
tags: []
---

# Knowledge Base Builder

## Overview

This skill creates searchable knowledge bases from document collections using SQLite FTS5 full-text search indexing. It handles PDF extraction, text chunking, metadata cataloging, and search interface creation.

## Quick Start

```python
import sqlite3

conn = sqlite3.connect("knowledge.db", timeout=30)
cursor = conn.cursor()

# Create FTS5 search table
cursor.execute('''
    CREATE VIRTUAL TABLE IF NOT EXISTS search_index
    USING fts5(content, filename)
''')

# Add content
cursor.execute('INSERT INTO search_index VALUES (?, ?)',
               ("Sample document text...", "doc.pdf"))

# Search
cursor.execute("SELECT * FROM search_index WHERE search_index MATCH 'sample'")
print(cursor.fetchall())
```

## When to Use

- Building searchable technical standards libraries
- Creating research paper databases
- Indexing corporate document repositories
- Setting up knowledge management systems
- Converting file-based document collections to queryable databases

## Architecture

```
Document Collection
       |
       v
+------------------+
|  1. Inventory    |  Scan files, extract metadata
+--------+---------+
         v
+------------------+
|  2. Extract      |  PDF -> text, chunk by pages
+--------+---------+
         v
+------------------+
|  3. Index        |  SQLite FTS5 full-text search
+--------+---------+
         v
+------------------+
|  4. Search CLI   |  Query interface with filtering
+------------------+
```

## Implementation Steps

### Step 1: Create Database Schema

```python
import sqlite3

def create_knowledge_base(db_path):
    conn = sqlite3.connect(db_path, timeout=30)
    cursor = conn.cursor()

    # Documents table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS documents (

*See sub-skills for full details.*
### Step 2: Document Inventory

```python
from pathlib import Path
import os

def build_inventory(root_path, extensions=['.pdf', '.docx', '.txt']):
    """Scan directory and catalog all documents."""
    documents = []

    for filepath in Path(root_path).rglob('*'):
        if filepath.suffix.lower() in extensions:

*See sub-skills for full details.*
### Step 3: PDF Text Extraction

```python
import fitz  # PyMuPDF

def extract_pdf_text(filepath, chunk_size=2000):
    """Extract text from PDF, chunked by approximate size."""
    doc = fitz.open(filepath)
    chunks = []

    for page_num, page in enumerate(doc, 1):
        text = page.get_text()

*See sub-skills for full details.*
### Step 4: Search Interface

```python
def search_knowledge_base(db_path, query, limit=20):
    """Full-text search with ranking."""
    conn = sqlite3.connect(db_path, timeout=30)
    cursor = conn.cursor()

    cursor.execute('''
        SELECT
            d.filename,
            d.category,

*See sub-skills for full details.*

## CLI Template

```bash
#!/bin/bash
# kb - Knowledge Base Search CLI

DB_PATH="${KB_DATABASE:-./knowledge.db}"

search() {
    sqlite3 "$DB_PATH" "
        SELECT d.filename, c.page_num,
               snippet(chunks_fts, 0, '>>>', '<<<', '...', 20)
        FROM chunks_fts
        JOIN chunks c ON chunks_fts.rowid = c.id
        JOIN documents d ON c.doc_id = d.id
        WHERE chunks_fts MATCH '$1'
        LIMIT 20
    "
}

case "$1" in
    search) search "$2" ;;
    status) sqlite3 "$DB_PATH" "SELECT COUNT(*) FROM documents" ;;
    *) echo "Usage: kb {search|status} [query]" ;;
esac
```

## Example Usage

```bash
# Build knowledge base
python inventory.py /path/to/documents
python extract.py --db knowledge.db
python index.py --db knowledge.db

# Search
./kb search "fatigue analysis"
./kb search "API AND riser"
```

## Related Skills

- `semantic-search-setup` - Add vector embeddings for AI search
- `rag-system-builder` - Build AI Q&A on top of knowledge base
- `pdf-text-extractor` - Detailed PDF extraction options

## Version History

- **1.1.0** (2026-01-02): Added Quick Start, Execution Checklist, Error Handling, Metrics sections; updated frontmatter with version, category, related_skills
- **1.0.0** (2024-10-15): Initial release with SQLite FTS5 full-text search, PDF extraction, CLI

## Sub-Skills

- [Execution Checklist](execution-checklist/SKILL.md)
- [Error Handling](error-handling/SKILL.md)
- [Metrics](metrics/SKILL.md)
- [Best Practices](best-practices/SKILL.md)
- [Dependencies](dependencies/SKILL.md)
