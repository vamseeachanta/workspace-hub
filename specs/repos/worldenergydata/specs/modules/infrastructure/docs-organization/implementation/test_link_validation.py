#!/usr/bin/env python3
"""
Tests for link validation and navigation system
Task 5.1: Write tests for link validation and navigation paths
"""

import pytest
from pathlib import Path
import re
from typing import List, Dict, Set, Tuple
from dataclasses import dataclass
from urllib.parse import urlparse
import tempfile


@dataclass
class LinkValidationResult:
    """Result of validating a single link"""
    source_file: Path
    link_text: str
    link_target: str
    link_type: str  # 'internal', 'external', 'anchor', 'email'
    is_valid: bool
    error_message: str = ""
    line_number: int = 0


@dataclass
class NavigationStructure:
    """Represents the navigation structure"""
    entry_points: Dict[str, Path]  # user_type -> main_file
    section_indexes: Dict[str, Path]  # section_name -> index_file
    cross_references: List[Tuple[Path, Path, str]]  # from_file, to_file, relation_type


class LinkValidator:
    """Validate internal and external links in markdown files"""
    
    def __init__(self, docs_root: Path):
        self.docs_root = docs_root
        self.project_root = docs_root.parent
        
        # Link patterns
        self.markdown_link_pattern = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')
        self.reference_link_pattern = re.compile(r'\[([^\]]+)\]:\s*(.+)')
        self.relative_link_pattern = re.compile(r'^\.\.?/')
        self.anchor_pattern = re.compile(r'#[a-zA-Z0-9_-]+$')
        
        # Navigation patterns
        self.header_pattern = re.compile(r'^(#{1,6})\s+(.+)$', re.MULTILINE)
        
        # File extensions that should exist
        self.valid_extensions = {'.md', '.txt', '.pdf', '.png', '.jpg', '.jpeg', '.gif', '.svg'}
    
    def validate_all_links(self) -> List[LinkValidationResult]:
        """Validate all links in all markdown files"""
        results = []
        
        md_files = list(self.docs_root.rglob("*.md"))
        
        for md_file in md_files:
            file_results = self.validate_file_links(md_file)
            results.extend(file_results)
        
        return results
    
    def validate_file_links(self, file_path: Path) -> List[LinkValidationResult]:
        """Validate all links in a single file"""
        results = []
        
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            lines = content.splitlines()
            
            # Find all markdown links
            for line_num, line in enumerate(lines, 1):
                # Standard markdown links [text](url)
                for match in self.markdown_link_pattern.finditer(line):
                    link_text = match.group(1)
                    link_target = match.group(2)
                    
                    result = self._validate_single_link(
                        file_path, link_text, link_target, line_num
                    )
                    results.append(result)
                
                # Reference style links [text]: url
                for match in self.reference_link_pattern.finditer(line):
                    link_text = match.group(1)
                    link_target = match.group(2)
                    
                    result = self._validate_single_link(
                        file_path, link_text, link_target, line_num
                    )
                    results.append(result)
        
        except Exception as e:
            results.append(LinkValidationResult(
                source_file=file_path,
                link_text="",
                link_target="",
                link_type="error",
                is_valid=False,
                error_message=f"Could not read file: {str(e)}",
                line_number=0
            ))
        
        return results
    
    def _validate_single_link(self, source_file: Path, link_text: str, 
                             link_target: str, line_number: int) -> LinkValidationResult:
        """Validate a single link"""
        
        # Determine link type
        link_type = self._determine_link_type(link_target)
        
        result = LinkValidationResult(
            source_file=source_file,
            link_text=link_text,
            link_target=link_target,
            link_type=link_type,
            is_valid=False,
            line_number=line_number
        )
        
        try:
            if link_type == 'internal':
                result.is_valid = self._validate_internal_link(source_file, link_target)
            elif link_type == 'anchor':
                result.is_valid = self._validate_anchor_link(source_file, link_target)
            elif link_type == 'external':
                result.is_valid = self._validate_external_link(link_target)
            elif link_type == 'email':
                result.is_valid = self._validate_email_link(link_target)
            else:
                result.error_message = f"Unknown link type: {link_type}"
                
        except Exception as e:
            result.error_message = str(e)
        
        return result
    
    def _determine_link_type(self, link_target: str) -> str:
        """Determine the type of link"""
        if link_target.startswith('mailto:'):
            return 'email'
        elif link_target.startswith(('http://', 'https://')):
            return 'external'
        elif link_target.startswith('#'):
            return 'anchor'
        elif self.relative_link_pattern.match(link_target) or not urlparse(link_target).scheme:
            return 'internal'
        else:
            return 'external'
    
    def _validate_internal_link(self, source_file: Path, link_target: str) -> bool:
        """Validate internal file links"""
        # Remove anchor part if present
        target_path = link_target.split('#')[0]
        
        if not target_path:  # Just an anchor
            return True
        
        # Handle relative paths
        if target_path.startswith('./') or target_path.startswith('../'):
            target_file = (source_file.parent / target_path).resolve()
        else:
            # Try relative to source file first
            target_file = (source_file.parent / target_path).resolve()
            
            # If not found, try relative to docs root
            if not target_file.exists():
                target_file = (self.docs_root / target_path).resolve()
                
            # If still not found, try relative to project root
            if not target_file.exists():
                target_file = (self.project_root / target_path).resolve()
        
        return target_file.exists()
    
    def _validate_anchor_link(self, source_file: Path, link_target: str) -> bool:
        """Validate anchor links within the same file"""
        try:
            content = source_file.read_text(encoding='utf-8', errors='ignore')
            
            # Convert anchor to expected header format
            anchor = link_target[1:]  # Remove #
            
            # Find all headers in the file
            headers = self.header_pattern.findall(content)
            
            # Convert headers to anchor format
            for level, header_text in headers:
                # GitHub-style anchor generation
                anchor_text = header_text.lower()
                anchor_text = re.sub(r'[^\w\s-]', '', anchor_text)
                anchor_text = re.sub(r'[-\s]+', '-', anchor_text)
                anchor_text = anchor_text.strip('-')
                
                if anchor_text == anchor:
                    return True
            
            return False
            
        except Exception:
            return False
    
    def _validate_external_link(self, link_target: str) -> bool:
        """Basic validation of external links (URL format)"""
        try:
            parsed = urlparse(link_target)
            return bool(parsed.scheme and parsed.netloc)
        except Exception:
            return False
    
    def _validate_email_link(self, link_target: str) -> bool:
        """Validate email links"""
        email_pattern = re.compile(r'^mailto:[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
        return bool(email_pattern.match(link_target))


class NavigationAnalyzer:
    """Analyze and validate navigation structure"""
    
    def __init__(self, docs_root: Path):
        self.docs_root = docs_root
        self.expected_sections = [
            'user-guide',
            'data-sources', 
            'analysis-guides',
            'development',
            'reference',
            'examples'
        ]
        
        self.user_types = [
            'energy-professional',
            'developer', 
            'data-analyst'
        ]
    
    def analyze_navigation_structure(self) -> NavigationStructure:
        """Analyze current navigation structure"""
        
        # Check for main entry points
        entry_points = {}
        main_readme = self.docs_root / "README.md"
        if main_readme.exists():
            entry_points['main'] = main_readme
        
        # Check for section indexes
        section_indexes = {}
        for section in self.expected_sections:
            section_dir = self.docs_root / section
            if section_dir.exists():
                # Look for index files
                possible_indexes = [
                    section_dir / "README.md",
                    section_dir / "index.md",
                    section_dir / f"{section}.md"
                ]
                
                for index_file in possible_indexes:
                    if index_file.exists():
                        section_indexes[section] = index_file
                        break
        
        # Analyze cross-references (simplified)
        cross_references = self._find_cross_references()
        
        return NavigationStructure(
            entry_points=entry_points,
            section_indexes=section_indexes,
            cross_references=cross_references
        )
    
    def _find_cross_references(self) -> List[Tuple[Path, Path, str]]:
        """Find cross-references between files"""
        cross_refs = []
        
        md_files = list(self.docs_root.rglob("*.md"))
        
        for source_file in md_files:
            try:
                content = source_file.read_text(encoding='utf-8', errors='ignore')
                
                # Look for relative links to other md files
                link_pattern = re.compile(r'\[([^\]]+)\]\(([^)]+\.md)\)')
                
                for match in link_pattern.finditer(content):
                    link_text = match.group(1)
                    link_target = match.group(2)
                    
                    # Resolve target file
                    if link_target.startswith('./') or link_target.startswith('../'):
                        target_file = (source_file.parent / link_target).resolve()
                    else:
                        target_file = (self.docs_root / link_target).resolve()
                    
                    if target_file.exists():
                        cross_refs.append((source_file, target_file, "reference"))
                        
            except Exception:
                continue
        
        return cross_refs
    
    def validate_navigation_completeness(self, nav_structure: NavigationStructure) -> Dict[str, List[str]]:
        """Validate that navigation structure is complete"""
        issues = {
            'missing_entry_points': [],
            'missing_section_indexes': [],
            'orphaned_sections': [],
            'broken_cross_references': []
        }
        
        # Check for main entry point
        if 'main' not in nav_structure.entry_points:
            issues['missing_entry_points'].append("Main docs/README.md missing")
        
        # Check for section indexes
        for section in self.expected_sections:
            if section not in nav_structure.section_indexes:
                section_dir = self.docs_root / section
                if section_dir.exists():
                    issues['missing_section_indexes'].append(f"Index missing for {section}")
        
        # Check for orphaned sections (directories without any documentation)
        for item in self.docs_root.iterdir():
            if item.is_dir() and item.name not in self.expected_sections:
                md_files = list(item.rglob("*.md"))
                if md_files and item.name not in nav_structure.section_indexes:
                    issues['orphaned_sections'].append(item.name)
        
        return issues


class TestLinkValidation:
    """Test suite for link validation system"""
    
    @pytest.fixture
    def temp_docs_dir(self, tmp_path):
        """Create temporary docs directory for testing"""
        docs_dir = tmp_path / "docs"
        docs_dir.mkdir()
        
        # Create basic structure
        (docs_dir / "user-guide").mkdir()
        (docs_dir / "data-sources").mkdir() 
        (docs_dir / "development").mkdir()
        
        return docs_dir
    
    @pytest.fixture
    def sample_markdown_files(self, temp_docs_dir):
        """Create sample markdown files with various link types"""
        
        # File with valid internal links
        main_file = temp_docs_dir / "README.md"
        main_content = """# Main Documentation

## Getting Started
See the [User Guide](user-guide/index.md) for getting started.

For developers, check out [Development Guide](development/setup.md).

## External Resources
- [Official Website](https://example.com)
- [Contact Us](mailto:contact@example.com)

## Anchors
Jump to [Installation](#installation) section.

### Installation
Installation instructions here.
"""
        main_file.write_text(main_content, encoding='utf-8')
        
        # User guide index
        user_guide_index = temp_docs_dir / "user-guide" / "index.md"
        user_guide_content = """# User Guide

Welcome to the user guide.

## Contents
- [Getting Started](getting-started.md)
- [API Reference](../development/api.md)

## See Also
Back to [Main Documentation](../README.md).
"""
        user_guide_index.write_text(user_guide_content, encoding='utf-8')
        
        # File with broken links
        broken_file = temp_docs_dir / "broken-links.md"
        broken_content = """# File with Broken Links

- [Missing File](missing-file.md)
- [Bad External Link](http://this-domain-does-not-exist-hopefully.invalid)
- [Bad Anchor](#non-existent-header)
- [Malformed Email](mailto:invalid-email)
"""
        broken_file.write_text(broken_content, encoding='utf-8')
        
        return {
            'main': main_file,
            'user_guide': user_guide_index,
            'broken': broken_file
        }
    
    def test_link_pattern_detection(self, temp_docs_dir):
        """Test that link patterns are correctly detected"""
        validator = LinkValidator(temp_docs_dir)
        
        test_content = """
[Valid Link](file.md)
[External Link](https://example.com)
[Email Link](mailto:test@example.com)
[Anchor Link](#section)
[Reference Link]: https://example.com
"""
        
        # Test pattern matching
        markdown_links = validator.markdown_link_pattern.findall(test_content)
        assert len(markdown_links) == 4
        
        reference_links = validator.reference_link_pattern.findall(test_content)
        assert len(reference_links) == 1
    
    def test_link_type_detection(self, temp_docs_dir):
        """Test correct classification of link types"""
        validator = LinkValidator(temp_docs_dir)
        
        test_cases = [
            ("https://example.com", "external"),
            ("mailto:test@example.com", "email"),
            ("#section", "anchor"),
            ("./file.md", "internal"),
            ("../other/file.md", "internal"),
            ("file.md", "internal")
        ]
        
        for link_target, expected_type in test_cases:
            actual_type = validator._determine_link_type(link_target)
            assert actual_type == expected_type, f"Link {link_target} should be {expected_type}, got {actual_type}"
    
    def test_internal_link_validation(self, temp_docs_dir, sample_markdown_files):
        """Test validation of internal links"""
        validator = LinkValidator(temp_docs_dir)
        
        # Test existing file
        main_file = sample_markdown_files['main']
        assert validator._validate_internal_link(main_file, "user-guide/index.md") == True
        
        # Test non-existing file
        assert validator._validate_internal_link(main_file, "non-existent.md") == False
    
    def test_anchor_link_validation(self, temp_docs_dir, sample_markdown_files):
        """Test validation of anchor links"""
        validator = LinkValidator(temp_docs_dir)
        
        main_file = sample_markdown_files['main']
        
        # Test existing anchor
        assert validator._validate_anchor_link(main_file, "#installation") == True
        
        # Test non-existing anchor
        assert validator._validate_anchor_link(main_file, "#non-existent") == False
    
    def test_external_link_validation(self, temp_docs_dir):
        """Test validation of external links"""
        validator = LinkValidator(temp_docs_dir)
        
        # Valid external links
        assert validator._validate_external_link("https://example.com") == True
        assert validator._validate_external_link("http://example.com") == True
        
        # Invalid external links
        assert validator._validate_external_link("not-a-url") == False
        assert validator._validate_external_link("mailto:test@example.com") == False
    
    def test_email_link_validation(self, temp_docs_dir):
        """Test validation of email links"""
        validator = LinkValidator(temp_docs_dir)
        
        # Valid email links
        assert validator._validate_email_link("mailto:test@example.com") == True
        assert validator._validate_email_link("mailto:user.name+tag@domain.co.uk") == True
        
        # Invalid email links
        assert validator._validate_email_link("mailto:invalid-email") == False
        assert validator._validate_email_link("test@example.com") == False
    
    def test_full_file_validation(self, temp_docs_dir, sample_markdown_files):
        """Test validation of all links in a file"""
        validator = LinkValidator(temp_docs_dir)
        
        main_file = sample_markdown_files['main']
        results = validator.validate_file_links(main_file)
        
        # Should find multiple links
        assert len(results) > 0
        
        # Check that we found the expected links
        link_targets = [r.link_target for r in results]
        assert "user-guide/index.md" in link_targets
        assert "https://example.com" in link_targets
        assert "mailto:contact@example.com" in link_targets
        assert "#installation" in link_targets
    
    def test_broken_link_detection(self, temp_docs_dir, sample_markdown_files):
        """Test detection of broken links"""
        validator = LinkValidator(temp_docs_dir)
        
        broken_file = sample_markdown_files['broken']
        results = validator.validate_file_links(broken_file)
        
        # Should find broken links
        broken_results = [r for r in results if not r.is_valid]
        assert len(broken_results) > 0
        
        # Check specific broken link
        missing_file_results = [r for r in broken_results if "missing-file.md" in r.link_target]
        assert len(missing_file_results) == 1
    
    def test_navigation_structure_analysis(self, temp_docs_dir, sample_markdown_files):
        """Test analysis of navigation structure"""
        analyzer = NavigationAnalyzer(temp_docs_dir)
        nav_structure = analyzer.analyze_navigation_structure()
        
        # Should detect main entry point
        assert 'main' in nav_structure.entry_points
        
        # Should detect some cross-references
        assert len(nav_structure.cross_references) > 0
    
    def test_navigation_completeness_validation(self, temp_docs_dir):
        """Test validation of navigation completeness"""
        analyzer = NavigationAnalyzer(temp_docs_dir)
        nav_structure = analyzer.analyze_navigation_structure()
        
        issues = analyzer.validate_navigation_completeness(nav_structure)
        
        # Should identify missing indexes for existing sections
        assert 'missing_section_indexes' in issues
        assert isinstance(issues['missing_section_indexes'], list)
    
    def test_cross_reference_detection(self, temp_docs_dir, sample_markdown_files):
        """Test detection of cross-references between files"""
        analyzer = NavigationAnalyzer(temp_docs_dir)
        cross_refs = analyzer._find_cross_references()
        
        # Should find cross-references
        assert len(cross_refs) > 0
        
        # Verify structure of cross-references
        for source, target, relation in cross_refs:
            assert isinstance(source, Path)
            assert isinstance(target, Path)
            assert isinstance(relation, str)


if __name__ == "__main__":
    # Run basic functionality test
    print("Testing link validation system...")
    
    from pathlib import Path
    import tempfile
    
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        docs_dir = tmp_path / "docs"
        docs_dir.mkdir()
        
        # Create test file
        test_file = docs_dir / "test.md"
        test_content = """# Test Document

[Valid Internal Link](other.md)
[External Link](https://example.com)
[Broken Link](missing.md)
[Anchor Link](#header)

## Header
Content here.
"""
        test_file.write_text(test_content, encoding='utf-8')
        
        # Create target file
        other_file = docs_dir / "other.md"
        other_file.write_text("# Other Document", encoding='utf-8')
        
        # Test validation
        validator = LinkValidator(docs_dir)
        results = validator.validate_file_links(test_file)
        
        print(f"Found {len(results)} links:")
        for result in results:
            status = "[OK]" if result.is_valid else "[FAIL]"
            print(f"  {status} {result.link_type}: {result.link_target}")
        
        # Test navigation analysis
        analyzer = NavigationAnalyzer(docs_dir)
        nav_structure = analyzer.analyze_navigation_structure()
        
        print(f"\nNavigation analysis:")
        print(f"  Entry points: {len(nav_structure.entry_points)}")
        print(f"  Section indexes: {len(nav_structure.section_indexes)}")
        print(f"  Cross-references: {len(nav_structure.cross_references)}")
    
    print("Link validation test completed!")