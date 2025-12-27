#!/usr/bin/env python3
"""
ABOUTME: O&G Standards Vector Embedding Generator
ABOUTME: Creates embeddings for semantic search using OpenAI or local models

Usage:
    python embed.py [--config config.yaml] [--limit N] [--model openai|local]
"""

import argparse
import logging
import os
import pickle
import sqlite3
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Tuple

import yaml

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


def get_openai_embeddings(texts: List[str], model: str = "text-embedding-3-small") -> List[List[float]]:
    """
    Generate embeddings using OpenAI API.

    Args:
        texts: List of text strings to embed
        model: OpenAI embedding model name

    Returns:
        List of embedding vectors
    """
    try:
        from openai import OpenAI
    except ImportError:
        logger.error("OpenAI not installed. Run: pip install openai")
        return []

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        logger.error("OPENAI_API_KEY environment variable not set")
        return []

    client = OpenAI(api_key=api_key)

    # OpenAI has a limit on batch size
    batch_size = 100
    all_embeddings = []

    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        try:
            response = client.embeddings.create(
                model=model,
                input=batch
            )
            batch_embeddings = [item.embedding for item in response.data]
            all_embeddings.extend(batch_embeddings)
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            # Return empty embeddings for failed batch
            all_embeddings.extend([[] for _ in batch])

    return all_embeddings


def get_local_embeddings(texts: List[str], model_name: str = "all-MiniLM-L6-v2") -> List[List[float]]:
    """
    Generate embeddings using local sentence-transformers model.

    Args:
        texts: List of text strings to embed
        model_name: Sentence-transformers model name

    Returns:
        List of embedding vectors
    """
    try:
        from sentence_transformers import SentenceTransformer
    except ImportError:
        logger.error("sentence-transformers not installed. Run: pip install sentence-transformers")
        return []

    try:
        model = SentenceTransformer(model_name)
        embeddings = model.encode(texts, show_progress_bar=True)
        return [emb.tolist() for emb in embeddings]
    except Exception as e:
        logger.error(f"Local embedding error: {e}")
        return []


class EmbeddingGenerator:
    """Generate and store embeddings for O&G standards text chunks."""

    def __init__(self, config_path: str):
        """Initialize with configuration file."""
        self.config = self._load_config(config_path)
        self.db_path = self.config['database_path']
        self.conn = None
        self.stats = {
            'processed': 0,
            'embedded': 0,
            'skipped': 0,
            'errors': 0,
        }

    def _load_config(self, config_path: str) -> dict:
        """Load configuration from YAML file."""
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)

    def connect(self):
        """Connect to database and ensure embedding columns exist."""
        if not os.path.exists(self.db_path):
            logger.error(f"Database not found: {self.db_path}")
            logger.error("Run extract.py first to extract text")
            sys.exit(1)

        self.conn = sqlite3.connect(self.db_path, timeout=30)
        self.conn.row_factory = sqlite3.Row

        # Add embedding column if not exists
        cursor = self.conn.cursor()
        try:
            cursor.execute('ALTER TABLE text_chunks ADD COLUMN embedding_model TEXT')
        except sqlite3.OperationalError:
            pass  # Column already exists

        self.conn.commit()
        logger.info("Connected to database")

    def get_chunks_to_embed(self, limit: int = None, force: bool = False) -> List[dict]:
        """Get text chunks that need embedding."""
        cursor = self.conn.cursor()

        if force:
            sql = '''
                SELECT tc.id, tc.document_id, tc.chunk_num, tc.chunk_text,
                       d.filename, d.organization
                FROM text_chunks tc
                JOIN documents d ON tc.document_id = d.id
                WHERE tc.chunk_text IS NOT NULL
                  AND tc.chunk_text != ''
                ORDER BY tc.id
            '''
        else:
            sql = '''
                SELECT tc.id, tc.document_id, tc.chunk_num, tc.chunk_text,
                       d.filename, d.organization
                FROM text_chunks tc
                JOIN documents d ON tc.document_id = d.id
                WHERE tc.embedding IS NULL
                  AND tc.chunk_text IS NOT NULL
                  AND tc.chunk_text != ''
                ORDER BY tc.id
            '''

        cursor.execute(sql)
        results = [dict(row) for row in cursor.fetchall()]

        if limit:
            results = results[:limit]

        return results

    def save_embeddings(self, chunk_ids: List[int], embeddings: List[List[float]],
                        model_name: str):
        """Save embeddings to database."""
        cursor = self.conn.cursor()

        for chunk_id, embedding in zip(chunk_ids, embeddings):
            if embedding:
                # Serialize embedding as blob
                embedding_blob = pickle.dumps(embedding)
                cursor.execute('''
                    UPDATE text_chunks
                    SET embedding = ?, embedding_model = ?
                    WHERE id = ?
                ''', (embedding_blob, model_name, chunk_id))
                self.stats['embedded'] += 1
            else:
                self.stats['errors'] += 1

        self.conn.commit()

    def generate_embeddings(self, model_type: str = "local",
                            model_name: str = None,
                            limit: int = None,
                            batch_size: int = 50,
                            force: bool = False):
        """
        Generate embeddings for all unprocessed chunks.

        Args:
            model_type: 'openai' or 'local'
            model_name: Specific model name (optional)
            limit: Maximum chunks to process
            batch_size: Chunks per embedding batch
            force: Re-embed even if already done
        """
        chunks = self.get_chunks_to_embed(limit=limit, force=force)
        total = len(chunks)

        if total == 0:
            logger.info("No chunks to embed")
            return

        logger.info(f"Generating embeddings for {total} chunks...")

        # Set default model names
        if model_name is None:
            if model_type == "openai":
                model_name = "text-embedding-3-small"
            else:
                model_name = "all-MiniLM-L6-v2"

        # Process in batches
        for i in range(0, total, batch_size):
            batch = chunks[i:i + batch_size]
            texts = [c['chunk_text'] for c in batch]
            chunk_ids = [c['id'] for c in batch]

            # Generate embeddings
            if model_type == "openai":
                embeddings = get_openai_embeddings(texts, model_name)
            else:
                embeddings = get_local_embeddings(texts, model_name)

            if embeddings:
                self.save_embeddings(chunk_ids, embeddings, model_name)

            self.stats['processed'] += len(batch)

            # Progress
            if (i + batch_size) % 500 == 0 or i + batch_size >= total:
                pct = min(100, (i + batch_size) / total * 100)
                logger.info(f"Progress: {i + batch_size:,}/{total:,} ({pct:.1f}%)")

        self._print_summary()

    def _print_summary(self):
        """Print embedding summary."""
        print("\n" + "=" * 60)
        print("EMBEDDING GENERATION COMPLETE")
        print("=" * 60)
        print(f"Chunks processed: {self.stats['processed']:,}")
        print(f"Embeddings saved: {self.stats['embedded']:,}")
        print(f"Errors:           {self.stats['errors']:,}")
        print("=" * 60)

    def get_embedding_stats(self) -> dict:
        """Get current embedding statistics."""
        cursor = self.conn.cursor()

        stats = {}

        # Total chunks
        cursor.execute("SELECT COUNT(*) FROM text_chunks")
        stats['total_chunks'] = cursor.fetchone()[0]

        # Embedded chunks
        cursor.execute("SELECT COUNT(*) FROM text_chunks WHERE embedding IS NOT NULL")
        stats['embedded'] = cursor.fetchone()[0]

        # Models used
        cursor.execute("""
            SELECT embedding_model, COUNT(*) as count
            FROM text_chunks
            WHERE embedding_model IS NOT NULL
            GROUP BY embedding_model
        """)
        stats['models'] = dict(cursor.fetchall())

        return stats

    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()


def main():
    parser = argparse.ArgumentParser(
        description='Generate vector embeddings for O&G standards'
    )
    parser.add_argument(
        '--config', '-c',
        default='config.yaml',
        help='Path to configuration file (default: config.yaml)'
    )
    parser.add_argument(
        '--model', '-m',
        choices=['openai', 'local'],
        default='local',
        help='Embedding model type (default: local)'
    )
    parser.add_argument(
        '--model-name',
        help='Specific model name (e.g., text-embedding-3-small or all-MiniLM-L6-v2)'
    )
    parser.add_argument(
        '--limit', '-n',
        type=int,
        help='Maximum number of chunks to process'
    )
    parser.add_argument(
        '--batch-size', '-b',
        type=int,
        default=50,
        help='Chunks per embedding batch (default: 50)'
    )
    parser.add_argument(
        '--force', '-f',
        action='store_true',
        help='Re-embed even if already processed'
    )
    parser.add_argument(
        '--stats',
        action='store_true',
        help='Show embedding statistics only'
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

    # Run embedding
    generator = EmbeddingGenerator(config_path)

    try:
        generator.connect()

        if args.stats:
            stats = generator.get_embedding_stats()
            print("\n" + "=" * 50)
            print("EMBEDDING STATISTICS")
            print("=" * 50)
            print(f"Total chunks:    {stats['total_chunks']:,}")
            print(f"Embedded:        {stats['embedded']:,}")
            if stats['models']:
                print("Models used:")
                for model, count in stats['models'].items():
                    print(f"  - {model}: {count:,}")
            print("=" * 50)
        else:
            generator.generate_embeddings(
                model_type=args.model,
                model_name=args.model_name,
                limit=args.limit,
                batch_size=args.batch_size,
                force=args.force
            )
    finally:
        generator.close()


if __name__ == '__main__':
    main()
