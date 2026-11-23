---
name: document-rag-pipeline-step-1-database-schema
description: 'Sub-skill of document-rag-pipeline: Step 1: Database Schema (+5).'
version: 1.1.0
category: data
type: reference
scripts_exempt: true
---

# Step 1: Database Schema (+5)

## Step 1: Database Schema


```python
import sqlite3
from pathlib import Path
from datetime import datetime

def create_database(db_path):
    """Create SQLite database with full schema."""
    conn = sqlite3.connect(db_path, timeout=30)
    cursor = conn.cursor()


*See sub-skills for full details.*

## Step 2: PDF Text Extraction


```python
import fitz  # PyMuPDF

def extract_pdf_text(pdf_path):
    """Extract text from PDF using PyMuPDF."""
    try:
        doc = fitz.open(pdf_path)
        text_parts = []

        for page_num in range(len(doc)):

*See sub-skills for full details.*

## Step 3: OCR for Scanned PDFs


```python
import fitz
import pytesseract
from PIL import Image
import io

def ocr_pdf(pdf_path, dpi=200):
    """OCR scanned PDF using Tesseract."""
    try:
        doc = fitz.open(pdf_path)

*See sub-skills for full details.*

## Step 4: Text Chunking


```python
def chunk_text(text, chunk_size=1000, overlap=200):
    """Split text into overlapping chunks."""
    chunks = []
    start = 0
    text_len = len(text)

    while start < text_len:
        end = start + chunk_size
        chunk = text[start:end]

*See sub-skills for full details.*

## Step 5: Embedding Generation


```python
from sentence_transformers import SentenceTransformer
import numpy as np
import pickle
import os

# Force CPU mode (for CUDA compatibility issues)
os.environ["CUDA_VISIBLE_DEVICES"] = ""

def create_embeddings(db_path, model_name='all-MiniLM-L6-v2', batch_size=100):

*See sub-skills for full details.*

## Step 6: Semantic Search


```python
def semantic_search(db_path, query, top_k=10, sample_size=50000):
    """Search for similar chunks using cosine similarity."""

    # Force CPU mode
    os.environ["CUDA_VISIBLE_DEVICES"] = ""

    model = SentenceTransformer('all-MiniLM-L6-v2')
    query_emb = model.encode(query, normalize_embeddings=True)


*See sub-skills for full details.*
