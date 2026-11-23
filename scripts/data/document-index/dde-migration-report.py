#!/usr/bin/env python3
"""
DDE Literature Migration Report
GitHub Issue: #1863

Walks the migrated DDE literature directory, counts files and bytes,
and compares against the original source catalog.

Usage:
    python dde-migration-report.py
"""

import os
import yaml
import datetime
from pathlib import Path
from collections import defaultdict

# --- Configuration ---
WORKSPACE_ROOT = Path(__file__).resolve().parents[3]
MIGRATION_DIR = Path("/mnt/ace/docs/literature/dde")
CATALOG_FILE = WORKSPACE_ROOT / "data" / "document-index" / "dde-literature-catalog.yaml"
OUTPUT_FILE = WORKSPACE_ROOT / "data" / "document-index" / "dde-migration-report.yaml"

def get_dir_stats(directory: Path):
    """Walks a directory and returns stats about its contents."""
    file_count = 0
    total_bytes = 0
    by_type = defaultdict(int)
    
    for root, _, files in os.walk(directory):
        for fname in files:
            file_path = Path(root) / fname
            file_count += 1
            try:
                size = file_path.stat().st_size
                total_bytes += size
                ext = file_path.suffix.lower() if file_path.suffix else '.no_extension'
                by_type[ext] += 1
            except FileNotFoundError:
                continue # File might be a broken symlink
                
    return file_count, total_bytes, dict(by_type)

def load_source_catalog(catalog_file: Path):
    """Loads the source DDE catalog."""
    if not catalog_file.exists():
        return None
    with open(catalog_file, 'r') as f:
        return yaml.safe_load(f)

def main():
    """Main function to generate the report."""
    print(f"Analyzing migrated files in: {MIGRATION_DIR}")
    
    # 1. Get stats from the migrated directory
    files_migrated, bytes_migrated, by_type = get_dir_stats(MIGRATION_DIR)
    
    print(f"Found {files_migrated} files, total size {bytes_migrated / (1024**3):.2f} GB.")

    # 2. Load source catalog for comparison
    source_catalog = load_source_catalog(CATALOG_FILE)
    comparison = {"source_catalog_found": False, "missing_files": []}
    if source_catalog:
        comparison["source_catalog_found"] = True
        source_files = {item['filename'] for item in source_catalog.get('catalog', [])}
        
        migrated_files = set()
        for root, _, files in os.walk(MIGRATION_DIR):
            for fname in files:
                migrated_files.add(fname)
        
        missing = sorted(list(source_files - migrated_files))
        comparison["missing_files"] = missing
        comparison["source_file_count"] = len(source_files)
        comparison["migrated_file_count_from_source_list"] = len(source_files) - len(missing)
        
        print(f"Compared against {len(source_files)} files in the source catalog.")
        if missing:
            print(f"Found {len(missing)} missing files (listed in report).")
        else:
            print("All files from source catalog appear to be migrated.")

    # 3. Prepare the report data
    report = {
        "migration_date": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "target_directory": str(MIGRATION_DIR),
        "files_migrated": files_migrated,
        "bytes_migrated": bytes_migrated,
        "gigabytes_migrated": round(bytes_migrated / (1024**3), 2),
        "files_by_type": dict(sorted(by_type.items(), key=lambda item: -item[1])),
        "source_comparison": comparison
    }
    
    # 4. Write the report
    OUTPUT_FILE.parent.mkdir(exist_ok=True)
    with open(OUTPUT_FILE, 'w') as f:
        yaml.dump(report, f, sort_keys=False, default_flow_style=False)
        
        print(f"\nMigration report written to: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
