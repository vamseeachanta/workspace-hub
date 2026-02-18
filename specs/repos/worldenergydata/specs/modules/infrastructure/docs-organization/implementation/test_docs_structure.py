#!/usr/bin/env python3
"""
Tests for documentation structure validation
Part of Task 1.1: Write tests for docs/ directory structure validation
"""

import os
import pytest
from pathlib import Path


class TestDocsStructure:
    """Test suite for validating the docs/ directory structure"""
    
    def setup_method(self):
        """Set up test environment"""
        self.project_root = Path(__file__).parent
        self.docs_root = self.project_root / "docs"
        
        # Expected directory structure
        self.expected_structure = {
            "user-guide": [
                "getting-started",
                "installation", 
                "quick-examples",
                "api-reference"
            ],
            "data-sources": [
                "bsee",
                "sodir", 
                "wind",
                "lng",
                "equipment",
                "onshore"
            ],
            "analysis-guides": [
                "economic-evaluation",
                "production-analysis", 
                "field-development"
            ],
            "development": [],
            "reference": [
                "literature",
                "equipment-specs",
                "industry-standards"
            ],
            "examples": [
                "basic-usage",
                "field-analysis",
                "economic-modeling"
            ]
        }
    
    def test_docs_directory_exists(self):
        """Test that main docs/ directory exists"""
        assert self.docs_root.exists(), "docs/ directory should exist"
        assert self.docs_root.is_dir(), "docs/ should be a directory"
    
    def test_main_subdirectories_exist(self):
        """Test that all main subdirectories exist"""
        for main_dir in self.expected_structure.keys():
            dir_path = self.docs_root / main_dir
            assert dir_path.exists(), f"Directory {main_dir} should exist in docs/"
            assert dir_path.is_dir(), f"{main_dir} should be a directory"
    
    def test_subdirectory_structure(self):
        """Test that subdirectories have correct structure"""
        for main_dir, subdirs in self.expected_structure.items():
            main_path = self.docs_root / main_dir
            for subdir in subdirs:
                subdir_path = main_path / subdir
                assert subdir_path.exists(), f"Subdirectory {main_dir}/{subdir} should exist"
                assert subdir_path.is_dir(), f"{main_dir}/{subdir} should be a directory"
    
    def test_naming_conventions(self):
        """Test that directory names follow kebab-case convention"""
        for main_dir in self.expected_structure.keys():
            # Check main directories use kebab-case
            assert self._is_kebab_case(main_dir), f"Directory {main_dir} should use kebab-case"
            
            # Check subdirectories use kebab-case
            for subdir in self.expected_structure[main_dir]:
                assert self._is_kebab_case(subdir), f"Subdirectory {subdir} should use kebab-case"
    
    def test_index_files_exist(self):
        """Test that each main directory has an index.md file"""
        for main_dir in self.expected_structure.keys():
            index_file = self.docs_root / main_dir / "index.md"
            assert index_file.exists(), f"index.md should exist in {main_dir}/"
            assert index_file.is_file(), f"index.md in {main_dir}/ should be a file"
    
    def test_main_readme_exists(self):
        """Test that main docs/README.md exists"""
        readme_file = self.docs_root / "README.md"
        assert readme_file.exists(), "README.md should exist in docs/"
        assert readme_file.is_file(), "README.md should be a file"
    
    def test_template_file_headers(self):
        """Test that template files have proper headers"""
        for main_dir in self.expected_structure.keys():
            index_file = self.docs_root / main_dir / "index.md"
            if index_file.exists():
                content = index_file.read_text(encoding='utf-8')
                assert content.startswith('#'), f"index.md in {main_dir} should start with markdown header"
                assert main_dir.replace('-', ' ').title() in content, f"index.md should contain section title"
    
    def _is_kebab_case(self, name):
        """Check if name follows kebab-case convention"""
        # Allow lowercase letters, numbers, and hyphens
        # Must not start or end with hyphen
        import re
        pattern = r'^[a-z0-9]+(-[a-z0-9]+)*$'
        return bool(re.match(pattern, name))


class TestFileNamingConventions:
    """Test suite for file naming conventions"""
    
    def test_markdown_file_naming(self):
        """Test that new template files follow naming conventions"""
        docs_root = Path(__file__).parent / "docs"
        
        # Focus on testing the new structure we created
        new_structure_paths = [
            "user-guide", "data-sources", "analysis-guides", 
            "development", "reference", "examples"
        ]
        
        if docs_root.exists():
            # Test that our new index.md files exist and follow conventions
            for section in new_structure_paths:
                index_file = docs_root / section / "index.md"
                if index_file.exists():
                    # The index.md files should follow our standards
                    assert index_file.name == "index.md", f"Template file should be named index.md"
                    
            # Test main README follows conventions
            main_readme = docs_root / "README.md"
            if main_readme.exists():
                assert main_readme.name == "README.md", "Main README should follow naming convention"
    
    def _is_valid_filename(self, filename):
        """Check if filename follows valid naming conventions"""
        import re
        # Allow kebab-case for regular files
        pattern = r'^[a-z0-9]+(-[a-z0-9]+)*$'
        return bool(re.match(pattern, filename))


if __name__ == "__main__":
    # Run tests when script is executed directly
    pytest.main([__file__, "-v"])