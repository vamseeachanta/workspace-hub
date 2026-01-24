#!/usr/bin/env python3
"""
ABOUTME: O&G Standards Duplicate Detection
ABOUTME: Identifies duplicate files by content hash and marks them in database

Usage:
    python dedup.py [--config config.yaml] [--report report.html]
"""

import argparse
import logging
import os
import sqlite3
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

import yaml

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


class DuplicateDetector:
    """Detects and reports duplicate documents in the inventory."""

    def __init__(self, config_path: str):
        """Initialize with configuration file."""
        self.config = self._load_config(config_path)
        self.db_path = self.config['database_path']
        self.conn = None
        self.stats = {
            'total_files': 0,
            'unique_files': 0,
            'duplicate_groups': 0,
            'total_duplicates': 0,
            'space_wasted_bytes': 0,
        }

    def _load_config(self, config_path: str) -> dict:
        """Load configuration from YAML file."""
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)

    def connect(self):
        """Connect to database."""
        if not os.path.exists(self.db_path):
            logger.error(f"Database not found: {self.db_path}")
            logger.error("Run inventory.py first to build the database")
            sys.exit(1)

        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row

    def find_duplicates(self) -> Dict[str, List[dict]]:
        """
        Find all duplicate files by content hash.

        Returns: Dictionary mapping content_hash to list of file records
        """
        cursor = self.conn.cursor()

        # Find hashes with multiple files
        cursor.execute('''
            SELECT content_hash, COUNT(*) as count
            FROM documents
            WHERE content_hash IS NOT NULL
            GROUP BY content_hash
            HAVING count > 1
            ORDER BY count DESC
        ''')

        duplicate_hashes = cursor.fetchall()
        logger.info(f"Found {len(duplicate_hashes)} groups of duplicate files")

        duplicates = {}
        for row in duplicate_hashes:
            content_hash = row['content_hash']
            cursor.execute('''
                SELECT id, file_path, filename, file_size, modified_date,
                       organization, doc_type, doc_number, source_dir
                FROM documents
                WHERE content_hash = ?
                ORDER BY modified_date DESC
            ''', (content_hash,))

            files = [dict(r) for r in cursor.fetchall()]
            duplicates[content_hash] = files

        return duplicates

    def select_best_version(self, files: List[dict]) -> dict:
        """
        Select the best version from a group of duplicate files.

        Strategy from config: newest, largest, or first_found
        """
        strategy = self.config.get('duplicate_strategy', {}).get('prefer', 'newest')

        if strategy == 'newest':
            # Sort by modified date descending, pick first
            sorted_files = sorted(files, key=lambda x: x['modified_date'] or '', reverse=True)
        elif strategy == 'largest':
            # Sort by file size descending
            sorted_files = sorted(files, key=lambda x: x['file_size'] or 0, reverse=True)
        else:  # first_found
            sorted_files = files

        return sorted_files[0]

    def mark_duplicates(self, duplicates: Dict[str, List[dict]]):
        """Mark duplicate files in database, keeping the best version as original."""
        cursor = self.conn.cursor()

        for content_hash, files in duplicates.items():
            if len(files) < 2:
                continue

            # Select best version
            best = self.select_best_version(files)
            best_id = best['id']

            self.stats['duplicate_groups'] += 1
            self.stats['unique_files'] += 1

            # Mark all others as duplicates
            for f in files:
                if f['id'] != best_id:
                    cursor.execute('''
                        UPDATE documents
                        SET is_duplicate = 1, duplicate_of = ?
                        WHERE id = ?
                    ''', (best_id, f['id']))

                    self.stats['total_duplicates'] += 1
                    self.stats['space_wasted_bytes'] += f['file_size'] or 0
                else:
                    # Mark the best as not duplicate
                    cursor.execute('''
                        UPDATE documents
                        SET is_duplicate = 0, duplicate_of = NULL
                        WHERE id = ?
                    ''', (f['id'],))

        self.conn.commit()

    def generate_report(self, duplicates: Dict[str, List[dict]], output_path: str):
        """Generate HTML report of duplicate files."""
        cursor = self.conn.cursor()

        # Get total stats
        cursor.execute('SELECT COUNT(*) FROM documents')
        self.stats['total_files'] = cursor.fetchone()[0]

        cursor.execute('SELECT COUNT(*) FROM documents WHERE is_duplicate = 0')
        unique_count = cursor.fetchone()[0]

        # Generate HTML
        html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>O&G Standards Duplicate Report</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
        }}
        .header {{
            background: linear-gradient(135deg, #1a365d 0%, #2c5282 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .stat-card {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .stat-value {{
            font-size: 2em;
            font-weight: bold;
            color: #2c5282;
        }}
        .stat-label {{
            color: #666;
            margin-top: 5px;
        }}
        .savings {{
            color: #38a169;
        }}
        .duplicate-group {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 15px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .group-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 1px solid #eee;
        }}
        .file-list {{
            list-style: none;
            padding: 0;
            margin: 0;
        }}
        .file-item {{
            padding: 10px;
            margin: 5px 0;
            background: #f8f9fa;
            border-radius: 5px;
            font-family: monospace;
            font-size: 0.85em;
            display: flex;
            justify-content: space-between;
        }}
        .file-item.original {{
            background: #c6f6d5;
            border-left: 4px solid #38a169;
        }}
        .file-item.duplicate {{
            background: #fed7d7;
            border-left: 4px solid #e53e3e;
        }}
        .badge {{
            display: inline-block;
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 0.8em;
            font-weight: bold;
        }}
        .badge-keep {{
            background: #38a169;
            color: white;
        }}
        .badge-duplicate {{
            background: #e53e3e;
            color: white;
        }}
        .org-badge {{
            background: #2c5282;
            color: white;
        }}
        .summary {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 30px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
        }}
        th, td {{
            text-align: left;
            padding: 10px;
            border-bottom: 1px solid #eee;
        }}
        th {{
            background: #f8f9fa;
        }}
        .file-path {{
            word-break: break-all;
            max-width: 600px;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>O&G Standards Duplicate Report</h1>
        <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>

    <div class="stats-grid">
        <div class="stat-card">
            <div class="stat-value">{self.stats['total_files']:,}</div>
            <div class="stat-label">Total Files</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">{unique_count:,}</div>
            <div class="stat-label">Unique Files</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">{self.stats['total_duplicates']:,}</div>
            <div class="stat-label">Duplicate Files</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">{self.stats['duplicate_groups']:,}</div>
            <div class="stat-label">Duplicate Groups</div>
        </div>
        <div class="stat-card">
            <div class="stat-value savings">{self.stats['space_wasted_bytes'] / (1024**3):.2f} GB</div>
            <div class="stat-label">Space to Save</div>
        </div>
        <div class="stat-card">
            <div class="stat-value savings">{(self.stats['total_duplicates'] / max(self.stats['total_files'], 1) * 100):.1f}%</div>
            <div class="stat-label">Reduction</div>
        </div>
    </div>

    <div class="summary">
        <h2>Summary by Organization</h2>
        <table>
            <tr>
                <th>Organization</th>
                <th>Total Files</th>
                <th>Unique</th>
                <th>Duplicates</th>
                <th>Duplicate %</th>
            </tr>
'''

        # Get stats by organization
        cursor.execute('''
            SELECT
                organization,
                COUNT(*) as total,
                SUM(CASE WHEN is_duplicate = 0 THEN 1 ELSE 0 END) as unique_count,
                SUM(CASE WHEN is_duplicate = 1 THEN 1 ELSE 0 END) as dup_count
            FROM documents
            GROUP BY organization
            ORDER BY total DESC
        ''')

        for row in cursor.fetchall():
            org, total, unique, dups = row
            pct = (dups / total * 100) if total > 0 else 0
            html += f'''
            <tr>
                <td><span class="badge org-badge">{org}</span></td>
                <td>{total:,}</td>
                <td>{unique:,}</td>
                <td>{dups:,}</td>
                <td>{pct:.1f}%</td>
            </tr>'''

        html += '''
        </table>
    </div>

    <h2>Duplicate Groups (Top 100)</h2>
'''

        # Show top 100 duplicate groups
        count = 0
        for content_hash, files in sorted(duplicates.items(),
                                          key=lambda x: len(x[1]),
                                          reverse=True)[:100]:
            if len(files) < 2:
                continue

            count += 1
            best = self.select_best_version(files)
            total_size = sum(f['file_size'] or 0 for f in files)
            wasted = total_size - (best['file_size'] or 0)

            html += f'''
    <div class="duplicate-group">
        <div class="group-header">
            <div>
                <strong>Group #{count}</strong> - {len(files)} copies
                <span class="badge org-badge">{best['organization']}</span>
            </div>
            <div>
                Size: {best['file_size'] / 1024 / 1024:.2f} MB |
                Wasted: {wasted / 1024 / 1024:.2f} MB
            </div>
        </div>
        <ul class="file-list">
'''

            for f in files:
                is_keep = f['id'] == best['id']
                css_class = 'original' if is_keep else 'duplicate'
                badge_class = 'badge-keep' if is_keep else 'badge-duplicate'
                badge_text = 'KEEP' if is_keep else 'DUPLICATE'

                html += f'''
            <li class="file-item {css_class}">
                <span class="file-path">{f['file_path']}</span>
                <span><span class="badge {badge_class}">{badge_text}</span></span>
            </li>'''

            html += '''
        </ul>
    </div>
'''

        html += '''
</body>
</html>
'''

        # Write report
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w') as f:
            f.write(html)

        logger.info(f"Report generated: {output_path}")

    def run(self, report_path: str = None):
        """Run duplicate detection and generate report."""
        self.connect()

        logger.info("Finding duplicates by content hash...")
        duplicates = self.find_duplicates()

        logger.info("Marking duplicates in database...")
        self.mark_duplicates(duplicates)

        # Generate report
        if report_path is None:
            report_path = os.path.join(
                self.config['target_directory'],
                '_duplicate_report.html'
            )

        self.generate_report(duplicates, report_path)

        # Print summary
        self._print_summary()

    def _print_summary(self):
        """Print duplicate detection summary."""
        print("\n" + "=" * 60)
        print("DUPLICATE DETECTION COMPLETE")
        print("=" * 60)
        print(f"Total files:        {self.stats['total_files']:,}")
        print(f"Unique files:       {self.stats['total_files'] - self.stats['total_duplicates']:,}")
        print(f"Duplicate files:    {self.stats['total_duplicates']:,}")
        print(f"Duplicate groups:   {self.stats['duplicate_groups']:,}")
        print(f"Space to save:      {self.stats['space_wasted_bytes'] / (1024**3):.2f} GB")
        print(f"Reduction:          {(self.stats['total_duplicates'] / max(self.stats['total_files'], 1) * 100):.1f}%")
        print("=" * 60)

    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()


def main():
    parser = argparse.ArgumentParser(
        description='Detect duplicate O&G standards documents'
    )
    parser.add_argument(
        '--config', '-c',
        default='config.yaml',
        help='Path to configuration file (default: config.yaml)'
    )
    parser.add_argument(
        '--report', '-r',
        help='Output path for HTML report'
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

    # Run duplicate detection
    detector = DuplicateDetector(config_path)
    try:
        detector.run(report_path=args.report)
    finally:
        detector.close()


if __name__ == '__main__':
    main()
