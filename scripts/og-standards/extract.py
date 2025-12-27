#!/usr/bin/env python3
"""
ABOUTME: O&G Standards PDF Text Extraction Pipeline
ABOUTME: Extracts text from PDFs for vector embedding and semantic search

Usage:
    python extract.py [--config config.yaml] [--limit N] [--force]
"""

import argparse
import hashlib
import logging
import os
import sqlite3
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import yaml

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


def extract_pdf_text(pdf_path: str) -> Tuple[str, str, int]:
    """
    Extract text from PDF file.

    Args:
        pdf_path: Path to PDF file

    Returns:
        Tuple of (text_content, extraction_method, page_count)
    """
    try:
        import fitz  # PyMuPDF
    except ImportError:
        logger.error("PyMuPDF not installed. Run: pip install pymupdf")
        return "", "error", 0

    try:
        doc = fitz.open(pdf_path)
        text_parts = []
        page_count = len(doc)

        for page_num, page in enumerate(doc):
            text = page.get_text("text")
            if text.strip():
                text_parts.append(f"[Page {page_num + 1}]\n{text}")

        doc.close()

        full_text = "\n\n".join(text_parts)

        # If no text extracted, might be scanned PDF
        if not full_text.strip():
            return "", "no_text", page_count

        return full_text, "pymupdf", page_count

    except Exception as e:
        logger.warning(f"Failed to extract from {pdf_path}: {e}")
        return "", "error", 0


def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> List[Dict]:
    """
    Split text into overlapping chunks for embedding.

    Args:
        text: Full document text
        chunk_size: Target chunk size in characters
        overlap: Overlap between chunks

    Returns:
        List of chunk dictionaries with text and metadata
    """
    if not text.strip():
        return []

    chunks = []
    words = text.split()

    if len(words) == 0:
        return []

    # Approximate words per chunk (assuming average 5 chars per word)
    words_per_chunk = chunk_size // 5
    overlap_words = overlap // 5

    start = 0
    chunk_num = 0

    while start < len(words):
        end = min(start + words_per_chunk, len(words))
        chunk_words = words[start:end]
        chunk_text = " ".join(chunk_words)

        chunks.append({
            "chunk_id": chunk_num,
            "text": chunk_text,
            "start_word": start,
            "end_word": end,
            "word_count": len(chunk_words),
            "char_count": len(chunk_text)
        })

        chunk_num += 1
        start = end - overlap_words

        if start >= len(words) - overlap_words:
            break

    return chunks


class TextExtractor:
    """Extract and store text from O&G standards PDFs."""

    def __init__(self, config_path: str):
        """Initialize with configuration file."""
        self.config = self._load_config(config_path)
        self.db_path = self.config['database_path']
        self.target_dir = self.config['target_directory']
        self.conn = None
        self.stats = {
            'processed': 0,
            'extracted': 0,
            'skipped': 0,
            'errors': 0,
            'total_chunks': 0,
            'total_chars': 0,
        }

    def _load_config(self, config_path: str) -> dict:
        """Load configuration from YAML file."""
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)

    def connect(self):
        """Connect to database and setup text tables."""
        if not os.path.exists(self.db_path):
            logger.error(f"Database not found: {self.db_path}")
            logger.error("Run the consolidation pipeline first")
            sys.exit(1)

        self.conn = sqlite3.connect(self.db_path, timeout=30)
        self.conn.row_factory = sqlite3.Row

        # Create text extraction tables
        cursor = self.conn.cursor()

        # Document text content
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS document_text (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                document_id INTEGER UNIQUE NOT NULL,
                full_text TEXT,
                extraction_method TEXT,
                page_count INTEGER,
                char_count INTEGER,
                word_count INTEGER,
                extracted_date TEXT,
                FOREIGN KEY (document_id) REFERENCES documents(id)
            )
        ''')

        # Text chunks for embedding
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS text_chunks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                document_id INTEGER NOT NULL,
                chunk_num INTEGER NOT NULL,
                chunk_text TEXT NOT NULL,
                start_word INTEGER,
                end_word INTEGER,
                word_count INTEGER,
                char_count INTEGER,
                embedding BLOB,
                FOREIGN KEY (document_id) REFERENCES documents(id),
                UNIQUE(document_id, chunk_num)
            )
        ''')

        # Create indexes
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_text_document_id ON document_text(document_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_chunks_document_id ON text_chunks(document_id)')

        self.conn.commit()
        logger.info("Text extraction tables initialized")

    def get_pdfs_to_process(self, force: bool = False, limit: int = None) -> List[dict]:
        """Get list of PDFs needing text extraction."""
        cursor = self.conn.cursor()

        if force:
            # Get all PDFs
            sql = '''
                SELECT id, filename, target_path, file_size
                FROM documents
                WHERE is_duplicate = 0
                  AND extension = '.pdf'
                  AND target_path IS NOT NULL
                ORDER BY file_size ASC
            '''
        else:
            # Get only unprocessed PDFs
            sql = '''
                SELECT d.id, d.filename, d.target_path, d.file_size
                FROM documents d
                LEFT JOIN document_text dt ON d.id = dt.document_id
                WHERE d.is_duplicate = 0
                  AND d.extension = '.pdf'
                  AND d.target_path IS NOT NULL
                  AND dt.id IS NULL
                ORDER BY d.file_size ASC
            '''

        cursor.execute(sql)
        results = [dict(row) for row in cursor.fetchall()]

        if limit:
            results = results[:limit]

        return results

    def process_pdf(self, doc: dict) -> Optional[dict]:
        """Process single PDF and extract text."""
        doc_id = doc['id']
        pdf_path = doc['target_path']

        if not os.path.exists(pdf_path):
            logger.warning(f"File not found: {pdf_path}")
            return None

        # Extract text
        text, method, page_count = extract_pdf_text(pdf_path)

        if not text:
            return {
                'document_id': doc_id,
                'full_text': '',
                'extraction_method': method,
                'page_count': page_count,
                'char_count': 0,
                'word_count': 0,
                'chunks': []
            }

        # Create chunks
        chunks = chunk_text(text, chunk_size=1000, overlap=200)

        word_count = len(text.split())
        char_count = len(text)

        return {
            'document_id': doc_id,
            'full_text': text,
            'extraction_method': method,
            'page_count': page_count,
            'char_count': char_count,
            'word_count': word_count,
            'chunks': chunks
        }

    def save_extraction(self, result: dict):
        """Save extraction result to database."""
        cursor = self.conn.cursor()
        extracted_date = datetime.now().isoformat()

        # Save full text
        cursor.execute('''
            INSERT OR REPLACE INTO document_text
            (document_id, full_text, extraction_method, page_count,
             char_count, word_count, extracted_date)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            result['document_id'],
            result['full_text'],
            result['extraction_method'],
            result['page_count'],
            result['char_count'],
            result['word_count'],
            extracted_date
        ))

        # Save chunks
        for chunk in result['chunks']:
            cursor.execute('''
                INSERT OR REPLACE INTO text_chunks
                (document_id, chunk_num, chunk_text, start_word, end_word,
                 word_count, char_count)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                result['document_id'],
                chunk['chunk_id'],
                chunk['text'],
                chunk['start_word'],
                chunk['end_word'],
                chunk['word_count'],
                chunk['char_count']
            ))

        self.conn.commit()

    def extract_all(self, force: bool = False, limit: int = None,
                    workers: int = 4):
        """
        Extract text from all PDFs.

        Args:
            force: Re-extract even if already processed
            limit: Maximum number of files to process
            workers: Number of parallel workers
        """
        pdfs = self.get_pdfs_to_process(force=force, limit=limit)
        total = len(pdfs)

        if total == 0:
            logger.info("No PDFs to process")
            return

        logger.info(f"Processing {total} PDFs...")

        for i, doc in enumerate(pdfs, 1):
            try:
                result = self.process_pdf(doc)

                if result:
                    self.save_extraction(result)

                    if result['full_text']:
                        self.stats['extracted'] += 1
                        self.stats['total_chunks'] += len(result['chunks'])
                        self.stats['total_chars'] += result['char_count']
                    else:
                        self.stats['skipped'] += 1

                self.stats['processed'] += 1

                # Progress update
                if i % 100 == 0 or i == total:
                    pct = i / total * 100
                    logger.info(f"Progress: {i:,}/{total:,} ({pct:.1f}%) - "
                               f"Extracted: {self.stats['extracted']:,}")

            except Exception as e:
                logger.error(f"Error processing {doc['filename']}: {e}")
                self.stats['errors'] += 1

        self._print_summary()

    def _print_summary(self):
        """Print extraction summary."""
        print("\n" + "=" * 60)
        print("TEXT EXTRACTION COMPLETE")
        print("=" * 60)
        print(f"Files processed:    {self.stats['processed']:,}")
        print(f"Text extracted:     {self.stats['extracted']:,}")
        print(f"Skipped (no text):  {self.stats['skipped']:,}")
        print(f"Errors:             {self.stats['errors']:,}")
        print(f"Total chunks:       {self.stats['total_chunks']:,}")
        print(f"Total characters:   {self.stats['total_chars']:,}")
        if self.stats['total_chars'] > 0:
            mb = self.stats['total_chars'] / (1024 * 1024)
            print(f"Text size:          {mb:.2f} MB")
        print("=" * 60)

    def get_extraction_stats(self) -> dict:
        """Get current extraction statistics."""
        cursor = self.conn.cursor()

        stats = {}

        # Total PDFs
        cursor.execute("""
            SELECT COUNT(*) FROM documents
            WHERE is_duplicate = 0 AND extension = '.pdf'
        """)
        stats['total_pdfs'] = cursor.fetchone()[0]

        # Extracted
        cursor.execute("SELECT COUNT(*) FROM document_text WHERE char_count > 0")
        stats['extracted'] = cursor.fetchone()[0]

        # Total chunks
        cursor.execute("SELECT COUNT(*) FROM text_chunks")
        stats['total_chunks'] = cursor.fetchone()[0]

        # Total characters
        cursor.execute("SELECT SUM(char_count) FROM document_text")
        stats['total_chars'] = cursor.fetchone()[0] or 0

        return stats

    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()


def main():
    parser = argparse.ArgumentParser(
        description='Extract text from O&G standards PDFs'
    )
    parser.add_argument(
        '--config', '-c',
        default='config.yaml',
        help='Path to configuration file (default: config.yaml)'
    )
    parser.add_argument(
        '--limit', '-n',
        type=int,
        help='Maximum number of files to process'
    )
    parser.add_argument(
        '--force', '-f',
        action='store_true',
        help='Re-extract even if already processed'
    )
    parser.add_argument(
        '--workers', '-w',
        type=int,
        default=1,
        help='Number of parallel workers (default: 1)'
    )
    parser.add_argument(
        '--stats',
        action='store_true',
        help='Show extraction statistics only'
    )

    args = parser.parse_args()

    # Find config file
    config_path = args.config
    if not os.path.isabs(config_path):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(script_dir, config_path)

    if not os.path.exists(config_path):
        logger.error(f"Configuration file not found: {config_path}")
        sys.exit(1)

    # Run extraction
    extractor = TextExtractor(config_path)

    try:
        extractor.connect()

        if args.stats:
            stats = extractor.get_extraction_stats()
            print("\n" + "=" * 50)
            print("TEXT EXTRACTION STATISTICS")
            print("=" * 50)
            print(f"Total PDFs:      {stats['total_pdfs']:,}")
            print(f"Text extracted:  {stats['extracted']:,}")
            print(f"Total chunks:    {stats['total_chunks']:,}")
            print(f"Total chars:     {stats['total_chars']:,}")
            if stats['total_chars'] > 0:
                mb = stats['total_chars'] / (1024 * 1024)
                print(f"Text size:       {mb:.2f} MB")
            print("=" * 50)
        else:
            extractor.extract_all(
                force=args.force,
                limit=args.limit,
                workers=args.workers
            )
    finally:
        extractor.close()


if __name__ == '__main__':
    main()
