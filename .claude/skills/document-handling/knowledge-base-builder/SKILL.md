---
name: knowledge-base-builder
description: Build searchable knowledge bases from document collections (PDFs, Word, text files). Use for creating technical libraries, standards repositories, research databases, or any large document collection requiring full-text search.
---

# Knowledge Base Builder Skill

## Overview

This skill creates searchable knowledge bases from document collections using SQLite FTS5 full-text search indexing. It handles PDF extraction, text chunking, metadata cataloging, and search interface creation.

## When to Use

- Building searchable technical standards libraries
- Creating research paper databases
- Indexing corporate document repositories
- Setting up knowledge management systems
- Converting file-based document collections to queryable databases

## Architecture

```
Document Collection
       │
       ▼
┌─────────────────┐
│  1. Inventory   │  Scan files, extract metadata
└────────┬────────┘
         ▼
┌─────────────────┐
│  2. Extract     │  PDF → text, chunk by pages
└────────┬────────┘
         ▼
┌─────────────────┐
│  3. Index       │  SQLite FTS5 full-text search
└────────┬────────┘
         ▼
┌─────────────────┐
│  4. Search CLI  │  Query interface with filtering
└─────────────────┘
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
            id INTEGER PRIMARY KEY,
            filename TEXT NOT NULL,
            filepath TEXT NOT NULL,
            category TEXT,
            file_size INTEGER,
            page_count INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Text chunks table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chunks (
            id INTEGER PRIMARY KEY,
            doc_id INTEGER,
            page_num INTEGER,
            chunk_text TEXT,
            char_count INTEGER,
            FOREIGN KEY (doc_id) REFERENCES documents(id)
        )
    ''')

    # FTS5 search index
    cursor.execute('''
        CREATE VIRTUAL TABLE IF NOT EXISTS chunks_fts
        USING fts5(chunk_text, content='chunks', content_rowid='id')
    ''')

    # Triggers for FTS sync
    cursor.execute('''
        CREATE TRIGGER IF NOT EXISTS chunks_ai AFTER INSERT ON chunks BEGIN
            INSERT INTO chunks_fts(rowid, chunk_text) VALUES (new.id, new.chunk_text);
        END
    ''')

    conn.commit()
    return conn
```

### Step 2: Document Inventory

```python
from pathlib import Path
import os

def build_inventory(root_path, extensions=['.pdf', '.docx', '.txt']):
    """Scan directory and catalog all documents."""
    documents = []

    for filepath in Path(root_path).rglob('*'):
        if filepath.suffix.lower() in extensions:
            stat = filepath.stat()
            documents.append({
                'filename': filepath.name,
                'filepath': str(filepath),
                'category': categorize_document(filepath),
                'file_size': stat.st_size,
            })

    return documents

def categorize_document(filepath):
    """Auto-categorize based on path or filename patterns."""
    name = filepath.name.upper()

    patterns = {
        'API': 'API',
        'ISO': 'ISO',
        'DNV': 'DNV',
        'ASME': 'ASME',
        'NORSOK': 'NORSOK',
    }

    for pattern, category in patterns.items():
        if pattern in name:
            return category

    return 'Unknown'
```

### Step 3: PDF Text Extraction

```python
import fitz  # PyMuPDF

def extract_pdf_text(filepath, chunk_size=2000):
    """Extract text from PDF, chunked by approximate size."""
    doc = fitz.open(filepath)
    chunks = []

    for page_num, page in enumerate(doc, 1):
        text = page.get_text()
        if text.strip():
            # Split into manageable chunks
            for i in range(0, len(text), chunk_size):
                chunk = text[i:i + chunk_size]
                chunks.append({
                    'page_num': page_num,
                    'text': chunk,
                    'char_count': len(chunk)
                })

    doc.close()
    return chunks
```

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
            c.page_num,
            snippet(chunks_fts, 0, '>>> ', ' <<<', '...', 32) as snippet,
            bm25(chunks_fts) as score
        FROM chunks_fts
        JOIN chunks c ON chunks_fts.rowid = c.id
        JOIN documents d ON c.doc_id = d.id
        WHERE chunks_fts MATCH ?
        ORDER BY score
        LIMIT ?
    ''', (query, limit))

    return cursor.fetchall()
```

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

## Best Practices

1. **Use SQLite timeout** - Add `timeout=30` for concurrent access
2. **Chunk appropriately** - 1000-2000 chars optimal for search
3. **Index progressively** - Process in batches for large collections
4. **Background processing** - Use service scripts for long extractions
5. **Category detection** - Auto-categorize from filename/path patterns

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

---

## Version History

- **1.0.0** (2024-10-15): Initial release with SQLite FTS5 full-text search, PDF extraction, CLI
