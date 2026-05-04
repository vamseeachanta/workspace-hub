---
name: document-inventory
description: Scan and catalog document collections with metadata extraction, categorization,
  and statistics. Use for auditing document libraries, preparing for knowledge base
  creation, or understanding large file collections.
type: reference
version: 1.1.0
last_updated: 2026-01-02
category: data
related_skills:
- knowledge-base-builder
- semantic-search-setup
capabilities: []
requires: []
tags: []
---

# Document Inventory

## Overview

This skill scans document collections (PDFs, Word docs, text files) and creates a structured inventory with metadata, automatic categorization, and collection statistics. Essential first step before building knowledge bases.

## Quick Start

```python
from pathlib import Path
import sqlite3

# Scan directory
documents = []
for filepath in Path("/path/to/docs").rglob("*.pdf"):
    documents.append({
        'filename': filepath.name,
        'size': filepath.stat().st_size,
        'path': str(filepath)
    })

# Store in database
conn = sqlite3.connect("inventory.db")
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS docs (name TEXT, size INTEGER, path TEXT)")
for doc in documents:
    cursor.execute("INSERT INTO docs VALUES (?, ?, ?)",
                   (doc['filename'], doc['size'], doc['path']))
conn.commit()
print(f"Inventoried {len(documents)} documents")
```

## When to Use

- Auditing large document libraries before processing
- Understanding the scope of a document collection
- Categorizing documents by type, source, or content
- Preparing inventories for knowledge base creation
- Generating reports on document collections
- Identifying duplicates or organizing files

## Features

- **Recursive scanning** - Process nested directories
- **Metadata extraction** - Size, dates, page counts
- **Auto-categorization** - Pattern-based classification
- **Statistics generation** - Collection summaries
- **SQLite storage** - Queryable inventory database
- **Multiple formats** - PDF, DOCX, TXT, and more

## Implementation

### Core Inventory Builder

```python
#!/usr/bin/env python3
"""Document inventory builder."""

import sqlite3
import os
from pathlib import Path
from datetime import datetime
import logging


*See sub-skills for full details.*
### CLI Interface

```python
#!/usr/bin/env python3
"""Document Inventory CLI."""

import argparse
import json

def main():
    parser = argparse.ArgumentParser(description='Document Inventory Tool')
    subparsers = parser.add_subparsers(dest='command', help='Commands')

*See sub-skills for full details.*
### Report Generator

```python
def generate_report(db_path, output_path):
    """Generate HTML inventory report."""
    inventory = DocumentInventory(db_path)
    stats = inventory.get_statistics()

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>

*See sub-skills for full details.*

## Custom Categorization

### Extend with Your Patterns

```python
# Add custom patterns for your domain
CUSTOM_PATTERNS = {
    'SPEC': 'Specifications',
    'DWG': 'Drawings',
    'REV': 'Revisions',
    'APPROVED': 'Approved',
    'DRAFT': 'Draft',
    'SUPERSEDED': 'Superseded',
}

*See sub-skills for full details.*
### Multi-Level Categories

```python
def categorize_hierarchical(filepath):
    """Create hierarchical categories."""
    name = filepath.name.upper()

    # Primary category
    primary = 'General'
    if 'API' in name:
        primary = 'API Standards'
    elif 'ISO' in name:

*See sub-skills for full details.*

## Example Usage

```bash
# Scan directory
python inventory.py scan /path/to/documents --db inventory.db

# View statistics
python inventory.py stats --db inventory.db

# Search
python inventory.py search "API" --category "Standards"

# Export to CSV
python inventory.py export inventory.csv --db inventory.db
```

## Related Skills

- `knowledge-base-builder` - Build searchable database after inventory
- `pdf/text-extractor` - Extract text from inventoried PDFs
- `semantic-search-setup` - Add AI search capabilities

## Version History

- **1.1.0** (2026-01-02): Added Quick Start, Execution Checklist, Error Handling, Metrics sections; updated frontmatter with version, category, related_skills
- **1.0.0** (2024-10-15): Initial release with SQLite storage, auto-categorization, CLI interface

## Sub-Skills

- [Best Practices](best-practices/SKILL.md)

## Sub-Skills

- [Execution Checklist](execution-checklist/SKILL.md)
- [Error Handling](error-handling/SKILL.md)
- [Metrics](metrics/SKILL.md)
- [Dependencies](dependencies/SKILL.md)
