#!/usr/bin/env python3
"""
Tests for documentation quality and consistency standards
Task 6.1: Write tests for documentation quality and consistency standards
"""

import pytest
from pathlib import Path
import re
from typing import List, Dict, Set, Tuple
from dataclasses import dataclass
from datetime import datetime
import tempfile


@dataclass
class QualityIssue:
    """Represents a documentation quality issue"""
    file_path: Path
    issue_type: str
    description: str
    line_number: int = 0
    severity: str = "warning"  # 'error', 'warning', 'info'
    suggestion: str = ""


@dataclass
class DocumentMetadata:
    """Represents expected document metadata"""
    title: str
    last_updated: str
    description: str
    target_users: List[str]
    section: str


class DocumentationQualityChecker:
    """Check documentation quality and consistency standards"""
    
    def __init__(self, docs_root: Path):
        self.docs_root = docs_root
        
        # Quality standards
        self.markdown_standards = {
            'max_line_length': 120,
            'min_header_spacing': 1,
            'required_sections': ['title'],
            'forbidden_patterns': [
                r'TODO:',  # Unresolved TODOs
                r'FIXME:',  # Unresolved fixes
                r'XXX:',   # Temporary markers
            ]
        }
        
        # Formatting standards
        self.formatting_standards = {
            'header_style': 'atx',  # # Header instead of Header\n======
            'list_style': 'dash',   # - item instead of * item
            'code_fence': 'backticks',  # ``` instead of ~~~
            'link_style': 'inline',     # [text](url) preferred over [text][ref]
        }
        
        # Content quality standards
        self.content_standards = {
            'min_content_length': 50,  # Minimum characters for substantial content
            'max_heading_length': 80,  # Maximum characters in headings
            'require_examples': True,  # Technical docs should have examples
            'energy_terminology': {   # Preferred energy industry terms
                'well bore': 'wellbore',
                'well head': 'wellhead', 
                'sea floor': 'seafloor',
                'off shore': 'offshore',
                'on shore': 'onshore'
            }
        }
        
        # File naming standards
        self.naming_standards = {
            'allowed_chars': r'^[a-z0-9_\-\.]+$',
            'preferred_case': 'snake_case',
            'max_filename_length': 50
        }
    
    def check_all_documents(self) -> List[QualityIssue]:
        """Check quality of all documentation files"""
        issues = []
        
        # Find all markdown files
        md_files = list(self.docs_root.rglob("*.md"))
        
        for md_file in md_files:
            file_issues = self.check_single_document(md_file)
            issues.extend(file_issues)
        
        return issues
    
    def check_single_document(self, file_path: Path) -> List[QualityIssue]:
        """Check quality of a single document"""
        issues = []
        
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            lines = content.splitlines()
            
            # Check filename standards
            issues.extend(self._check_filename_standards(file_path))
            
            # Check markdown formatting
            issues.extend(self._check_markdown_formatting(file_path, content, lines))
            
            # Check content quality
            issues.extend(self._check_content_quality(file_path, content, lines))
            
            # Check structure and metadata
            issues.extend(self._check_document_structure(file_path, content, lines))
            
            # Check energy industry terminology
            issues.extend(self._check_terminology(file_path, content))
            
        except Exception as e:
            issues.append(QualityIssue(
                file_path=file_path,
                issue_type="file_error",
                description=f"Could not read file: {str(e)}",
                severity="error"
            ))
        
        return issues
    
    def _check_filename_standards(self, file_path: Path) -> List[QualityIssue]:
        """Check filename follows standards"""
        issues = []
        filename = file_path.name
        
        # Check allowed characters
        if not re.match(self.naming_standards['allowed_chars'], filename.lower()):
            issues.append(QualityIssue(
                file_path=file_path,
                issue_type="filename_format",
                description="Filename contains invalid characters (use only a-z, 0-9, _, -, .)",
                severity="warning",
                suggestion=f"Rename to use only lowercase letters, numbers, underscores, hyphens, and dots"
            ))
        
        # Check filename length
        if len(filename) > self.naming_standards['max_filename_length']:
            issues.append(QualityIssue(
                file_path=file_path,
                issue_type="filename_length",
                description=f"Filename is too long ({len(filename)} chars, max {self.naming_standards['max_filename_length']})",
                severity="warning",
                suggestion="Use shorter, more concise filename"
            ))
        
        return issues
    
    def _check_markdown_formatting(self, file_path: Path, content: str, lines: List[str]) -> List[QualityIssue]:
        """Check markdown formatting consistency"""
        issues = []
        
        # Check line lengths
        for i, line in enumerate(lines, 1):
            if len(line) > self.markdown_standards['max_line_length']:
                issues.append(QualityIssue(
                    file_path=file_path,
                    issue_type="line_length",
                    description=f"Line too long ({len(line)} chars, max {self.markdown_standards['max_line_length']})",
                    line_number=i,
                    severity="info",
                    suggestion="Break long lines for better readability"
                ))
        
        # Check header formatting (ATX style preferred)
        setext_headers = re.findall(r'^.+\n[=-]+$', content, re.MULTILINE)
        if setext_headers:
            issues.append(QualityIssue(
                file_path=file_path,
                issue_type="header_style",
                description="Use ATX-style headers (# Header) instead of Setext-style (Header\n======)",
                severity="info",
                suggestion="Convert Setext headers to ATX format"
            ))
        
        # Check list formatting consistency
        bullet_lists = re.findall(r'^\s*[*+-]\s', content, re.MULTILINE)
        if bullet_lists:
            dash_count = len([item for item in bullet_lists if '-' in item])
            star_count = len([item for item in bullet_lists if '*' in item])
            plus_count = len([item for item in bullet_lists if '+' in item])
            
            if dash_count > 0 and (star_count > 0 or plus_count > 0):
                issues.append(QualityIssue(
                    file_path=file_path,
                    issue_type="list_consistency",
                    description="Mixed bullet list styles detected",
                    severity="info", 
                    suggestion="Use consistent bullet style (prefer dashes: -)"
                ))
        
        # Check for forbidden patterns
        for pattern in self.markdown_standards['forbidden_patterns']:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                line_num = content[:match.start()].count('\n') + 1
                issues.append(QualityIssue(
                    file_path=file_path,
                    issue_type="forbidden_pattern",
                    description=f"Found forbidden pattern: {pattern}",
                    line_number=line_num,
                    severity="warning",
                    suggestion="Resolve or remove temporary markers"
                ))
        
        return issues
    
    def _check_content_quality(self, file_path: Path, content: str, lines: List[str]) -> List[QualityIssue]:
        """Check content quality standards"""
        issues = []
        
        # Check minimum content length
        content_without_headers = re.sub(r'^#+\s.*$', '', content, flags=re.MULTILINE)
        content_text = re.sub(r'[^\w\s]', '', content_without_headers)
        
        if len(content_text.strip()) < self.content_standards['min_content_length']:
            issues.append(QualityIssue(
                file_path=file_path,
                issue_type="content_length",
                description=f"Document appears to have minimal content ({len(content_text.strip())} chars)",
                severity="warning",
                suggestion="Add more substantial content or consider if file is needed"
            ))
        
        # Check for very long headings
        headers = re.findall(r'^#+\s(.+)$', content, re.MULTILINE)
        for header in headers:
            if len(header) > self.content_standards['max_heading_length']:
                issues.append(QualityIssue(
                    file_path=file_path,
                    issue_type="heading_length",
                    description=f"Heading too long: '{header[:50]}...' ({len(header)} chars)",
                    severity="info",
                    suggestion="Use shorter, more concise headings"
                ))
        
        # Check for empty sections
        sections = re.split(r'^#+\s', content, flags=re.MULTILINE)
        for i, section in enumerate(sections[1:], 1):  # Skip first split (before first header)
            section_content = section.split('\n', 1)[1] if '\n' in section else ''
            section_text = re.sub(r'[^\w\s]', '', section_content).strip()
            
            if len(section_text) < 20:  # Very short section
                header_line = section.split('\n')[0] if section else f"Section {i}"
                issues.append(QualityIssue(
                    file_path=file_path,
                    issue_type="empty_section",
                    description=f"Section appears empty or too brief: {header_line}",
                    severity="info",
                    suggestion="Add content to section or remove if not needed"
                ))
        
        return issues
    
    def _check_document_structure(self, file_path: Path, content: str, lines: List[str]) -> List[QualityIssue]:
        """Check document structure and metadata"""
        issues = []
        
        # Check for H1 title
        h1_headers = re.findall(r'^#\s+(.+)$', content, re.MULTILINE)
        if not h1_headers:
            issues.append(QualityIssue(
                file_path=file_path,
                issue_type="missing_title",
                description="Document missing H1 title",
                severity="warning",
                suggestion="Add main title using # Title format"
            ))
        elif len(h1_headers) > 1:
            issues.append(QualityIssue(
                file_path=file_path,
                issue_type="multiple_titles",
                description=f"Document has multiple H1 titles ({len(h1_headers)})",
                severity="warning",
                suggestion="Use only one H1 title per document"
            ))
        
        # Check for consistent header hierarchy
        all_headers = re.findall(r'^(#+)\s', content, re.MULTILINE)
        if all_headers:
            header_levels = [len(h) for h in all_headers]
            
            # Check for skipped levels (e.g., H1 followed by H3)
            for i in range(1, len(header_levels)):
                if header_levels[i] > header_levels[i-1] + 1:
                    issues.append(QualityIssue(
                        file_path=file_path,
                        issue_type="header_hierarchy",
                        description=f"Header level skipped (H{header_levels[i-1]} to H{header_levels[i]})",
                        severity="info",
                        suggestion="Maintain sequential header hierarchy (H1 → H2 → H3)"
                    ))
        
        return issues
    
    def _check_terminology(self, file_path: Path, content: str) -> List[QualityIssue]:
        """Check energy industry terminology consistency"""
        issues = []
        
        for incorrect_term, correct_term in self.content_standards['energy_terminology'].items():
            if incorrect_term.lower() in content.lower():
                # Find all occurrences
                pattern = re.compile(re.escape(incorrect_term), re.IGNORECASE)
                matches = pattern.finditer(content)
                
                for match in matches:
                    line_num = content[:match.start()].count('\n') + 1
                    issues.append(QualityIssue(
                        file_path=file_path,
                        issue_type="terminology",
                        description=f"Use '{correct_term}' instead of '{incorrect_term}'",
                        line_number=line_num,
                        severity="info",
                        suggestion=f"Replace with industry-standard term: {correct_term}"
                    ))
        
        return issues
    
    def generate_quality_report(self, issues: List[QualityIssue]) -> Dict:
        """Generate comprehensive quality report"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'total_issues': len(issues),
            'issues_by_severity': {
                'error': len([i for i in issues if i.severity == 'error']),
                'warning': len([i for i in issues if i.severity == 'warning']),
                'info': len([i for i in issues if i.severity == 'info'])
            },
            'issues_by_type': {},
            'files_with_issues': len(set(i.file_path for i in issues)),
            'issues_by_file': {}
        }
        
        # Group by issue type
        for issue in issues:
            if issue.issue_type not in report['issues_by_type']:
                report['issues_by_type'][issue.issue_type] = 0
            report['issues_by_type'][issue.issue_type] += 1
        
        # Group by file
        for issue in issues:
            file_str = str(issue.file_path)
            if file_str not in report['issues_by_file']:
                report['issues_by_file'][file_str] = []
            
            report['issues_by_file'][file_str].append({
                'type': issue.issue_type,
                'description': issue.description,
                'line_number': issue.line_number,
                'severity': issue.severity,
                'suggestion': issue.suggestion
            })
        
        return report


class DocumentationFormatter:
    """Apply consistent formatting to documentation files"""
    
    def __init__(self, docs_root: Path):
        self.docs_root = docs_root
        self.fixes_applied = []
    
    def format_all_documents(self, dry_run: bool = True) -> Dict:
        """Apply consistent formatting to all documents"""
        results = {
            'timestamp': datetime.now().isoformat(),
            'dry_run': dry_run,
            'files_processed': 0,
            'files_modified': 0,
            'fixes_applied': 0,
            'errors': []
        }
        
        md_files = list(self.docs_root.rglob("*.md"))
        
        for md_file in md_files:
            try:
                modified = self._format_single_document(md_file, dry_run)
                results['files_processed'] += 1
                
                if modified:
                    results['files_modified'] += 1
                
            except Exception as e:
                results['errors'].append(f"Error formatting {md_file}: {str(e)}")
        
        results['fixes_applied'] = len(self.fixes_applied)
        return results
    
    def _format_single_document(self, file_path: Path, dry_run: bool) -> bool:
        """Format a single document"""
        try:
            original_content = file_path.read_text(encoding='utf-8', errors='ignore')
            formatted_content = original_content
            
            # Apply formatting fixes
            formatted_content = self._fix_header_spacing(formatted_content)
            formatted_content = self._fix_list_formatting(formatted_content)
            formatted_content = self._fix_line_endings(formatted_content)
            formatted_content = self._fix_trailing_whitespace(formatted_content)
            
            # Check if changes were made
            if formatted_content != original_content:
                if not dry_run:
                    file_path.write_text(formatted_content, encoding='utf-8')
                
                self.fixes_applied.append(str(file_path))
                return True
            
            return False
            
        except Exception as e:
            raise Exception(f"Failed to format {file_path}: {str(e)}")
    
    def _fix_header_spacing(self, content: str) -> str:
        """Fix header spacing"""
        # Ensure blank line before headers (except at start of file)
        content = re.sub(r'(\n[^\n#].*)\n(#+\s)', r'\1\n\n\2', content)
        
        # Ensure blank line after headers
        content = re.sub(r'(#+\s.*)\n([^\n#])', r'\1\n\n\2', content)
        
        return content
    
    def _fix_list_formatting(self, content: str) -> str:
        """Standardize list formatting to use dashes"""
        # Convert * and + to - for bullet lists
        content = re.sub(r'^(\s*)[*+](\s)', r'\1-\2', content, flags=re.MULTILINE)
        return content
    
    def _fix_line_endings(self, content: str) -> str:
        """Ensure consistent line endings"""
        # Normalize to Unix line endings
        content = content.replace('\r\n', '\n').replace('\r', '\n')
        return content
    
    def _fix_trailing_whitespace(self, content: str) -> str:
        """Remove trailing whitespace"""
        lines = content.splitlines()
        cleaned_lines = [line.rstrip() for line in lines]
        return '\n'.join(cleaned_lines)


class TestDocumentationQuality:
    """Test suite for documentation quality standards"""
    
    @pytest.fixture
    def temp_docs_dir(self, tmp_path):
        """Create temporary docs directory for testing"""
        docs_dir = tmp_path / "docs"
        docs_dir.mkdir()
        return docs_dir
    
    @pytest.fixture
    def sample_quality_documents(self, temp_docs_dir):
        """Create sample documents with various quality issues"""
        
        # Good quality document
        good_doc = temp_docs_dir / "good_document.md"
        good_content = """# Well-Structured Document

This document demonstrates good quality standards.

## Introduction

This section provides a clear introduction to the topic with sufficient detail
to help readers understand the content.

## Technical Details

Here we provide technical information with proper formatting:

- Item one with clear description
- Item two with additional context
- Item three completing the list

### Subsection

More detailed information in appropriate subsections.

## Conclusion

A proper conclusion that summarizes the content.
"""
        good_doc.write_text(good_content, encoding='utf-8')
        
        # Poor quality document
        poor_doc = temp_docs_dir / "poor-quality-document.md"
        poor_content = """# Poor Document
## Missing Introduction
This has issues TODO: fix this later
* Mixed bullet styles
- Different bullets
+ More different bullets

Very long line that exceeds the maximum recommended line length and should be broken into multiple lines for better readability and formatting consistency across all documentation files in the project

### Skipped Header Level

FIXME: This needs work

Short.
"""
        poor_doc.write_text(poor_content, encoding='utf-8')
        
        # Document with terminology issues
        terminology_doc = temp_docs_dir / "terminology_issues.md"
        terminology_content = """# Offshore Operations

Operations on the sea floor require specialized equipment.
The well head must be properly configured.
Off shore drilling presents unique challenges.
"""
        terminology_doc.write_text(terminology_content, encoding='utf-8')
        
        return {
            'good': good_doc,
            'poor': poor_doc,
            'terminology': terminology_doc
        }
    
    def test_quality_checker_initialization(self, temp_docs_dir):
        """Test quality checker initialization"""
        checker = DocumentationQualityChecker(temp_docs_dir)
        
        assert checker.docs_root == temp_docs_dir
        assert 'max_line_length' in checker.markdown_standards
        assert 'energy_terminology' in checker.content_standards
    
    def test_filename_standards_checking(self, temp_docs_dir):
        """Test filename standards validation"""
        checker = DocumentationQualityChecker(temp_docs_dir)
        
        # Create files with various naming issues
        bad_filename = temp_docs_dir / "Bad File Name With Spaces.md"
        bad_filename.write_text("# Test")
        
        long_filename = temp_docs_dir / "this_is_an_extremely_long_filename_that_exceeds_reasonable_limits.md"
        long_filename.write_text("# Test")
        
        issues = checker.check_all_documents()
        filename_issues = [i for i in issues if i.issue_type in ['filename_format', 'filename_length']]
        
        assert len(filename_issues) >= 2
    
    def test_markdown_formatting_detection(self, temp_docs_dir, sample_quality_documents):
        """Test markdown formatting issue detection"""
        checker = DocumentationQualityChecker(temp_docs_dir)
        
        issues = checker.check_single_document(sample_quality_documents['poor'])
        
        # Should detect various formatting issues
        issue_types = [i.issue_type for i in issues]
        assert 'line_length' in issue_types
        assert 'list_consistency' in issue_types
        assert 'forbidden_pattern' in issue_types
    
    def test_content_quality_checking(self, temp_docs_dir, sample_quality_documents):
        """Test content quality validation"""
        checker = DocumentationQualityChecker(temp_docs_dir)
        
        # Create document with minimal content
        minimal_doc = temp_docs_dir / "minimal.md"
        minimal_doc.write_text("# Title\n\nShort.")
        
        issues = checker.check_single_document(minimal_doc)
        content_issues = [i for i in issues if i.issue_type == 'content_length']
        
        assert len(content_issues) >= 1
    
    def test_document_structure_validation(self, temp_docs_dir):
        """Test document structure validation"""
        checker = DocumentationQualityChecker(temp_docs_dir)
        
        # Document without title
        no_title_doc = temp_docs_dir / "no_title.md"
        no_title_doc.write_text("## Just a subtitle\n\nContent here.")
        
        # Document with multiple H1s
        multiple_titles_doc = temp_docs_dir / "multiple_titles.md"
        multiple_titles_doc.write_text("# First Title\n\n# Second Title\n\nContent.")
        
        issues1 = checker.check_single_document(no_title_doc)
        issues2 = checker.check_single_document(multiple_titles_doc)
        
        title_issues1 = [i for i in issues1 if i.issue_type == 'missing_title']
        title_issues2 = [i for i in issues2 if i.issue_type == 'multiple_titles']
        
        assert len(title_issues1) >= 1
        assert len(title_issues2) >= 1
    
    def test_terminology_checking(self, temp_docs_dir, sample_quality_documents):
        """Test energy industry terminology validation"""
        checker = DocumentationQualityChecker(temp_docs_dir)
        
        issues = checker.check_single_document(sample_quality_documents['terminology'])
        terminology_issues = [i for i in issues if i.issue_type == 'terminology']
        
        # Should detect terminology issues
        assert len(terminology_issues) >= 2  # sea floor -> seafloor, well head -> wellhead
    
    def test_quality_report_generation(self, temp_docs_dir, sample_quality_documents):
        """Test quality report generation"""
        checker = DocumentationQualityChecker(temp_docs_dir)
        
        all_issues = checker.check_all_documents()
        report = checker.generate_quality_report(all_issues)
        
        assert 'timestamp' in report
        assert 'total_issues' in report
        assert 'issues_by_severity' in report
        assert 'issues_by_type' in report
        assert report['total_issues'] >= 0
    
    def test_document_formatter(self, temp_docs_dir):
        """Test document formatting functionality"""
        formatter = DocumentationFormatter(temp_docs_dir)
        
        # Create document with formatting issues
        messy_doc = temp_docs_dir / "messy.md"
        messy_content = """# Title
## No Space Before
Content here.
* Mixed lists
- Different bullets

Text with trailing spaces    

## Another Section"""
        messy_doc.write_text(messy_content, encoding='utf-8')
        
        # Test dry run
        results = formatter.format_all_documents(dry_run=True)
        
        assert results['files_processed'] >= 1
        assert 'dry_run' in results
        assert results['dry_run'] is True
    
    def test_formatting_fixes(self, temp_docs_dir):
        """Test specific formatting fixes"""
        formatter = DocumentationFormatter(temp_docs_dir)
        
        test_content = "# Title\n## Immediate Header\n* Bullet\n+ Different bullet\nLine with spaces   \n"
        
        fixed_content = formatter._fix_header_spacing(test_content)
        fixed_content = formatter._fix_list_formatting(fixed_content)
        fixed_content = formatter._fix_trailing_whitespace(fixed_content)
        
        # Should have proper spacing and consistent formatting
        assert '\n\n##' in fixed_content  # Header spacing
        assert '+ ' not in fixed_content  # Consistent bullets
        assert not fixed_content.endswith('   ')  # No trailing spaces


if __name__ == "__main__":
    # Run basic functionality test
    print("Testing documentation quality system...")
    
    from pathlib import Path
    import tempfile
    
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        docs_dir = tmp_path / "docs"
        docs_dir.mkdir()
        
        # Create test document
        test_doc = docs_dir / "test.md"
        test_content = """# Test Document

This is a test document with various issues TODO: fix later.

## Section One
* Mixed bullet styles
- Different bullets

Very long line that exceeds the maximum recommended line length and should be broken for better readability and consistency

### Subsection

FIXME: This needs work

Short content that might be too brief.
"""
        test_doc.write_text(test_content, encoding='utf-8')
        
        # Test quality checking
        checker = DocumentationQualityChecker(docs_dir)
        issues = checker.check_all_documents()
        
        print(f"Found {len(issues)} quality issues:")
        for issue in issues:
            print(f"  - {issue.issue_type}: {issue.description}")
        
        # Test formatting
        formatter = DocumentationFormatter(docs_dir)
        results = formatter.format_all_documents(dry_run=True)
        
        print(f"\nFormatting analysis:")
        print(f"  Files processed: {results['files_processed']}")
        print(f"  Files that need formatting: {results['files_modified']}")
        print(f"  Potential fixes: {results['fixes_applied']}")
    
    print("Documentation quality test completed!")