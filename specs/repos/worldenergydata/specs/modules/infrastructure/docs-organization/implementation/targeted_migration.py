#!/usr/bin/env python3
"""
Targeted Migration Script for BSEE Documentation
Focuses on actual BSEE module files to avoid categorization errors
"""

import json
import shutil
from pathlib import Path
from docs_migration_system import DocumentationMigrator


def get_actual_bsee_files():
    """Get files that are actually in the BSEE module directory"""
    project_root = Path(__file__).parent
    bsee_files = []
    
    # Look for files in docs/modules/bsee/
    bsee_module_path = project_root / "docs/modules/bsee"
    if bsee_module_path.exists():
        for file_path in bsee_module_path.rglob("*.md"):
            if file_path.is_file():
                rel_path = str(file_path.relative_to(project_root))
                bsee_files.append(rel_path)
    
    return bsee_files


def create_bsee_migration_mapping(bsee_files):
    """Create proper mapping for BSEE files"""
    mapping = {}
    
    for old_path in bsee_files:
        old_path_obj = Path(old_path)
        
        # Preserve internal BSEE structure
        # Normalize path separators
        normalized_path = old_path.replace("\\", "/")
        
        if "modules/bsee/" in normalized_path:
            # Replace docs/modules/bsee/ with docs/data-sources/bsee/
            new_path = normalized_path.replace("docs/modules/bsee/", "docs/data-sources/bsee/")
        else:
            new_path = f"docs/data-sources/bsee/{old_path_obj.name}"
        
        mapping[old_path] = {
            'old_path': old_path,
            'new_path': new_path,
            'category': 'data-sources/bsee',
            'action': 'migrate'
        }
    
    return mapping


def execute_bsee_migration(dry_run=True):
    """Execute focused BSEE migration"""
    print("=== FOCUSED BSEE MIGRATION ===")
    
    # Get actual BSEE files
    bsee_files = get_actual_bsee_files()
    print(f"Found {len(bsee_files)} actual BSEE module files")
    
    if not bsee_files:
        print("No BSEE files found to migrate")
        return
    
    # Show sample files
    print("\\nSample files to migrate:")
    for i, file_path in enumerate(bsee_files[:5]):
        print(f"  {i+1}. {file_path}")
    if len(bsee_files) > 5:
        print(f"  ... and {len(bsee_files) - 5} more")
    
    # Create proper mapping
    bsee_mapping = create_bsee_migration_mapping(bsee_files)
    
    # Show mapping examples
    print("\\nMigration mapping examples:")
    for i, (old_path, mapping_info) in enumerate(list(bsee_mapping.items())[:3]):
        print(f"  {old_path}")
        print(f"  -> {mapping_info['new_path']}")
        print()
    
    if dry_run:
        print("DRY RUN - No files were actually moved")
        return bsee_mapping
    
    # Execute migration
    project_root = Path(__file__).parent
    migrated_count = 0
    failed_files = []
    
    for old_path, mapping_info in bsee_mapping.items():
        try:
            old_full_path = project_root / old_path
            new_full_path = project_root / mapping_info['new_path']
            
            if old_full_path.exists():
                # Ensure destination directory exists
                new_full_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Move file
                shutil.move(str(old_full_path), str(new_full_path))
                migrated_count += 1
                print(f"[OK] Migrated: {old_path}")
            else:
                print(f"[WARN] Source not found: {old_path}")
        
        except Exception as e:
            print(f"[ERROR] Failed to migrate {old_path}: {e}")
            failed_files.append(old_path)
    
    print(f"\\nMigration complete: {migrated_count}/{len(bsee_files)} successful")
    if failed_files:
        print(f"Failed files: {failed_files}")
    
    return bsee_mapping


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Targeted BSEE Migration")
    parser.add_argument('--execute', action='store_true', 
                        help='Execute actual migration (default is dry run)')
    
    args = parser.parse_args()
    
    execute_bsee_migration(dry_run=not args.execute)