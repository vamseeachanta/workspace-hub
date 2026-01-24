#!/usr/bin/env python3
"""
ABOUTME: O&G Standards Catalog Generator
ABOUTME: Generates searchable JSON and HTML catalogs for integration with workspace-hub

Usage:
    python catalog.py [--config config.yaml] [--format json|html|both]

Output:
    - _catalog.json: Machine-readable catalog for AI/search integration
    - _catalog.html: Interactive HTML browser
    - Full-text search index in SQLite database
"""

import argparse
import json
import logging
import os
import sqlite3
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import yaml

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


class CatalogGenerator:
    """Generates searchable catalogs for O&G standards."""

    def __init__(self, config_path: str):
        """Initialize with configuration file."""
        self.config = self._load_config(config_path)
        self.db_path = self.config['database_path']
        self.target_dir = self.config['target_directory']
        self.conn = None

    def _load_config(self, config_path: str) -> dict:
        """Load configuration from YAML file."""
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)

    def connect(self):
        """Connect to database."""
        if not os.path.exists(self.db_path):
            logger.error(f"Database not found: {self.db_path}")
            logger.error("Run inventory.py first")
            sys.exit(1)

        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row

    def _build_fts_index(self):
        """Build full-text search index for fast querying."""
        cursor = self.conn.cursor()

        # Create FTS5 virtual table if not exists
        cursor.execute('''
            CREATE VIRTUAL TABLE IF NOT EXISTS documents_fts USING fts5(
                filename, title, organization, doc_type, doc_number,
                content='documents',
                content_rowid='id'
            )
        ''')

        # Populate FTS index
        cursor.execute('''
            INSERT OR REPLACE INTO documents_fts(rowid, filename, title, organization, doc_type, doc_number)
            SELECT id, filename, title, organization, doc_type, doc_number
            FROM documents
            WHERE is_duplicate = 0
        ''')

        self.conn.commit()
        logger.info("Full-text search index created")

    def generate_json_catalog(self) -> str:
        """
        Generate comprehensive JSON catalog.

        Returns: Path to generated JSON file
        """
        cursor = self.conn.cursor()

        # Get all unique documents
        cursor.execute('''
            SELECT id, file_path, filename, extension, file_size, modified_date,
                   content_hash, organization, doc_type, doc_number, title,
                   target_path
            FROM documents
            WHERE is_duplicate = 0
            ORDER BY organization, doc_type, doc_number, filename
        ''')

        documents = []
        for row in cursor.fetchall():
            doc = dict(row)
            # Convert to relative path from target directory
            if doc['target_path']:
                doc['relative_path'] = os.path.relpath(
                    doc['target_path'],
                    self.target_dir
                )
            documents.append(doc)

        # Build catalog structure
        catalog = {
            'metadata': {
                'generated': datetime.now().isoformat(),
                'total_documents': len(documents),
                'version': '1.0.0',
                'source': 'O&G Standards Consolidation System',
                'target_directory': self.target_dir,
            },
            'statistics': self._get_statistics(),
            'organizations': self._get_organization_index(),
            'documents': documents,
        }

        # Write JSON
        output_path = self.config.get('catalog_json',
                                       os.path.join(self.target_dir, '_catalog.json'))
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        with open(output_path, 'w') as f:
            json.dump(catalog, f, indent=2, default=str)

        logger.info(f"JSON catalog generated: {output_path}")
        return output_path

    def _get_statistics(self) -> dict:
        """Get catalog statistics."""
        cursor = self.conn.cursor()

        stats = {}

        # Total unique documents
        cursor.execute('SELECT COUNT(*) FROM documents WHERE is_duplicate = 0')
        stats['unique_documents'] = cursor.fetchone()[0]

        # Total with duplicates
        cursor.execute('SELECT COUNT(*) FROM documents')
        stats['total_scanned'] = cursor.fetchone()[0]

        # Total size
        cursor.execute('SELECT SUM(file_size) FROM documents WHERE is_duplicate = 0')
        total_bytes = cursor.fetchone()[0] or 0
        stats['total_size_bytes'] = total_bytes
        stats['total_size_gb'] = round(total_bytes / (1024**3), 2)

        # By organization
        cursor.execute('''
            SELECT organization, COUNT(*) as count
            FROM documents
            WHERE is_duplicate = 0
            GROUP BY organization
            ORDER BY count DESC
        ''')
        stats['by_organization'] = {row[0]: row[1] for row in cursor.fetchall()}

        # By extension
        cursor.execute('''
            SELECT extension, COUNT(*) as count
            FROM documents
            WHERE is_duplicate = 0
            GROUP BY extension
            ORDER BY count DESC
        ''')
        stats['by_extension'] = {row[0]: row[1] for row in cursor.fetchall()}

        return stats

    def _get_organization_index(self) -> dict:
        """Get hierarchical index by organization."""
        cursor = self.conn.cursor()

        cursor.execute('''
            SELECT organization, doc_type, COUNT(*) as count
            FROM documents
            WHERE is_duplicate = 0
            GROUP BY organization, doc_type
            ORDER BY organization, doc_type
        ''')

        index = defaultdict(lambda: defaultdict(int))
        for org, doc_type, count in cursor.fetchall():
            index[org][doc_type or 'General'] = count

        return dict(index)

    def generate_html_catalog(self) -> str:
        """
        Generate interactive HTML catalog with search and filtering.

        Returns: Path to generated HTML file
        """
        cursor = self.conn.cursor()
        stats = self._get_statistics()

        # Get all documents
        cursor.execute('''
            SELECT id, filename, extension, file_size, organization,
                   doc_type, doc_number, title, target_path
            FROM documents
            WHERE is_duplicate = 0
            ORDER BY organization, doc_type, filename
        ''')

        documents = [dict(row) for row in cursor.fetchall()]

        html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>O&G Standards Catalog</title>
    <style>
        :root {{
            --primary: #1a365d;
            --primary-light: #2c5282;
            --success: #38a169;
            --bg: #f7fafc;
            --card-bg: #ffffff;
            --border: #e2e8f0;
            --text: #2d3748;
            --text-muted: #718096;
        }}

        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: var(--bg);
            color: var(--text);
            line-height: 1.6;
        }}

        .container {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }}

        .header {{
            background: linear-gradient(135deg, var(--primary) 0%, var(--primary-light) 100%);
            color: white;
            padding: 40px 20px;
            margin-bottom: 30px;
        }}

        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
        }}

        .header p {{
            opacity: 0.9;
        }}

        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}

        .stat-card {{
            background: var(--card-bg);
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
            text-align: center;
        }}

        .stat-value {{
            font-size: 2.2em;
            font-weight: 700;
            color: var(--primary);
        }}

        .stat-label {{
            color: var(--text-muted);
            font-size: 0.9em;
            margin-top: 5px;
        }}

        .search-section {{
            background: var(--card-bg);
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
            margin-bottom: 30px;
        }}

        .search-row {{
            display: flex;
            gap: 15px;
            flex-wrap: wrap;
        }}

        .search-input {{
            flex: 1;
            min-width: 200px;
            padding: 12px 16px;
            border: 2px solid var(--border);
            border-radius: 8px;
            font-size: 1em;
            transition: border-color 0.2s;
        }}

        .search-input:focus {{
            outline: none;
            border-color: var(--primary);
        }}

        .filter-select {{
            padding: 12px 16px;
            border: 2px solid var(--border);
            border-radius: 8px;
            font-size: 1em;
            background: white;
            cursor: pointer;
        }}

        .results-info {{
            padding: 10px 0;
            color: var(--text-muted);
        }}

        .catalog-table {{
            width: 100%;
            background: var(--card-bg);
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        }}

        .catalog-table th,
        .catalog-table td {{
            padding: 14px 16px;
            text-align: left;
            border-bottom: 1px solid var(--border);
        }}

        .catalog-table th {{
            background: var(--primary);
            color: white;
            font-weight: 600;
            cursor: pointer;
            user-select: none;
        }}

        .catalog-table th:hover {{
            background: var(--primary-light);
        }}

        .catalog-table tr:hover {{
            background: #f8fafc;
        }}

        .org-badge {{
            display: inline-block;
            padding: 4px 10px;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: 600;
            background: var(--primary);
            color: white;
        }}

        .org-badge.api {{ background: #e53e3e; }}
        .org-badge.dnv {{ background: #38a169; }}
        .org-badge.astm {{ background: #3182ce; }}
        .org-badge.iso {{ background: #805ad5; }}
        .org-badge.norsok {{ background: #dd6b20; }}
        .org-badge.bsi {{ background: #319795; }}

        .file-link {{
            color: var(--primary);
            text-decoration: none;
            font-family: monospace;
            font-size: 0.9em;
        }}

        .file-link:hover {{
            text-decoration: underline;
        }}

        .size-cell {{
            font-family: monospace;
            color: var(--text-muted);
        }}

        .pagination {{
            display: flex;
            justify-content: center;
            gap: 10px;
            margin-top: 30px;
        }}

        .page-btn {{
            padding: 10px 16px;
            border: 2px solid var(--border);
            border-radius: 8px;
            background: white;
            cursor: pointer;
            transition: all 0.2s;
        }}

        .page-btn:hover {{
            border-color: var(--primary);
            color: var(--primary);
        }}

        .page-btn.active {{
            background: var(--primary);
            color: white;
            border-color: var(--primary);
        }}

        .footer {{
            text-align: center;
            padding: 30px;
            color: var(--text-muted);
            font-size: 0.9em;
        }}

        @media (max-width: 768px) {{
            .catalog-table {{
                display: block;
                overflow-x: auto;
            }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <div class="container">
            <h1>O&G Standards Catalog</h1>
            <p>Consolidated reference library for Oil & Gas industry standards</p>
            <p style="opacity: 0.7; font-size: 0.9em;">Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
        </div>
    </div>

    <div class="container">
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-value">{stats['unique_documents']:,}</div>
                <div class="stat-label">Documents</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{stats['total_size_gb']}</div>
                <div class="stat-label">GB Total</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{len(stats['by_organization'])}</div>
                <div class="stat-label">Organizations</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{stats['by_organization'].get('API', 0):,}</div>
                <div class="stat-label">API Standards</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{stats['by_organization'].get('DNV', 0):,}</div>
                <div class="stat-label">DNV Standards</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{stats['by_organization'].get('ISO', 0):,}</div>
                <div class="stat-label">ISO Standards</div>
            </div>
        </div>

        <div class="search-section">
            <div class="search-row">
                <input type="text" id="searchInput" class="search-input"
                       placeholder="Search by filename, title, or document number..."
                       onkeyup="filterTable()">
                <select id="orgFilter" class="filter-select" onchange="filterTable()">
                    <option value="">All Organizations</option>
'''

        # Add organization options
        for org in sorted(stats['by_organization'].keys()):
            html += f'                    <option value="{org}">{org} ({stats["by_organization"][org]:,})</option>\n'

        html += '''                </select>
            </div>
            <div class="results-info">
                <span id="resultsCount">Showing all documents</span>
            </div>
        </div>

        <table class="catalog-table" id="catalogTable">
            <thead>
                <tr>
                    <th onclick="sortTable(0)">Organization</th>
                    <th onclick="sortTable(1)">Document Number</th>
                    <th onclick="sortTable(2)">Title / Filename</th>
                    <th onclick="sortTable(3)">Type</th>
                    <th onclick="sortTable(4)">Size</th>
                </tr>
            </thead>
            <tbody id="tableBody">
'''

        # Add document rows
        for doc in documents:
            org = doc['organization'] or 'Unknown'
            org_class = org.lower().replace(' ', '-')
            doc_num = doc['doc_number'] or ''
            title = doc['title'] or doc['filename']
            doc_type = doc['doc_type'] or ''
            size_mb = (doc['file_size'] or 0) / (1024 * 1024)

            # Create file link (relative path)
            rel_path = ''
            if doc['target_path']:
                rel_path = os.path.relpath(doc['target_path'], self.target_dir)

            html += f'''                <tr>
                    <td><span class="org-badge {org_class}">{org}</span></td>
                    <td>{doc_num}</td>
                    <td><a href="{rel_path}" class="file-link" title="{doc['filename']}">{title[:60]}{'...' if len(title) > 60 else ''}</a></td>
                    <td>{doc_type}</td>
                    <td class="size-cell">{size_mb:.1f} MB</td>
                </tr>
'''

        html += '''            </tbody>
        </table>

        <div class="footer">
            <p>O&G Standards Catalog - Part of workspace-hub knowledge management</p>
            <p>Use JSON catalog (_catalog.json) for programmatic access</p>
        </div>
    </div>

    <script>
        function filterTable() {
            const searchTerm = document.getElementById('searchInput').value.toLowerCase();
            const orgFilter = document.getElementById('orgFilter').value.toLowerCase();
            const rows = document.querySelectorAll('#tableBody tr');
            let visibleCount = 0;

            rows.forEach(row => {
                const text = row.textContent.toLowerCase();
                const org = row.querySelector('.org-badge')?.textContent.toLowerCase() || '';

                const matchesSearch = text.includes(searchTerm);
                const matchesOrg = !orgFilter || org === orgFilter;

                if (matchesSearch && matchesOrg) {
                    row.style.display = '';
                    visibleCount++;
                } else {
                    row.style.display = 'none';
                }
            });

            document.getElementById('resultsCount').textContent =
                `Showing ${visibleCount.toLocaleString()} of ${rows.length.toLocaleString()} documents`;
        }

        function sortTable(columnIndex) {
            const table = document.getElementById('catalogTable');
            const tbody = document.getElementById('tableBody');
            const rows = Array.from(tbody.querySelectorAll('tr'));

            const sortedRows = rows.sort((a, b) => {
                const aText = a.cells[columnIndex].textContent.trim();
                const bText = b.cells[columnIndex].textContent.trim();

                if (columnIndex === 4) {
                    // Size column - numeric sort
                    return parseFloat(aText) - parseFloat(bText);
                }
                return aText.localeCompare(bText);
            });

            // Toggle sort direction
            if (table.dataset.sortColumn === String(columnIndex) &&
                table.dataset.sortDir === 'asc') {
                sortedRows.reverse();
                table.dataset.sortDir = 'desc';
            } else {
                table.dataset.sortColumn = columnIndex;
                table.dataset.sortDir = 'asc';
            }

            tbody.innerHTML = '';
            sortedRows.forEach(row => tbody.appendChild(row));
        }
    </script>
</body>
</html>
'''

        # Write HTML
        output_path = self.config.get('catalog_html',
                                       os.path.join(self.target_dir, '_catalog.html'))
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        with open(output_path, 'w') as f:
            f.write(html)

        logger.info(f"HTML catalog generated: {output_path}")
        return output_path

    def run(self, format: str = 'both'):
        """
        Generate catalog(s).

        Args:
            format: 'json', 'html', or 'both'
        """
        self.connect()

        # Build FTS index
        self._build_fts_index()

        if format in ('json', 'both'):
            self.generate_json_catalog()

        if format in ('html', 'both'):
            self.generate_html_catalog()

        print("\n" + "=" * 60)
        print("CATALOG GENERATION COMPLETE")
        print("=" * 60)
        print(f"Target directory: {self.target_dir}")
        print("\nGenerated files:")
        if format in ('json', 'both'):
            print(f"  - _catalog.json (machine-readable)")
        if format in ('html', 'both'):
            print(f"  - _catalog.html (interactive browser)")
        print("\nFull-text search index available in database")
        print("=" * 60)

    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()


def main():
    parser = argparse.ArgumentParser(
        description='Generate O&G standards catalog'
    )
    parser.add_argument(
        '--config', '-c',
        default='config.yaml',
        help='Path to configuration file (default: config.yaml)'
    )
    parser.add_argument(
        '--format', '-f',
        choices=['json', 'html', 'both'],
        default='both',
        help='Output format (default: both)'
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

    # Generate catalog
    generator = CatalogGenerator(config_path)
    try:
        generator.run(format=args.format)
    finally:
        generator.close()


if __name__ == '__main__':
    main()
