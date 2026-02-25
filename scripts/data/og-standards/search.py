#!/usr/bin/env python3
"""
ABOUTME: O&G Standards Search CLI Tool
ABOUTME: Provides fast command-line search across consolidated standards library

Usage:
    python search.py "API RP 2RD"           # Basic search
    python search.py --org API "riser"      # Filter by organization
    python search.py --type RP "design"     # Filter by document type
    python search.py --list-orgs            # List all organizations
    python search.py --stats                # Show database statistics
"""

import argparse
import os
import re
import sqlite3
import sys
from pathlib import Path
from typing import List, Optional, Tuple

import yaml


class StandardsSearch:
    """Search interface for O&G standards database."""

    def __init__(self, db_path: str):
        """Initialize search with database path."""
        self.db_path = db_path
        self.conn = None

    def connect(self):
        """Connect to database."""
        if not os.path.exists(self.db_path):
            print(f"Error: Database not found: {self.db_path}")
            print("Run the consolidation pipeline first.")
            sys.exit(1)

        self.conn = sqlite3.connect(self.db_path, timeout=30)
        self.conn.row_factory = sqlite3.Row

    def search_fts(self, query: str, org: str = None, doc_type: str = None,
                   limit: int = 25) -> List[dict]:
        """
        Full-text search using FTS5 index.

        Args:
            query: Search query (supports FTS5 syntax)
            org: Filter by organization
            doc_type: Filter by document type
            limit: Maximum results to return

        Returns:
            List of matching documents
        """
        cursor = self.conn.cursor()

        # Check if FTS table exists
        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='documents_fts'
        """)

        if cursor.fetchone():
            # Use FTS5 search
            sql = '''
                SELECT d.id, d.filename, d.organization, d.doc_type,
                       d.doc_number, d.title, d.file_size, d.target_path
                FROM documents_fts fts
                JOIN documents d ON fts.rowid = d.id
                WHERE documents_fts MATCH ?
            '''
            params = [query]
        else:
            # Fall back to LIKE search
            sql = '''
                SELECT id, filename, organization, doc_type,
                       doc_number, title, file_size, target_path
                FROM documents
                WHERE (filename LIKE ? OR title LIKE ?)
                  AND is_duplicate = 0
            '''
            like_query = f'%{query}%'
            params = [like_query, like_query]

        # Add filters
        if org:
            sql += ' AND d.organization = ?' if 'JOIN' in sql else ' AND organization = ?'
            params.append(org)

        if doc_type:
            sql += ' AND d.doc_type LIKE ?' if 'JOIN' in sql else ' AND doc_type LIKE ?'
            params.append(f'%{doc_type}%')

        sql += f' LIMIT {limit}'

        cursor.execute(sql, params)
        return [dict(row) for row in cursor.fetchall()]

    def search_standard_number(self, standard: str) -> List[dict]:
        """
        Search by standard number (e.g., "API RP 2RD", "DNV-OS-F101").

        Args:
            standard: Standard identifier

        Returns:
            List of matching documents
        """
        cursor = self.conn.cursor()

        # Parse standard number into components
        standard_upper = standard.upper().strip()

        # Try to parse structured standard number (e.g., "DNV-OS-F101", "API RP 2RD")
        # Pattern: ORG[-\s]TYPE[-\s]NUMBER
        match = re.match(
            r'^(API|DNV|ASTM|ISO|NORSOK|BSI|MIL)[-\s]*(RP|OS|STD|SPEC|TR|CN|ST)?[-\s]*([A-Z0-9]+)$',
            standard_upper
        )

        if match:
            org, doc_type, doc_num = match.groups()
            doc_type = doc_type or ''

            # Build query with parsed components
            sql = '''
                SELECT id, filename, organization, doc_type,
                       doc_number, title, file_size, target_path
                FROM documents
                WHERE organization = ?
                  AND doc_number LIKE ?
                  AND is_duplicate = 0
            '''
            params = [org, f'%{doc_num}%']

            if doc_type:
                sql += ' AND doc_type LIKE ?'
                params.append(f'%{doc_type}%')

            sql += ' ORDER BY modified_date DESC LIMIT 25'
            cursor.execute(sql, params)
            results = [dict(row) for row in cursor.fetchall()]

            if results:
                return results

        # Fallback: Try doc_number match
        cursor.execute('''
            SELECT id, filename, organization, doc_type,
                   doc_number, title, file_size, target_path
            FROM documents
            WHERE doc_number LIKE ?
              AND is_duplicate = 0
            ORDER BY modified_date DESC
            LIMIT 25
        ''', (f'%{standard_upper}%',))

        results = [dict(row) for row in cursor.fetchall()]

        if not results:
            # Try filename search with normalized pattern
            # Convert "DNV-OS-F101" to pattern matching "DNV*OS*F101"
            search_pattern = '%' + '%'.join(standard_upper.replace('-', ' ').split()) + '%'
            cursor.execute('''
                SELECT id, filename, organization, doc_type,
                       doc_number, title, file_size, target_path
                FROM documents
                WHERE UPPER(filename) LIKE ?
                  AND is_duplicate = 0
                ORDER BY modified_date DESC
                LIMIT 25
            ''', (search_pattern,))
            results = [dict(row) for row in cursor.fetchall()]

        return results

    def list_organizations(self) -> List[Tuple[str, int]]:
        """List all organizations with document counts."""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT organization, COUNT(*) as count
            FROM documents
            WHERE is_duplicate = 0
            GROUP BY organization
            ORDER BY count DESC
        ''')
        return cursor.fetchall()

    def list_doc_types(self, org: str = None) -> List[Tuple[str, int]]:
        """List document types with counts."""
        cursor = self.conn.cursor()

        sql = '''
            SELECT doc_type, COUNT(*) as count
            FROM documents
            WHERE is_duplicate = 0
              AND doc_type IS NOT NULL
              AND doc_type != ''
        '''

        params = []
        if org:
            sql += ' AND organization = ?'
            params.append(org)

        sql += ' GROUP BY doc_type ORDER BY count DESC'

        cursor.execute(sql, params)
        return cursor.fetchall()

    def get_stats(self) -> dict:
        """Get database statistics."""
        cursor = self.conn.cursor()

        stats = {}

        # Total documents
        cursor.execute('SELECT COUNT(*) FROM documents WHERE is_duplicate = 0')
        stats['total_documents'] = cursor.fetchone()[0]

        # Total size
        cursor.execute('SELECT SUM(file_size) FROM documents WHERE is_duplicate = 0')
        stats['total_size_bytes'] = cursor.fetchone()[0] or 0

        # Organizations
        cursor.execute('SELECT COUNT(DISTINCT organization) FROM documents')
        stats['organizations'] = cursor.fetchone()[0]

        # Document types
        cursor.execute("SELECT COUNT(DISTINCT doc_type) FROM documents WHERE doc_type != ''")
        stats['doc_types'] = cursor.fetchone()[0]

        # Duplicates removed
        cursor.execute('SELECT COUNT(*) FROM documents WHERE is_duplicate = 1')
        stats['duplicates_removed'] = cursor.fetchone()[0]

        return stats

    def get_recent(self, limit: int = 10) -> List[dict]:
        """Get recently modified documents."""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT id, filename, organization, doc_type,
                   doc_number, title, file_size, target_path, modified_date
            FROM documents
            WHERE is_duplicate = 0
            ORDER BY modified_date DESC
            LIMIT ?
        ''', (limit,))
        return [dict(row) for row in cursor.fetchall()]

    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()


def format_size(size_bytes: int) -> str:
    """Format file size for display."""
    if size_bytes is None:
        return "Unknown"
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"


def print_results(results: List[dict], verbose: bool = False):
    """Print search results in formatted table."""
    if not results:
        print("No results found.")
        return

    print(f"\nFound {len(results)} result(s):\n")
    print("-" * 100)

    for i, doc in enumerate(results, 1):
        org = doc.get('organization', 'Unknown')
        doc_type = doc.get('doc_type', '')
        doc_num = doc.get('doc_number', '')
        filename = doc.get('filename', '')
        size = format_size(doc.get('file_size'))

        # Build standard reference
        ref = f"{org}"
        if doc_type:
            ref += f" {doc_type}"
        if doc_num:
            ref += f" {doc_num}"

        print(f"{i:2}. [{org:<8}] {filename[:60]:<60} ({size})")

        if verbose and doc.get('target_path'):
            print(f"    Path: {doc['target_path']}")

    print("-" * 100)


def print_stats(stats: dict):
    """Print database statistics."""
    size_gb = stats['total_size_bytes'] / (1024 ** 3)

    print("\n" + "=" * 50)
    print("O&G STANDARDS DATABASE STATISTICS")
    print("=" * 50)
    print(f"Total Documents:    {stats['total_documents']:,}")
    print(f"Total Size:         {size_gb:.2f} GB")
    print(f"Organizations:      {stats['organizations']}")
    print(f"Document Types:     {stats['doc_types']}")
    print(f"Duplicates Removed: {stats['duplicates_removed']:,}")
    print("=" * 50)


def print_organizations(orgs: List[Tuple[str, int]]):
    """Print organization list."""
    print("\n" + "=" * 40)
    print("ORGANIZATIONS")
    print("=" * 40)
    for org, count in orgs:
        print(f"  {org:<20} {count:>8,} documents")
    print("=" * 40)


def print_doc_types(types: List[Tuple[str, int]], org: str = None):
    """Print document type list."""
    header = f"DOCUMENT TYPES" + (f" ({org})" if org else "")
    print("\n" + "=" * 40)
    print(header)
    print("=" * 40)
    for doc_type, count in types:
        if doc_type:
            print(f"  {doc_type:<20} {count:>8,} documents")
    print("=" * 40)


def main():
    parser = argparse.ArgumentParser(
        description='Search O&G Standards Database',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s "API RP 2RD"              Search for API RP 2RD
  %(prog)s "riser design"            Full-text search
  %(prog)s --org DNV "fatigue"       Search DNV docs for fatigue
  %(prog)s --type RP "subsea"        Search Recommended Practices
  %(prog)s --list-orgs               List all organizations
  %(prog)s --list-types              List all document types
  %(prog)s --list-types --org API    List API document types
  %(prog)s --stats                   Show database statistics
  %(prog)s --recent                  Show recently modified docs
        """
    )

    parser.add_argument(
        'query',
        nargs='?',
        help='Search query'
    )
    parser.add_argument(
        '--org', '-o',
        help='Filter by organization (API, DNV, ASTM, ISO, etc.)'
    )
    parser.add_argument(
        '--type', '-t',
        help='Filter by document type (RP, Spec, STD, OS, etc.)'
    )
    parser.add_argument(
        '--limit', '-n',
        type=int,
        default=25,
        help='Maximum results (default: 25)'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Show full file paths'
    )
    parser.add_argument(
        '--list-orgs',
        action='store_true',
        help='List all organizations'
    )
    parser.add_argument(
        '--list-types',
        action='store_true',
        help='List document types'
    )
    parser.add_argument(
        '--stats',
        action='store_true',
        help='Show database statistics'
    )
    parser.add_argument(
        '--recent',
        action='store_true',
        help='Show recently modified documents'
    )
    parser.add_argument(
        '--config', '-c',
        default='config.yaml',
        help='Path to configuration file'
    )
    parser.add_argument(
        '--db',
        help='Direct path to database file'
    )

    args = parser.parse_args()

    # Find database path
    if args.db:
        db_path = args.db
    else:
        config_path = args.config
        if not os.path.isabs(config_path):
            script_dir = os.path.dirname(os.path.abspath(__file__))
            config_path = os.path.join(script_dir, config_path)

        if os.path.exists(config_path):
            with open(config_path) as f:
                config = yaml.safe_load(f)
            db_path = config['database_path']
        else:
            # Default path
            db_path = '/mnt/ace/O&G-Standards/_inventory.db'

    # Create search instance
    search = StandardsSearch(db_path)

    try:
        search.connect()

        # Handle different modes
        if args.stats:
            stats = search.get_stats()
            print_stats(stats)

        elif args.list_orgs:
            orgs = search.list_organizations()
            print_organizations(orgs)

        elif args.list_types:
            types = search.list_doc_types(args.org)
            print_doc_types(types, args.org)

        elif args.recent:
            results = search.get_recent(args.limit)
            print("\nRecently Modified Documents:")
            print_results(results, args.verbose)

        elif args.query:
            # Determine search type
            query_upper = args.query.upper().strip()

            # Check if query looks like a pure standard number (e.g., "API RP 2RD", "DNV-OS-F101")
            # Pattern: ORG + optional type code + number (must contain at least one digit)
            is_standard_number = re.match(
                r'^(API|DNV|ASTM|ISO|NORSOK|BSI|MIL)[-\s]*(RP|OS|STD|SPEC|TR|CN|ST)?[-\s]*([A-Z]*\d+[A-Z0-9]*|F\d+|\d+[A-Z]*)$',
                query_upper
            )

            if is_standard_number and len(query_upper.split()) <= 3:
                # Pure standard number search (e.g., "API RP 2RD", "DNV-OS-F101")
                results = search.search_standard_number(args.query)
            else:
                # Check if query starts with org name - extract it as filter
                org_match = re.match(r'^(API|DNV|ASTM|ISO|NORSOK|BSI|MIL)\s+(.+)$', query_upper)
                if org_match and not args.org:
                    # Extract org and use remaining as query
                    extracted_org = org_match.group(1)
                    remaining_query = org_match.group(2)
                    results = search.search_fts(
                        remaining_query,
                        org=extracted_org,
                        doc_type=args.type,
                        limit=args.limit
                    )
                else:
                    # Standard FTS search
                    results = search.search_fts(
                        args.query,
                        org=args.org,
                        doc_type=args.type,
                        limit=args.limit
                    )

            print_results(results, args.verbose)

        else:
            parser.print_help()

    finally:
        search.close()


if __name__ == '__main__':
    main()
