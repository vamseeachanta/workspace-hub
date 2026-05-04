---
name: knowledge-base-builder
description: Build searchable knowledge bases from document collections (PDFs, Word,
  text files). Use for creating technical libraries, standards repositories, research
  databases, or any large document collection requiring full-text search.
type: reference
version: 1.1.0
last_updated: 2026-01-02
category: data
related_skills:
- semantic-search-setup
- rag-system-builder
capabilities: []
requires: []
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

See [references/implementation.md](references/implementation.md) for detailed code for each step (schema creation, document inventory, PDF extraction, search interface, CLI template, and usage examples).

## Related Skills

- `semantic-search-setup` - Add vector embeddings for AI search
- `rag-system-builder` - Build AI Q&A on top of knowledge base
- `pdf/text-extractor` - Detailed PDF extraction options

## Version History

- **1.1.0** (2026-01-02): Added Quick Start, Execution Checklist, Error Handling, Metrics sections; updated frontmatter with version, category, related_skills
- **1.0.0** (2024-10-15): Initial release with SQLite FTS5 full-text search, PDF extraction, CLI

## Sub-Skills

- [Execution Checklist](execution-checklist/SKILL.md)
- [Error Handling](error-handling/SKILL.md)
- [Metrics](metrics/SKILL.md)
- [Best Practices](best-practices/SKILL.md)
- [Dependencies](dependencies/SKILL.md)
