#!/usr/bin/env python3
"""
ABOUTME: O&G Standards Inventory Builder
ABOUTME: Scans directories and creates SQLite database with file metadata and content hashes

Usage:
    python inventory.py [--config config.yaml] [--force]
"""

import argparse
import hashlib
import logging
import os
import re
import sqlite3
import sys
from datetime import datetime
from fnmatch import fnmatch
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


class StandardsInventory:
    """Builds and manages inventory of O&G standards documents."""

    def __init__(self, config_path: str):
        """Initialize with configuration file."""
        self.config = self._load_config(config_path)
        self.db_path = self.config['database_path']
        self.conn = None
        self.stats = {
            'files_scanned': 0,
            'files_added': 0,
            'files_skipped': 0,
            'errors': 0,
            'total_size_bytes': 0,
        }

    def _load_config(self, config_path: str) -> dict:
        """Load configuration from YAML file."""
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)

    def _init_database(self, force: bool = False):
        """Initialize SQLite database schema."""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

        if force and os.path.exists(self.db_path):
            os.remove(self.db_path)
            logger.info(f"Removed existing database: {self.db_path}")

        self.conn = sqlite3.connect(self.db_path, timeout=30)
        cursor = self.conn.cursor()

        # Create main documents table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_path TEXT UNIQUE NOT NULL,
                filename TEXT NOT NULL,
                extension TEXT,
                file_size INTEGER,
                modified_date TEXT,
                content_hash TEXT,
                organization TEXT,
                doc_type TEXT,
                doc_number TEXT,
                title TEXT,
                source_dir TEXT,
                is_duplicate INTEGER DEFAULT 0,
                duplicate_of INTEGER,
                target_path TEXT,
                processed INTEGER DEFAULT 0,
                scan_date TEXT,
                FOREIGN KEY (duplicate_of) REFERENCES documents(id)
            )
        ''')

        # Create indexes for fast querying
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_content_hash ON documents(content_hash)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_organization ON documents(organization)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_is_duplicate ON documents(is_duplicate)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_filename ON documents(filename)')

        # Create scan history table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS scan_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                scan_date TEXT,
                source_dirs TEXT,
                files_scanned INTEGER,
                files_added INTEGER,
                total_size_bytes INTEGER,
                duration_seconds REAL
            )
        ''')

        self.conn.commit()
        logger.info(f"Database initialized: {self.db_path}")

    def _should_exclude(self, file_path: str) -> bool:
        """Check if file path matches any exclude patterns."""
        for pattern in self.config.get('exclude_patterns', []):
            if fnmatch(file_path, pattern):
                return True
        return False

    def _is_valid_extension(self, file_path: str) -> bool:
        """Check if file has valid extension for processing."""
        ext = os.path.splitext(file_path)[1].lower()
        return ext in self.config.get('file_extensions', ['.pdf'])

    def _compute_hash(self, file_path: str, chunk_size: int = 8192) -> Optional[str]:
        """Compute MD5 hash of file content."""
        try:
            hasher = hashlib.md5()
            with open(file_path, 'rb') as f:
                while chunk := f.read(chunk_size):
                    hasher.update(chunk)
            return hasher.hexdigest()
        except Exception as e:
            logger.warning(f"Failed to hash {file_path}: {e}")
            return None

    def _parse_standard_info(self, filename: str, file_path: str) -> Tuple[str, str, str]:
        """
        Parse organization, document type, and number from filename.

        Returns: (organization, doc_type, doc_number)
        """
        filename_upper = filename.upper()
        path_upper = file_path.upper()

        # Try to identify organization
        org = 'Unknown'
        doc_type = ''
        doc_number = ''

        org_mappings = self.config.get('organization_mappings', {})

        for org_name, org_config in org_mappings.items():
            patterns = org_config.get('patterns', [])
            for pattern in patterns:
                pattern_upper = pattern.upper().replace('*', '')
                if pattern_upper in filename_upper or pattern_upper in path_upper:
                    org = org_name
                    break
            if org != 'Unknown':
                break

        # Parse document type and number based on organization
        if org == 'API':
            # Match patterns like "API RP 2RD", "API Spec 6A", "API STD 650"
            match = re.search(r'API\s*(RP|Spec|STD|Bull|TR|MPMS|Publ)?\s*(\d+[A-Z]*)', filename_upper)
            if match:
                doc_type = match.group(1) or 'STD'
                doc_number = match.group(2)

        elif org == 'DNV':
            # Match patterns like "DNV-OS-F101", "DNV-RP-F105"
            match = re.search(r'DNV[-\s]*(OS|RP|CN|OSS|GL)[-\s]*([A-Z]?\d+)', filename_upper)
            if match:
                doc_type = match.group(1)
                doc_number = match.group(2)

        elif org == 'ASTM':
            # Match patterns like "ASTM A131", "ASTM D4294"
            match = re.search(r'ASTM\s*([A-G])[-\s]*(\d+)', filename_upper)
            if match:
                doc_type = match.group(1) + '-Series'
                doc_number = match.group(1) + match.group(2)

        elif org == 'ISO':
            # Match patterns like "ISO 13628-1", "ISO 15156"
            match = re.search(r'ISO\s*(\d+)(?:[-\s]*(\d+))?', filename_upper)
            if match:
                doc_number = match.group(1)
                if match.group(2):
                    doc_number += '-' + match.group(2)
                # Determine series
                if doc_number.startswith('13'):
                    doc_type = '13xxx'
                elif doc_number.startswith('14'):
                    doc_type = '14xxx'
                elif doc_number.startswith('15'):
                    doc_type = '15xxx'
                elif doc_number.startswith('19'):
                    doc_type = '19xxx'

        elif org == 'Norsok':
            # Match patterns like "NORSOK M-001"
            match = re.search(r'NORSOK\s*([A-Z])[-\s]*(\d+)', filename_upper)
            if match:
                doc_type = match.group(1) + '-Series'
                doc_number = match.group(1) + '-' + match.group(2)

        return org, doc_type, doc_number

    def _extract_title(self, filename: str) -> str:
        """Extract document title from filename (removing extension and cleanup)."""
        title = os.path.splitext(filename)[0]
        # Clean up common patterns
        title = re.sub(r'[-_]+', ' ', title)
        title = re.sub(r'\s+', ' ', title)
        return title.strip()

    def scan_directory(self, source_dir: str) -> int:
        """
        Scan a directory and add files to inventory.

        Returns: Number of files added
        """
        files_added = 0
        cursor = self.conn.cursor()
        scan_date = datetime.now().isoformat()

        logger.info(f"Scanning directory: {source_dir}")

        for root, dirs, files in os.walk(source_dir):
            for filename in files:
                file_path = os.path.join(root, filename)
                self.stats['files_scanned'] += 1

                # Skip excluded paths
                if self._should_exclude(file_path):
                    self.stats['files_skipped'] += 1
                    continue

                # Skip invalid extensions
                if not self._is_valid_extension(file_path):
                    self.stats['files_skipped'] += 1
                    continue

                try:
                    # Get file metadata
                    stat = os.stat(file_path)
                    file_size = stat.st_size
                    modified_date = datetime.fromtimestamp(stat.st_mtime).isoformat()

                    # Compute content hash
                    content_hash = self._compute_hash(file_path)
                    if not content_hash:
                        self.stats['errors'] += 1
                        continue

                    # Parse standard info
                    org, doc_type, doc_number = self._parse_standard_info(filename, file_path)
                    title = self._extract_title(filename)
                    extension = os.path.splitext(filename)[1].lower()

                    # Insert into database
                    cursor.execute('''
                        INSERT OR IGNORE INTO documents
                        (file_path, filename, extension, file_size, modified_date,
                         content_hash, organization, doc_type, doc_number, title,
                         source_dir, scan_date)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        file_path, filename, extension, file_size, modified_date,
                        content_hash, org, doc_type, doc_number, title,
                        source_dir, scan_date
                    ))

                    if cursor.rowcount > 0:
                        files_added += 1
                        self.stats['files_added'] += 1
                        self.stats['total_size_bytes'] += file_size

                except Exception as e:
                    logger.warning(f"Error processing {file_path}: {e}")
                    self.stats['errors'] += 1

                # Progress logging every 500 files
                if self.stats['files_scanned'] % 500 == 0:
                    logger.info(f"Progress: {self.stats['files_scanned']} files scanned, "
                               f"{self.stats['files_added']} added")

        self.conn.commit()
        return files_added

    def run_full_scan(self, force: bool = False):
        """Run full inventory scan on all configured source directories."""
        start_time = datetime.now()

        # Initialize database
        self._init_database(force=force)

        # Scan each source directory
        for source_dir in self.config['source_directories']:
            if os.path.exists(source_dir):
                self.scan_directory(source_dir)
            else:
                logger.warning(f"Source directory not found: {source_dir}")

        # Calculate duration
        duration = (datetime.now() - start_time).total_seconds()

        # Record scan history
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO scan_history
            (scan_date, source_dirs, files_scanned, files_added, total_size_bytes, duration_seconds)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            datetime.now().isoformat(),
            ','.join(self.config['source_directories']),
            self.stats['files_scanned'],
            self.stats['files_added'],
            self.stats['total_size_bytes'],
            duration
        ))
        self.conn.commit()

        # Print summary
        self._print_summary(duration)

    def _print_summary(self, duration: float):
        """Print scan summary statistics."""
        size_gb = self.stats['total_size_bytes'] / (1024 ** 3)

        print("\n" + "=" * 60)
        print("INVENTORY SCAN COMPLETE")
        print("=" * 60)
        print(f"Files scanned:     {self.stats['files_scanned']:,}")
        print(f"Files added:       {self.stats['files_added']:,}")
        print(f"Files skipped:     {self.stats['files_skipped']:,}")
        print(f"Errors:            {self.stats['errors']:,}")
        print(f"Total size:        {size_gb:.2f} GB")
        print(f"Duration:          {duration:.1f} seconds")
        print(f"Database:          {self.db_path}")
        print("=" * 60)

        # Show organization breakdown
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT organization, COUNT(*) as count
            FROM documents
            GROUP BY organization
            ORDER BY count DESC
        ''')

        print("\nFiles by Organization:")
        print("-" * 40)
        for row in cursor.fetchall():
            print(f"  {row[0]:<20} {row[1]:>8,}")

    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()


def main():
    parser = argparse.ArgumentParser(
        description='Build inventory of O&G standards documents'
    )
    parser.add_argument(
        '--config', '-c',
        default='config.yaml',
        help='Path to configuration file (default: config.yaml)'
    )
    parser.add_argument(
        '--force', '-f',
        action='store_true',
        help='Force rebuild of database (removes existing)'
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

    # Run inventory
    inventory = StandardsInventory(config_path)
    try:
        inventory.run_full_scan(force=args.force)
    finally:
        inventory.close()


if __name__ == '__main__':
    main()
