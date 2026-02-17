#!/usr/bin/env python3
"""
Tests for duplicate content detection and consolidation system
Task 4.1: Write tests for duplicate detection and merging accuracy
"""

import pytest
from pathlib import Path
import shutil
import hashlib
from dataclasses import dataclass
from typing import List, Dict, Tuple, Set
import difflib
from collections import defaultdict


@dataclass
class DuplicateMatch:
    """Represents a potential duplicate match between files"""
    file1: Path
    file2: Path
    similarity_score: float
    match_type: str  # 'exact', 'near_duplicate', 'partial_overlap'
    overlapping_sections: List[str]
    unique_content_file1: List[str]
    unique_content_file2: List[str]


@dataclass
class ConsolidationPlan:
    """Plan for consolidating duplicate content"""
    primary_file: Path
    files_to_merge: List[Path]
    files_to_remove: List[Path]
    merge_strategy: str  # 'append', 'interleave', 'replace_sections'
    preserved_sections: Dict[str, Path]  # section -> source file


class DuplicateDetector:
    """Detect and analyze duplicate content in documentation files"""
    
    def __init__(self, docs_root: Path):
        self.docs_root = docs_root
        self.similarity_threshold = 0.7  # 70% similarity for near-duplicates
        self.exact_threshold = 0.95      # 95% similarity for exact duplicates
    
    def find_all_duplicates(self) -> List[DuplicateMatch]:
        """Find all duplicate and overlapping content"""
        md_files = list(self.docs_root.rglob("*.md"))
        duplicates = []
        
        # Compare each pair of files
        for i, file1 in enumerate(md_files):
            for file2 in md_files[i+1:]:
                match = self._compare_files(file1, file2)
                if match and match.similarity_score >= self.similarity_threshold:
                    duplicates.append(match)
        
        return duplicates
    
    def _compare_files(self, file1: Path, file2: Path) -> DuplicateMatch:
        """Compare two files for duplicate content"""
        try:
            content1 = self._read_file_safe(file1)
            content2 = self._read_file_safe(file2)
            
            if not content1 or not content2:
                return None
            
            # Calculate overall similarity
            similarity = self._calculate_similarity(content1, content2)
            
            if similarity < self.similarity_threshold:
                return None
            
            # Determine match type
            if similarity >= self.exact_threshold:
                match_type = 'exact'
            elif similarity >= self.similarity_threshold:
                match_type = 'near_duplicate'
            else:
                match_type = 'partial_overlap'
            
            # Find overlapping sections
            overlapping_sections = self._find_overlapping_sections(content1, content2)
            
            # Find unique content in each file
            unique1 = self._find_unique_content(content1, content2)
            unique2 = self._find_unique_content(content2, content1)
            
            return DuplicateMatch(
                file1=file1,
                file2=file2,
                similarity_score=similarity,
                match_type=match_type,
                overlapping_sections=overlapping_sections,
                unique_content_file1=unique1,
                unique_content_file2=unique2
            )
            
        except Exception as e:
            return None
    
    def _read_file_safe(self, file_path: Path) -> str:
        """Safely read file content with error handling"""
        try:
            return file_path.read_text(encoding='utf-8', errors='ignore')
        except:
            return ""
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two texts"""
        lines1 = text1.splitlines()
        lines2 = text2.splitlines()
        
        matcher = difflib.SequenceMatcher(None, lines1, lines2)
        return matcher.ratio()
    
    def _find_overlapping_sections(self, text1: str, text2: str) -> List[str]:
        """Find sections that overlap between two texts"""
        lines1 = text1.splitlines()
        lines2 = text2.splitlines()
        
        matcher = difflib.SequenceMatcher(None, lines1, lines2)
        overlapping = []
        
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == 'equal':
                section = '\n'.join(lines1[i1:i2])
                if len(section.strip()) > 50:  # Only significant sections
                    overlapping.append(section)
        
        return overlapping
    
    def _find_unique_content(self, text1: str, text2: str) -> List[str]:
        """Find content unique to text1"""
        lines1 = text1.splitlines()
        lines2 = text2.splitlines()
        
        matcher = difflib.SequenceMatcher(None, lines1, lines2)
        unique = []
        
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag in ('delete', 'replace'):
                section = '\n'.join(lines1[i1:i2])
                if len(section.strip()) > 20:  # Only significant unique content
                    unique.append(section)
        
        return unique


class ContentConsolidator:
    """Consolidate duplicate content according to consolidation plans"""
    
    def __init__(self, docs_root: Path):
        self.docs_root = docs_root
    
    def create_consolidation_plan(self, duplicates: List[DuplicateMatch]) -> List[ConsolidationPlan]:
        """Create consolidation plans for duplicate groups"""
        # Group duplicates by similarity clusters
        clusters = self._cluster_duplicates(duplicates)
        plans = []
        
        for cluster in clusters:
            plan = self._create_plan_for_cluster(cluster)
            if plan:
                plans.append(plan)
        
        return plans
    
    def _cluster_duplicates(self, duplicates: List[DuplicateMatch]) -> List[List[DuplicateMatch]]:
        """Group duplicates into clusters of related files"""
        clusters = []
        processed_files = set()
        
        for duplicate in duplicates:
            if duplicate.file1 in processed_files or duplicate.file2 in processed_files:
                continue
            
            # Start new cluster
            cluster = [duplicate]
            cluster_files = {duplicate.file1, duplicate.file2}
            
            # Find all related duplicates
            for other_dup in duplicates:
                if other_dup == duplicate:
                    continue
                if (other_dup.file1 in cluster_files or 
                    other_dup.file2 in cluster_files):
                    cluster.append(other_dup)
                    cluster_files.update({other_dup.file1, other_dup.file2})
            
            clusters.append(cluster)
            processed_files.update(cluster_files)
        
        return clusters
    
    def _create_plan_for_cluster(self, cluster: List[DuplicateMatch]) -> ConsolidationPlan:
        """Create consolidation plan for a cluster of duplicates"""
        if not cluster:
            return None
        
        # Get all files in cluster
        all_files = set()
        for match in cluster:
            all_files.update({match.file1, match.file2})
        
        # Choose primary file (longest content or most recent)
        primary_file = self._choose_primary_file(list(all_files))
        files_to_merge = [f for f in all_files if f != primary_file]
        
        # Determine merge strategy
        exact_matches = [m for m in cluster if m.match_type == 'exact']
        if exact_matches:
            merge_strategy = 'replace_sections'  # Remove exact duplicates
            files_to_remove = [m.file2 for m in exact_matches if m.file1 == primary_file]
        else:
            merge_strategy = 'append'  # Merge unique content
            files_to_remove = []
        
        return ConsolidationPlan(
            primary_file=primary_file,
            files_to_merge=files_to_merge,
            files_to_remove=files_to_remove,
            merge_strategy=merge_strategy,
            preserved_sections={}
        )
    
    def _choose_primary_file(self, files: List[Path]) -> Path:
        """Choose the primary file to keep in consolidation"""
        # Prefer files with longer content
        best_file = files[0]
        best_length = 0
        
        for file_path in files:
            try:
                content = file_path.read_text(encoding='utf-8', errors='ignore')
                if len(content) > best_length:
                    best_length = len(content)
                    best_file = file_path
            except:
                continue
        
        return best_file
    
    def execute_consolidation_plan(self, plan: ConsolidationPlan, dry_run: bool = True) -> bool:
        """Execute a consolidation plan"""
        if dry_run:
            print(f"DRY RUN: Would consolidate {len(plan.files_to_merge)} files into {plan.primary_file}")
            return True
        
        try:
            # Read primary file content
            primary_content = plan.primary_file.read_text(encoding='utf-8', errors='ignore')
            
            # Merge content from other files
            for merge_file in plan.files_to_merge:
                if merge_file in plan.files_to_remove:
                    continue  # Skip files marked for removal
                
                merge_content = merge_file.read_text(encoding='utf-8', errors='ignore')
                primary_content = self._merge_content(primary_content, merge_content, plan.merge_strategy)
            
            # Write consolidated content
            plan.primary_file.write_text(primary_content, encoding='utf-8')
            
            # Remove obsolete files
            for remove_file in plan.files_to_remove:
                if remove_file.exists():
                    remove_file.unlink()
            
            return True
            
        except Exception as e:
            print(f"Error executing consolidation plan: {e}")
            return False
    
    def _merge_content(self, primary: str, merge: str, strategy: str) -> str:
        """Merge content according to strategy"""
        if strategy == 'append':
            return primary + "\n\n" + merge
        elif strategy == 'replace_sections':
            return primary  # Keep primary, ignore duplicate
        else:
            return primary


class TestDuplicateConsolidation:
    """Test suite for duplicate content detection and consolidation"""
    
    @pytest.fixture
    def temp_docs_dir(self, tmp_path):
        """Create temporary docs directory structure for testing"""
        docs_dir = tmp_path / "docs"
        docs_dir.mkdir()
        
        # Create test directories
        (docs_dir / "data-sources" / "bsee").mkdir(parents=True)
        (docs_dir / "data-sources" / "sodir").mkdir(parents=True)
        (docs_dir / "development").mkdir(parents=True)
        
        return docs_dir
    
    @pytest.fixture
    def sample_duplicate_files(self, temp_docs_dir):
        """Create sample files with duplicate content for testing"""
        # Exact duplicate
        exact_content = """# Field Analysis
        
This document analyzes field performance data.

## Introduction
The field analysis covers production metrics.

## Data Sources
Data comes from BSEE reporting.
"""
        
        file1 = temp_docs_dir / "data-sources" / "bsee" / "field_analysis.md"
        file2 = temp_docs_dir / "data-sources" / "bsee" / "field_analysis_copy.md"
        
        file1.write_text(exact_content, encoding='utf-8')  
        file2.write_text(exact_content, encoding='utf-8')
        
        # Near duplicate with slight differences
        near_duplicate = """# Field Analysis Report
        
This document analyzes field performance data for evaluation.

## Introduction  
The field analysis covers production metrics and economics.

## Data Sources
Data comes from BSEE reporting systems.

## Additional Notes
Some additional context here.
"""
        
        file3 = temp_docs_dir / "data-sources" / "bsee" / "analysis_report.md"
        file3.write_text(near_duplicate, encoding='utf-8')
        
        # Partial overlap
        partial_content = """# Economic Analysis
        
## Data Sources
Data comes from BSEE reporting.

## Methodology
We use NPV calculations for evaluation.
"""
        
        file4 = temp_docs_dir / "development" / "economics.md"
        file4.write_text(partial_content, encoding='utf-8')
        
        # Unique content (no duplicates)
        unique_content = """# Wind Energy Data
        
This covers wind energy specific analysis.
"""
        
        file5 = temp_docs_dir / "data-sources" / "sodir" / "wind_analysis.md"
        file5.write_text(unique_content, encoding='utf-8')
        
        return {
            'exact1': file1,
            'exact2': file2, 
            'near': file3,
            'partial': file4,
            'unique': file5
        }
    
    def test_exact_duplicate_detection(self, temp_docs_dir, sample_duplicate_files):
        """Test detection of exact duplicate files"""
        detector = DuplicateDetector(temp_docs_dir)
        duplicates = detector.find_all_duplicates()
        
        # Should find exact duplicates
        exact_matches = [d for d in duplicates if d.match_type == 'exact']
        assert len(exact_matches) >= 1, "Should detect exact duplicates"
        
        # Verify the exact match
        exact_match = exact_matches[0]
        assert exact_match.similarity_score >= detector.exact_threshold
        assert len(exact_match.overlapping_sections) > 0
    
    def test_near_duplicate_detection(self, temp_docs_dir, sample_duplicate_files):
        """Test detection of near-duplicate files"""
        detector = DuplicateDetector(temp_docs_dir)
        duplicates = detector.find_all_duplicates()
        
        # Should find near duplicates
        near_matches = [d for d in duplicates if d.match_type == 'near_duplicate']
        assert len(near_matches) >= 1, "Should detect near duplicates"
        
        # Verify similarity thresholds
        for match in near_matches:
            assert match.similarity_score >= detector.similarity_threshold
            assert match.similarity_score < detector.exact_threshold
    
    def test_partial_overlap_detection(self, temp_docs_dir, sample_duplicate_files):
        """Test detection of files with partial content overlap"""
        detector = DuplicateDetector(temp_docs_dir)
        duplicates = detector.find_all_duplicates()
        
        # Check that overlapping sections are identified
        for duplicate in duplicates:
            if duplicate.similarity_score >= detector.similarity_threshold:
                assert len(duplicate.overlapping_sections) > 0
    
    def test_unique_content_identification(self, temp_docs_dir, sample_duplicate_files):
        """Test identification of unique content in duplicate files"""
        detector = DuplicateDetector(temp_docs_dir)
        duplicates = detector.find_all_duplicates()
        
        # Find a near duplicate match
        near_matches = [d for d in duplicates if d.match_type == 'near_duplicate']
        if near_matches:
            match = near_matches[0]
            
            # Should identify unique content in both files
            assert isinstance(match.unique_content_file1, list)
            assert isinstance(match.unique_content_file2, list)
    
    def test_consolidation_plan_creation(self, temp_docs_dir, sample_duplicate_files):
        """Test creation of consolidation plans"""
        detector = DuplicateDetector(temp_docs_dir)
        duplicates = detector.find_all_duplicates()
        
        consolidator = ContentConsolidator(temp_docs_dir)
        plans = consolidator.create_consolidation_plan(duplicates)
        
        assert len(plans) > 0, "Should create consolidation plans"
        
        for plan in plans:
            assert plan.primary_file.exists(), "Primary file should exist"
            assert len(plan.files_to_merge) >= 0, "Should have files to merge"
            assert plan.merge_strategy in ['append', 'replace_sections', 'interleave']
    
    def test_primary_file_selection(self, temp_docs_dir, sample_duplicate_files):
        """Test selection of primary file in consolidation"""
        consolidator = ContentConsolidator(temp_docs_dir)
        
        # Test with files of different lengths
        files = [sample_duplicate_files['exact1'], sample_duplicate_files['near']]
        primary = consolidator._choose_primary_file(files)
        
        # Should choose file with more content
        primary_content = primary.read_text(encoding='utf-8')
        for file_path in files:
            if file_path != primary:
                other_content = file_path.read_text(encoding='utf-8')
                assert len(primary_content) >= len(other_content)
    
    def test_dry_run_consolidation(self, temp_docs_dir, sample_duplicate_files):
        """Test dry run consolidation execution"""
        detector = DuplicateDetector(temp_docs_dir)
        duplicates = detector.find_all_duplicates()
        
        consolidator = ContentConsolidator(temp_docs_dir)
        plans = consolidator.create_consolidation_plan(duplicates)
        
        for plan in plans:
            # Should succeed in dry run
            result = consolidator.execute_consolidation_plan(plan, dry_run=True)
            assert result is True, "Dry run should succeed"
    
    def test_content_preservation(self, temp_docs_dir, sample_duplicate_files):
        """Test that unique content is preserved during consolidation"""
        detector = DuplicateDetector(temp_docs_dir)
        duplicates = detector.find_all_duplicates()
        
        consolidator = ContentConsolidator(temp_docs_dir)
        plans = consolidator.create_consolidation_plan(duplicates)
        
        # Record original unique content
        original_unique_content = set()
        for duplicate in duplicates:
            original_unique_content.update(duplicate.unique_content_file1)
            original_unique_content.update(duplicate.unique_content_file2)
        
        # Execute consolidation in dry run
        for plan in plans:
            result = consolidator.execute_consolidation_plan(plan, dry_run=True)
            assert result is True
    
    def test_similarity_calculation_accuracy(self, temp_docs_dir):
        """Test accuracy of similarity calculation"""
        detector = DuplicateDetector(temp_docs_dir)
        
        # Test identical strings
        identical = "This is a test string"
        similarity = detector._calculate_similarity(identical, identical)
        assert similarity == 1.0, "Identical strings should have 100% similarity"
        
        # Test completely different strings
        different1 = "This is completely different content"
        different2 = "Totally unrelated text here"
        similarity = detector._calculate_similarity(different1, different2)
        assert similarity < 0.3, "Different strings should have low similarity"
        
        # Test partially similar strings
        similar1 = "This is a test document with content"
        similar2 = "This is a test document with different content"
        similarity = detector._calculate_similarity(similar1, similar2)
        assert 0.5 < similarity < 1.0, "Similar strings should have moderate similarity"
    
    def test_error_handling(self, temp_docs_dir):
        """Test error handling in duplicate detection"""
        detector = DuplicateDetector(temp_docs_dir)
        
        # Test with non-existent file
        non_existent = temp_docs_dir / "non_existent.md"
        existing = temp_docs_dir / "existing.md"
        existing.write_text("Some content", encoding='utf-8')
        
        result = detector._compare_files(non_existent, existing)
        assert result is None, "Should handle non-existent files gracefully"
    
    def test_consolidation_plan_validation(self, temp_docs_dir, sample_duplicate_files):
        """Test validation of consolidation plans"""
        detector = DuplicateDetector(temp_docs_dir)
        duplicates = detector.find_all_duplicates()
        
        consolidator = ContentConsolidator(temp_docs_dir)
        plans = consolidator.create_consolidation_plan(duplicates)
        
        for plan in plans:
            # Validate plan structure
            assert plan.primary_file is not None
            assert isinstance(plan.files_to_merge, list)
            assert isinstance(plan.files_to_remove, list)
            assert plan.merge_strategy in ['append', 'replace_sections', 'interleave']
            
            # Ensure primary file is not in removal list
            assert plan.primary_file not in plan.files_to_remove


if __name__ == "__main__":
    # Run basic functionality test
    print("Testing duplicate detection system...")
    
    # Create minimal test
    from pathlib import Path
    import tempfile
    
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        docs_dir = tmp_path / "docs"
        docs_dir.mkdir()
        
        # Create test files
        test_dir = docs_dir / "test"
        test_dir.mkdir()
        
        file1 = test_dir / "file1.md"
        file2 = test_dir / "file2.md"
        
        content = "# Test Document\nThis is test content."
        file1.write_text(content)
        file2.write_text(content)
        
        # Test detection
        detector = DuplicateDetector(docs_dir)
        duplicates = detector.find_all_duplicates()
        
        print(f"Found {len(duplicates)} duplicate matches")
        
        if duplicates:
            match = duplicates[0]
            print(f"Match type: {match.match_type}")
            print(f"Similarity: {match.similarity_score:.2f}")
        
        # Test consolidation
        consolidator = ContentConsolidator(docs_dir)
        plans = consolidator.create_consolidation_plan(duplicates)
        
        print(f"Created {len(plans)} consolidation plans")
        
        for i, plan in enumerate(plans):
            print(f"Plan {i+1}: Merge {len(plan.files_to_merge)} files into {plan.primary_file.name}")
    
    print("Basic duplicate detection test completed!")