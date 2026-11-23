# Knowledge Base Builder — Implementation Details

## Step 1: Create Database Schema

```python
import sqlite3

def create_knowledge_base(db_path):
    conn = sqlite3.connect(db_path, timeout=30)
    cursor = conn.cursor()

    # Documents table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS documents (

*See sub-skills for full details.*
```

## Step 2: Document Inventory

```python
from pathlib import Path
import os

def build_inventory(root_path, extensions=['.pdf', '.docx', '.txt']):
    """Scan directory and catalog all documents."""
    documents = []

    for filepath in Path(root_path).rglob('*'):
        if filepath.suffix.lower() in extensions:

*See sub-skills for full details.*
```

## Step 3: PDF Text Extraction

```python
import fitz  # PyMuPDF

def extract_pdf_text(filepath, chunk_size=2000):
    """Extract text from PDF, chunked by approximate size."""
    doc = fitz.open(filepath)
    chunks = []

    for page_num, page in enumerate(doc, 1):
        text = page.get_text()

*See sub-skills for full details.*
```

## Step 4: Search Interface

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
