#!/usr/bin/env python3
"""
ABOUTME: O&G Standards Consolidation Script
ABOUTME: Copies unique files to organized directory structure, skipping duplicates

Usage:
    python consolidate.py [--config config.yaml] [--dry-run]
"""

import argparse
import logging
import os
import re
import shutil
import sqlite3
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Tuple

import yaml

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


class StandardsConsolidator:
    """Consolidates O&G standards into organized directory structure."""

    def __init__(self, config_path: str):
        """Initialize with configuration file."""
        self.config = self._load_config(config_path)
        self.db_path = self.config['database_path']
        self.target_dir = self.config['target_directory']
        self.conn = None
        self.dry_run = False
        self.stats = {
            'files_copied': 0,
            'files_skipped': 0,
            'bytes_copied': 0,
            'errors': 0,
            'dirs_created': 0,
        }

    def _load_config(self, config_path: str) -> dict:
        """Load configuration from YAML file."""
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)

    def connect(self):
        """Connect to database."""
        if not os.path.exists(self.db_path):
            logger.error(f"Database not found: {self.db_path}")
            logger.error("Run inventory.py and dedup.py first")
            sys.exit(1)

        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row

    def _get_subfolder(self, org: str, doc_type: str, filename: str) -> str:
        """
        Determine target subfolder based on organization and document type.

        Returns: Subfolder path like 'API/Recommended-Practice' or 'DNV/Offshore-Standards'
        """
        org_config = self.config.get('organization_mappings', {}).get(org, {})
        subfolders = org_config.get('subfolders', {})

        # Try to match document type to configured subfolders
        for subfolder_name, patterns in subfolders.items():
            for pattern in patterns:
                if pattern.upper() in (doc_type or '').upper():
                    return os.path.join(org, subfolder_name)
                if pattern.upper() in filename.upper():
                    return os.path.join(org, subfolder_name)

        # Default: just use organization folder
        return org

    def _clean_filename(self, filename: str) -> str:
        """Clean and normalize filename for consistency."""
        # Remove problematic characters
        cleaned = re.sub(r'[<>:"/\\|?*]', '_', filename)
        # Replace multiple spaces/underscores with single underscore
        cleaned = re.sub(r'[\s_]+', '_', cleaned)
        # Remove leading/trailing underscores
        cleaned = cleaned.strip('_')
        # Limit length
        name, ext = os.path.splitext(cleaned)
        if len(name) > 200:
            name = name[:200]
        return name + ext

    def _get_target_path(self, doc: dict) -> str:
        """
        Determine target path for a document.

        Returns: Full target path for the file
        """
        org = doc['organization'] or 'Other'
        doc_type = doc['doc_type'] or ''
        filename = doc['filename']

        # Get subfolder
        subfolder = self._get_subfolder(org, doc_type, filename)

        # Clean filename
        clean_name = self._clean_filename(filename)

        return os.path.join(self.target_dir, subfolder, clean_name)

    def _handle_collision(self, target_path: str, source_path: str) -> str:
        """
        Handle filename collision by adding suffix.

        Returns: Unique target path
        """
        if not os.path.exists(target_path):
            return target_path

        base, ext = os.path.splitext(target_path)
        counter = 1

        while True:
            new_path = f"{base}_{counter}{ext}"
            if not os.path.exists(new_path):
                return new_path
            counter += 1
            if counter > 100:
                # Give up and use hash
                import hashlib
                hash_suffix = hashlib.md5(source_path.encode()).hexdigest()[:8]
                return f"{base}_{hash_suffix}{ext}"

    def consolidate(self, dry_run: bool = False):
        """
        Consolidate all unique files to target directory.

        Args:
            dry_run: If True, only log what would be done without copying
        """
        self.dry_run = dry_run
        cursor = self.conn.cursor()

        # Get all non-duplicate files
        cursor.execute('''
            SELECT id, file_path, filename, file_size, organization,
                   doc_type, doc_number, title
            FROM documents
            WHERE is_duplicate = 0
            ORDER BY organization, doc_type, filename
        ''')

        files = cursor.fetchall()
        total = len(files)
        logger.info(f"Processing {total:,} unique files...")

        if dry_run:
            logger.info("DRY RUN - No files will be copied")

        for i, doc in enumerate(files, 1):
            doc = dict(doc)
            source_path = doc['file_path']
            target_path = self._get_target_path(doc)

            # Handle collision
            target_path = self._handle_collision(target_path, source_path)

            # Create target directory
            target_dir = os.path.dirname(target_path)
            if not dry_run and not os.path.exists(target_dir):
                os.makedirs(target_dir, exist_ok=True)
                self.stats['dirs_created'] += 1

            # Copy file
            try:
                if not os.path.exists(source_path):
                    logger.warning(f"Source file missing: {source_path}")
                    self.stats['errors'] += 1
                    continue

                if not dry_run:
                    shutil.copy2(source_path, target_path)

                # Update database with target path
                cursor.execute('''
                    UPDATE documents
                    SET target_path = ?, processed = 1
                    WHERE id = ?
                ''', (target_path, doc['id']))

                self.stats['files_copied'] += 1
                self.stats['bytes_copied'] += doc['file_size'] or 0

                # Progress logging
                if i % 100 == 0 or i == total:
                    logger.info(f"Progress: {i:,}/{total:,} ({i/total*100:.1f}%)")

            except Exception as e:
                logger.error(f"Error copying {source_path}: {e}")
                self.stats['errors'] += 1

        if not dry_run:
            self.conn.commit()

        self._print_summary()

    def _print_summary(self):
        """Print consolidation summary."""
        action = "Would copy" if self.dry_run else "Copied"
        size_gb = self.stats['bytes_copied'] / (1024 ** 3)

        print("\n" + "=" * 60)
        print("CONSOLIDATION " + ("DRY RUN " if self.dry_run else "") + "COMPLETE")
        print("=" * 60)
        print(f"{action}:          {self.stats['files_copied']:,} files")
        print(f"Total size:         {size_gb:.2f} GB")
        print(f"Directories:        {self.stats['dirs_created']:,}")
        print(f"Errors:             {self.stats['errors']:,}")
        print(f"Target:             {self.target_dir}")
        print("=" * 60)

    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()


def main():
    parser = argparse.ArgumentParser(
        description='Consolidate O&G standards to organized directory'
    )
    parser.add_argument(
        '--config', '-c',
        default='config.yaml',
        help='Path to configuration file (default: config.yaml)'
    )
    parser.add_argument(
        '--dry-run', '-n',
        action='store_true',
        help='Show what would be done without copying files'
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

    # Run consolidation
    consolidator = StandardsConsolidator(config_path)
    try:
        consolidator.connect()
        consolidator.consolidate(dry_run=args.dry_run)
    finally:
        consolidator.close()


if __name__ == '__main__':
    main()
