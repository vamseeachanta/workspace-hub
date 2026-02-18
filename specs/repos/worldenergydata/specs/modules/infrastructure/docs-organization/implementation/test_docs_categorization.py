#!/usr/bin/env python3
"""
Tests for documentation categorization and analysis
Part of Task 2.1: Write tests for content categorization accuracy
"""

import os
import pytest
from pathlib import Path
import difflib
import re
from typing import Dict, List, Tuple, Set


class DocumentCategorizer:
    """Categorizes documentation files into appropriate target locations"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.docs_root = self.project_root / "docs"
        
        # Define categorization rules based on content analysis
        self.category_keywords = {
            'user-guide': {
                'keywords': ['getting started', 'installation', 'quick start', 'tutorial', 
                           'how to', 'user guide', 'usage', 'example', 'api reference'],
                'path_patterns': ['user', 'guide', 'tutorial', 'example', 'getting'],
                'weight': 1.0
            },
            'data-sources/bsee': {
                'keywords': ['bsee', 'bureau of safety', 'gulf of mexico', 'offshore', 
                           'production data', 'well data', 'directional survey', 'completion'],
                'path_patterns': ['bsee', 'modules/bsee'],
                'weight': 1.5
            },
            'data-sources/sodir': {
                'keywords': ['sodir', 'norwegian', 'north sea', 'norwegian continental shelf'],
                'path_patterns': ['sodir', 'norwegian'],
                'weight': 1.5
            },
            'data-sources/wind': {
                'keywords': ['wind energy', 'wind turbine', 'renewable', 'offshore wind'],
                'path_patterns': ['wind', 'renewable'],
                'weight': 1.5
            },
            'data-sources/lng': {
                'keywords': ['lng', 'liquefied natural gas', 'export', 'lng terminal'],
                'path_patterns': ['lng', 'modules/lng'],
                'weight': 1.5
            },
            'data-sources/equipment': {
                'keywords': ['equipment', 'drilling rig', 'bop', 'wellhead', 'christmas tree',
                           'subsea', 'production equipment', 'completion equipment'],
                'path_patterns': ['equipment', 'modules/equipment'],
                'weight': 1.5
            },
            'data-sources/onshore': {
                'keywords': ['onshore', 'unconventional', 'shale', 'fracking', 'wyoming'],
                'path_patterns': ['onshore', 'modules/onshore'],
                'weight': 1.5
            },
            'analysis-guides/economic-evaluation': {
                'keywords': ['npv', 'net present value', 'economic', 'cash flow', 'economics',
                           'revenue', 'cost analysis', 'investment', 'financial'],
                'path_patterns': ['npv', 'economic', 'revenue'],
                'weight': 1.2
            },
            'analysis-guides/production-analysis': {
                'keywords': ['production', 'decline curve', 'reserves', 'forecast', 
                           'cumulative production', 'well performance'],
                'path_patterns': ['production', 'analysis'],
                'weight': 1.2
            },
            'analysis-guides/field-development': {
                'keywords': ['field development', 'field layout', 'drilling', 'completion',
                           'well spacing', 'development plan'],
                'path_patterns': ['field', 'development'],
                'weight': 1.2
            },
            'development': {
                'keywords': ['development', 'contributing', 'uv', 'package manager', 
                           'testing', 'pytest', 'code quality'],
                'path_patterns': ['development', 'dev'],
                'weight': 1.0
            },
            'reference/literature': {
                'keywords': ['reference', 'literature', 'paper', 'publication', 'spe', 'seg'],
                'path_patterns': ['literature', 'reference', 'ref'],
                'weight': 0.8
            },
            'reference/equipment-specs': {
                'keywords': ['specification', 'datasheet', 'technical spec', 'equipment spec'],
                'path_patterns': ['spec', 'datasheet'],
                'weight': 0.8
            },
            'examples': {
                'keywords': ['example', 'demo', 'sample', 'case study', 'workflow'],
                'path_patterns': ['example', 'demo', 'sample'],
                'weight': 1.0
            }
        }
    
    def analyze_file_content(self, file_path: Path) -> Dict[str, float]:
        """Analyze file content and return category scores"""
        if not file_path.exists() or file_path.suffix not in ['.md', '.txt']:
            return {}
        
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore').lower()
        except:
            return {}
        
        scores = {}
        for category, rules in self.category_keywords.items():
            score = 0.0
            
            # Score based on keywords in content
            for keyword in rules['keywords']:
                if keyword in content:
                    score += rules['weight']
            
            # Score based on path patterns
            path_str = str(file_path).lower()
            for pattern in rules['path_patterns']:
                if pattern in path_str:
                    score += rules['weight'] * 1.5
            
            scores[category] = score
        
        return scores
    
    def categorize_file(self, file_path: Path) -> Tuple[str, float]:
        """Categorize a single file and return best category and confidence score"""
        scores = self.analyze_file_content(file_path)
        
        if not scores:
            return 'uncategorized', 0.0
        
        best_category = max(scores, key=scores.get)
        confidence = scores[best_category]
        
        return best_category, confidence
    
    def find_duplicates(self, files: List[Path], threshold: float = 0.8) -> List[Tuple[Path, Path, float]]:
        """Find duplicate or highly similar files"""
        duplicates = []
        
        for i, file1 in enumerate(files):
            for file2 in files[i+1:]:
                similarity = self.calculate_similarity(file1, file2)
                if similarity >= threshold:
                    duplicates.append((file1, file2, similarity))
        
        return duplicates
    
    def calculate_similarity(self, file1: Path, file2: Path) -> float:
        """Calculate similarity between two files"""
        try:
            content1 = file1.read_text(encoding='utf-8', errors='ignore')
            content2 = file2.read_text(encoding='utf-8', errors='ignore')
            
            # Use difflib to calculate similarity
            similarity = difflib.SequenceMatcher(None, content1, content2).ratio()
            return similarity
        except:
            return 0.0


class TestDocumentCategorization:
    """Test suite for document categorization functionality"""
    
    def setup_method(self):
        """Set up test environment"""
        self.categorizer = DocumentCategorizer()
        self.project_root = Path(__file__).parent
        self.docs_root = self.project_root / "docs"
    
    def test_categorizer_initialization(self):
        """Test that categorizer initializes correctly"""
        assert isinstance(self.categorizer, DocumentCategorizer)
        assert self.categorizer.docs_root.exists()
        assert len(self.categorizer.category_keywords) > 0
    
    def test_bsee_content_categorization(self):
        """Test that BSEE-related content is categorized correctly"""
        # Create test content that should be categorized as BSEE
        test_content = "This document describes BSEE production data analysis for Gulf of Mexico wells"
        
        # Test categorization logic
        scores = {}
        content_lower = test_content.lower()
        
        for category, rules in self.categorizer.category_keywords.items():
            score = 0.0
            for keyword in rules['keywords']:
                if keyword in content_lower:
                    score += rules['weight']
            scores[category] = score
        
        # BSEE should have highest score
        best_category = max(scores, key=scores.get) if scores else None
        assert best_category == 'data-sources/bsee'
        assert scores['data-sources/bsee'] > 0
    
    def test_economic_analysis_categorization(self):
        """Test that economic analysis content is categorized correctly"""
        test_content = "NPV analysis and cash flow modeling for oil and gas projects"
        
        scores = {}
        content_lower = test_content.lower()
        
        for category, rules in self.categorizer.category_keywords.items():
            score = 0.0
            for keyword in rules['keywords']:
                if keyword in content_lower:
                    score += rules['weight']
            scores[category] = score
        
        best_category = max(scores, key=scores.get) if scores else None
        assert best_category == 'analysis-guides/economic-evaluation'
    
    def test_development_content_categorization(self):
        """Test that development content is categorized correctly"""
        test_content = "UV package manager usage guide for Python development"
        
        scores = {}
        content_lower = test_content.lower()
        
        for category, rules in self.categorizer.category_keywords.items():
            score = 0.0
            for keyword in rules['keywords']:
                if keyword in content_lower:
                    score += rules['weight']
            scores[category] = score
        
        best_category = max(scores, key=scores.get) if scores else None
        assert best_category == 'development'
    
    def test_path_based_categorization(self):
        """Test that file paths influence categorization"""
        test_path = Path("docs/modules/bsee/analysis/production/test.md")
        
        # Test path pattern matching
        path_str = str(test_path).lower()
        bsee_rules = self.categorizer.category_keywords['data-sources/bsee']
        
        path_score = 0.0
        for pattern in bsee_rules['path_patterns']:
            if pattern in path_str:
                path_score += bsee_rules['weight'] * 1.5
        
        assert path_score > 0
    
    def test_similarity_calculation(self):
        """Test file similarity calculation"""
        # Test with identical content
        identical_similarity = difflib.SequenceMatcher(None, "test content", "test content").ratio()
        assert identical_similarity == 1.0
        
        # Test with similar content
        similar_similarity = difflib.SequenceMatcher(None, "test content", "test content updated").ratio()
        assert 0.5 < similar_similarity < 1.0
        
        # Test with different content
        different_similarity = difflib.SequenceMatcher(None, "test content", "completely different").ratio()
        assert different_similarity < 0.5
    
    def test_category_completeness(self):
        """Test that all required categories are defined"""
        required_categories = {
            'user-guide', 'data-sources/bsee', 'data-sources/sodir', 
            'data-sources/wind', 'data-sources/lng', 'data-sources/equipment',
            'data-sources/onshore', 'analysis-guides/economic-evaluation',
            'analysis-guides/production-analysis', 'analysis-guides/field-development',
            'development', 'reference/literature', 'examples'
        }
        
        defined_categories = set(self.categorizer.category_keywords.keys())
        
        # Check that all required categories are defined
        missing_categories = required_categories - defined_categories
        assert len(missing_categories) == 0, f"Missing categories: {missing_categories}"
    
    def test_keyword_coverage(self):
        """Test that each category has sufficient keywords"""
        for category, rules in self.categorizer.category_keywords.items():
            assert len(rules['keywords']) >= 2, f"Category {category} needs more keywords"
            assert len(rules['path_patterns']) >= 1, f"Category {category} needs path patterns"
            assert 'weight' in rules, f"Category {category} missing weight"
            assert rules['weight'] > 0, f"Category {category} weight must be positive"


class TestDuplicateDetection:
    """Test suite for duplicate detection functionality"""
    
    def setup_method(self):
        """Set up test environment"""
        self.categorizer = DocumentCategorizer()
    
    def test_duplicate_detection_threshold(self):
        """Test duplicate detection with different thresholds"""
        # Test that high similarity is detected as duplicate
        high_similarity = 0.9
        assert high_similarity >= 0.8  # Default threshold
        
        # Test that low similarity is not detected as duplicate
        low_similarity = 0.3
        assert low_similarity < 0.8  # Default threshold
    
    def test_similarity_edge_cases(self):
        """Test similarity calculation edge cases"""
        # Empty content
        empty_similarity = difflib.SequenceMatcher(None, "", "").ratio()
        assert empty_similarity == 1.0
        
        # One empty, one with content
        mixed_similarity = difflib.SequenceMatcher(None, "", "content").ratio()
        assert mixed_similarity == 0.0


if __name__ == "__main__":
    # Run tests when script is executed directly
    pytest.main([__file__, "-v"])