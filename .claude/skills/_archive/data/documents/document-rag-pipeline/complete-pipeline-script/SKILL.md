---
name: document-rag-pipeline-complete-pipeline-script
description: 'Sub-skill of document-rag-pipeline: Complete Pipeline Script.'
version: 1.1.0
category: data
type: reference
scripts_exempt: true
---

# Complete Pipeline Script

## Complete Pipeline Script


```python
#!/usr/bin/env python3
"""
Document RAG Pipeline - Build searchable knowledge base from PDF folder.

Usage:
    python build_knowledge_base.py /path/to/documents --db inventory.db
    python build_knowledge_base.py /path/to/documents --search "query text"
"""

import argparse
import os
from pathlib import Path
from tqdm import tqdm

def build_inventory(folder_path, db_path):
    """Build document inventory from folder."""
    conn = create_database(db_path)
    cursor = conn.cursor()

    pdf_files = list(Path(folder_path).rglob("*.pdf"))
    print(f"Found {len(pdf_files)} PDF files")

    for pdf_path in tqdm(pdf_files, desc="Building inventory"):
        # Check if already processed

*See sub-skills for full details.*
