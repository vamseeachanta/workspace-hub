#!/usr/bin/env python3
"""
Tests for documentation migration system integrity
Part of Task 3.1: Write tests for file migration integrity
"""

import os
import json
import shutil
import hashlib
import tempfile
import pytest
from pathlib import Path
from typing import Dict, List, Tuple, Set
from unittest.mock import Mock, patch


class MigrationTester:
    """Test framework for documentation migration operations"""
    
    def __init__(self, project_root: Path = None):
        self.project_root = project_root or Path(__file__).parent
        self.docs_root = self.project_root / "docs"
        self.test_temp_dir = None
        
    def setup_test_environment(self) -> Path:
        """Create temporary test environment"""
        self.test_temp_dir = Path(tempfile.mkdtemp(prefix="docs_migration_test_"))
        return self.test_temp_dir
    
    def cleanup_test_environment(self):
        """Clean up temporary test environment"""
        if self.test_temp_dir and self.test_temp_dir.exists():
            shutil.rmtree(self.test_temp_dir)
    
    def calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA-256 hash of file content"""
        if not file_path.exists():
            return ""
        
        hash_sha256 = hashlib.sha256()
        try:
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_sha256.update(chunk)
            return hash_sha256.hexdigest()
        except Exception:
            return ""
    
    def create_file_inventory(self, directory: Path) -> Dict[str, Dict]:
        """Create comprehensive inventory of files in directory"""
        inventory = {}
        
        for file_path in directory.rglob('*'):
            if file_path.is_file():
                rel_path = str(file_path.relative_to(directory))
                inventory[rel_path] = {
                    'size': file_path.stat().st_size,
                    'hash': self.calculate_file_hash(file_path),
                    'exists': True
                }
        
        return inventory
    
    def compare_inventories(self, before: Dict, after: Dict) -> Dict:
        """Compare file inventories before and after migration"""
        comparison = {
            'files_added': [],
            'files_removed': [],
            'files_modified': [],
            'files_unchanged': [],
            'hash_mismatches': [],
            'size_changes': []
        }
        
        all_files = set(before.keys()) | set(after.keys())
        
        for file_path in all_files:
            if file_path not in before:
                comparison['files_added'].append(file_path)
            elif file_path not in after:
                comparison['files_removed'].append(file_path)
            else:
                before_info = before[file_path]
                after_info = after[file_path]
                
                if before_info['hash'] != after_info['hash']:
                    comparison['hash_mismatches'].append(file_path)
                
                if before_info['size'] != after_info['size']:
                    comparison['size_changes'].append(file_path)
                
                if before_info == after_info:
                    comparison['files_unchanged'].append(file_path)
                else:
                    comparison['files_modified'].append(file_path)
        
        return comparison


class TestMigrationIntegrity:
    """Test suite for migration system integrity"""
    
    def setup_method(self):
        """Set up test environment"""
        self.tester = MigrationTester()
        self.test_dir = self.tester.setup_test_environment()
        
        # Load migration mapping
        migration_file = Path(__file__).parent / 'docs_analysis_report.json'
        if migration_file.exists():
            with open(migration_file, 'r', encoding='utf-8') as f:
                self.migration_data = json.load(f)
        else:
            self.migration_data = {'migration_mapping': {}}
    
    def teardown_method(self):
        """Clean up test environment"""
        self.tester.cleanup_test_environment()
    
    def test_migration_tester_initialization(self):
        """Test that migration tester initializes correctly"""
        assert isinstance(self.tester, MigrationTester)
        assert self.test_dir.exists()
        assert self.test_dir.is_dir()
    
    def test_file_hash_calculation(self):
        """Test file hash calculation accuracy"""
        # Create test file
        test_file = self.test_dir / "test.md"
        test_content = "# Test Content\nThis is test content."
        test_file.write_text(test_content, encoding='utf-8')
        
        # Calculate hash
        hash1 = self.tester.calculate_file_hash(test_file)
        assert len(hash1) == 64  # SHA-256 hex length
        
        # Calculate again - should be identical
        hash2 = self.tester.calculate_file_hash(test_file)
        assert hash1 == hash2
        
        # Modify file - hash should change
        test_file.write_text(test_content + "\nAdditional content", encoding='utf-8')
        hash3 = self.tester.calculate_file_hash(test_file)
        assert hash1 != hash3
    
    def test_file_inventory_creation(self):
        """Test comprehensive file inventory creation"""
        # Create test files
        (self.test_dir / "file1.md").write_text("Content 1", encoding='utf-8')
        (self.test_dir / "file2.txt").write_text("Content 2", encoding='utf-8')
        (self.test_dir / "subdir").mkdir()
        (self.test_dir / "subdir" / "file3.md").write_text("Content 3", encoding='utf-8')
        
        # Create inventory
        inventory = self.tester.create_file_inventory(self.test_dir)
        
        # Verify inventory
        assert len(inventory) == 3
        assert "file1.md" in inventory
        assert "file2.txt" in inventory
        # Handle both forward and backslash separators
        subdir_file = "subdir/file3.md" if "subdir/file3.md" in inventory else "subdir\\file3.md"
        assert subdir_file in inventory
        
        # Verify inventory structure
        for file_info in inventory.values():
            assert 'size' in file_info
            assert 'hash' in file_info
            assert 'exists' in file_info
    
    def test_inventory_comparison(self):
        """Test inventory comparison functionality"""
        # Create initial inventory
        before = {
            'file1.md': {'size': 100, 'hash': 'abc123', 'exists': True},
            'file2.md': {'size': 200, 'hash': 'def456', 'exists': True},
            'file3.md': {'size': 150, 'hash': 'ghi789', 'exists': True}
        }
        
        # Create modified inventory
        after = {
            'file1.md': {'size': 100, 'hash': 'abc123', 'exists': True},  # Unchanged
            'file2.md': {'size': 200, 'hash': 'modified', 'exists': True},  # Hash changed
            'file4.md': {'size': 300, 'hash': 'new123', 'exists': True}   # New file
        }
        
        # Compare inventories
        comparison = self.tester.compare_inventories(before, after)
        
        # Verify comparison results
        assert len(comparison['files_added']) == 1
        assert 'file4.md' in comparison['files_added']
        
        assert len(comparison['files_removed']) == 1
        assert 'file3.md' in comparison['files_removed']
        
        assert len(comparison['hash_mismatches']) == 1
        assert 'file2.md' in comparison['hash_mismatches']
        
        assert len(comparison['files_unchanged']) == 1
        assert 'file1.md' in comparison['files_unchanged']
    
    def test_migration_content_preservation(self):
        """Test that migration preserves file content"""
        # Create source file
        source_file = self.test_dir / "source.md"
        test_content = "# Original Content\n\nThis content must be preserved."
        source_file.write_text(test_content, encoding='utf-8')
        original_hash = self.tester.calculate_file_hash(source_file)
        
        # Simulate migration (copy to new location)
        dest_dir = self.test_dir / "migrated"
        dest_dir.mkdir()
        dest_file = dest_dir / "source.md"
        shutil.copy2(source_file, dest_file)
        
        # Verify content preservation
        migrated_hash = self.tester.calculate_file_hash(dest_file)
        assert original_hash == migrated_hash
        
        # Verify content is identical
        migrated_content = dest_file.read_text(encoding='utf-8')
        assert test_content == migrated_content
    
    def test_migration_metadata_preservation(self):
        """Test that migration preserves file metadata"""
        # Create source file
        source_file = self.test_dir / "metadata_test.md"
        source_file.write_text("Test content", encoding='utf-8')
        original_stat = source_file.stat()
        
        # Simulate migration with metadata preservation
        dest_file = self.test_dir / "migrated_metadata.md"
        shutil.copy2(source_file, dest_file)  # copy2 preserves metadata
        
        # Compare metadata
        migrated_stat = dest_file.stat()
        assert original_stat.st_size == migrated_stat.st_size
        assert abs(original_stat.st_mtime - migrated_stat.st_mtime) < 2  # Allow small time diff
    
    def test_directory_structure_creation(self):
        """Test that migration creates proper directory structure"""
        # Define target structure
        target_structure = [
            "docs/data-sources/bsee/analysis",
            "docs/data-sources/bsee/data", 
            "docs/analysis-guides/economic-evaluation",
            "docs/user-guide/getting-started"
        ]
        
        # Create directory structure
        for dir_path in target_structure:
            full_path = self.test_dir / dir_path
            full_path.mkdir(parents=True, exist_ok=True)
        
        # Verify structure exists
        for dir_path in target_structure:
            full_path = self.test_dir / dir_path
            assert full_path.exists()
            assert full_path.is_dir()
    
    def test_migration_rollback_capability(self):
        """Test ability to rollback migrations if needed"""
        # Create original structure
        original_file = self.test_dir / "original" / "test.md"
        original_file.parent.mkdir()
        original_file.write_text("Original content", encoding='utf-8')
        original_hash = self.tester.calculate_file_hash(original_file)
        
        # Create backup info
        backup_info = {
            str(original_file.relative_to(self.test_dir)): {
                'original_path': str(original_file),
                'content_hash': original_hash
            }
        }
        
        # Simulate migration
        migrated_file = self.test_dir / "migrated" / "test.md"
        migrated_file.parent.mkdir()
        shutil.move(str(original_file), str(migrated_file))
        
        # Verify original is gone
        assert not original_file.exists()
        assert migrated_file.exists()
        
        # Simulate rollback
        shutil.move(str(migrated_file), str(original_file))
        
        # Verify rollback success
        assert original_file.exists()
        assert not migrated_file.exists()
        rollback_hash = self.tester.calculate_file_hash(original_file)
        assert original_hash == rollback_hash
    
    def test_migration_error_handling(self):
        """Test migration error handling"""
        # Test migration to non-existent directory (should fail gracefully)
        source_file = self.test_dir / "source.md"
        source_file.write_text("Test content", encoding='utf-8')
        
        # Attempt migration to invalid destination
        invalid_dest = self.test_dir / "nonexistent" / "deeply" / "nested" / "file.md"
        
        # This should handle the error gracefully
        try:
            # Without creating parent directories, this should fail
            shutil.copy2(source_file, invalid_dest)
            assert False, "Should have raised an error"
        except (FileNotFoundError, OSError):
            # Expected behavior - error should be caught
            pass
        
        # Verify original file still exists
        assert source_file.exists()
    
    def test_migration_mapping_validation(self):
        """Test validation of migration mapping data"""
        if not self.migration_data.get('migration_mapping'):
            pytest.skip("No migration mapping data available")
        
        mapping = self.migration_data['migration_mapping']
        
        # Validate mapping structure
        for old_path, migration_info in mapping.items():
            assert 'old_path' in migration_info
            assert 'new_path' in migration_info
            assert 'category' in migration_info
            assert 'action' in migration_info
            
            # Validate paths are strings
            assert isinstance(migration_info['old_path'], str)
            assert isinstance(migration_info['new_path'], str)
            
            # Validate new path starts with docs/
            assert migration_info['new_path'].startswith('docs/'), \
                f"New path should start with docs/: {migration_info['new_path']}"


class TestMigrationScenarios:
    """Test specific migration scenarios"""
    
    def setup_method(self):
        """Set up test environment"""
        self.tester = MigrationTester()
        self.test_dir = self.tester.setup_test_environment()
    
    def teardown_method(self):
        """Clean up test environment"""
        self.tester.cleanup_test_environment()
    
    def test_bsee_documentation_migration(self):
        """Test BSEE documentation migration scenario"""
        # Create mock BSEE structure
        bsee_files = [
            "docs/modules/bsee/analysis/economics/npv.md",
            "docs/modules/bsee/analysis/production/decline.md",
            "docs/modules/bsee/data/production/notes.md"
        ]
        
        # Create source files
        for file_path in bsee_files:
            full_path = self.test_dir / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(f"Content for {file_path}", encoding='utf-8')
        
        # Create inventory before migration
        before_inventory = self.tester.create_file_inventory(self.test_dir)
        
        # Simulate migration to new structure
        new_structure = {
            "docs/modules/bsee/analysis/economics/npv.md": "docs/data-sources/bsee/analysis/economics/npv.md",
            "docs/modules/bsee/analysis/production/decline.md": "docs/data-sources/bsee/analysis/production/decline.md",
            "docs/modules/bsee/data/production/notes.md": "docs/data-sources/bsee/data/production/notes.md"
        }
        
        # Execute migration
        for old_path, new_path in new_structure.items():
            old_full = self.test_dir / old_path
            new_full = self.test_dir / new_path
            
            if old_full.exists():
                new_full.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(old_full), str(new_full))
        
        # Create inventory after migration
        after_inventory = self.tester.create_file_inventory(self.test_dir)
        
        # Verify migration results
        comparison = self.tester.compare_inventories(before_inventory, after_inventory)
        
        # Files should have moved, not been lost or modified
        assert len(comparison['files_removed']) == len(bsee_files)
        assert len(comparison['files_added']) == len(bsee_files)
        assert len(comparison['hash_mismatches']) == 0  # Content should be unchanged


if __name__ == "__main__":
    # Run tests when script is executed directly
    pytest.main([__file__, "-v"])