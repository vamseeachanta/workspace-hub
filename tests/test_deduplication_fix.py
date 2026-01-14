"""
Tests for the deduplication analyzer bug fix.

ABOUTME: Comprehensive test suite for deduplication functionality
ABOUTME: Verifies that duplicate detection works correctly across files
"""

import pytest
import tempfile
from pathlib import Path
from src.utilities.deduplication import DeduplicationAnalyzer, DuplicateCode


class TestDeduplicationBugFix:
    """Test suite verifying the P1 bug fix in deduplication analyzer."""

    @pytest.fixture
    def analyzer(self):
        """Create analyzer instance with minimum block size of 3 lines."""
        return DeduplicationAnalyzer(min_block_size=3)

    @pytest.fixture
    def temp_files(self):
        """Create temporary test files with known duplicate patterns."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            # File 1: Contains duplicated block
            file1 = tmpdir / "file1.py"
            file1.write_text(
                "def helper_function():\n"
                "    x = 10\n"
                "    y = 20\n"
                "    return x + y\n"
            )

            # File 2: Contains SAME duplicated block
            file2 = tmpdir / "file2.py"
            file2.write_text(
                "def helper_function():\n"
                "    x = 10\n"
                "    y = 20\n"
                "    return x + y\n"
            )

            # File 3: Contains unique code (no duplicates)
            file3 = tmpdir / "file3.py"
            file3.write_text(
                "def unique_function():\n"
                "    a = 100\n"
                "    b = 200\n"
                "    return a * b\n"
            )

            yield [file1, file2, file3]

    def test_duplicate_detection_across_files(self, analyzer, temp_files):
        """
        Test that duplicates ARE detected across multiple files.

        This is the core bug fix - previously this would always return 0 duplicates.
        """
        # Analyze all files
        duplicates = analyzer.analyze_files(temp_files)

        # Should find duplicates (identical blocks across files)
        assert len(duplicates) > 0, "Deduplication should find duplicates across files"

        # Find the duplicate block
        found_duplicate = False
        for dup_hash, duplicate in duplicates.items():
            # Should have exactly 2 locations (file1 and file2)
            assert len(duplicate.file_paths) >= 2, \
                f"Expected duplicate to appear in multiple files, got {len(duplicate.file_paths)}"

            # File paths should NOT be 'unknown' (this was the bug!)
            for file_path in duplicate.file_paths:
                assert file_path != 'unknown', \
                    "File paths should be tracked, not marked as 'unknown'"
                assert file_path, "File path should not be empty"

            # Should have proper line numbers
            assert len(duplicate.line_numbers) >= 2, "Should have line numbers for each occurrence"

            found_duplicate = True
            break

        assert found_duplicate, "Should have found at least one duplicate block"

    def test_file_paths_are_preserved(self, analyzer, temp_files):
        """Test that file paths are properly preserved during analysis."""
        duplicates = analyzer.analyze_files(temp_files)

        if duplicates:
            # Check first duplicate
            duplicate = list(duplicates.values())[0]

            # File paths should be strings, not 'unknown'
            for file_path in duplicate.file_paths:
                assert isinstance(file_path, str), "File path should be string"
                assert file_path != 'unknown', "File path should not be 'unknown'"
                assert str(temp_files[0].parent) in file_path or str(temp_files[1].parent) in file_path, \
                    f"File path should contain one of our temp files: {file_path}"

    def test_no_false_positives(self, analyzer, temp_files):
        """Test that unique code is not reported as duplicates."""
        duplicates = analyzer.analyze_files(temp_files)

        # The unique_function in file3 should not appear in duplicates
        for duplicate in duplicates.values():
            # None of the file paths should be ONLY file3
            # (file3 contains unique code, not the duplicated function)
            file3_str = str(temp_files[2])
            if file3_str in duplicate.file_paths:
                # If file3 is in the duplicate, there should be other files too
                assert len(duplicate.file_paths) > 1, \
                    "file3 contains unique code, shouldn't be in duplicates"

    def test_duplicate_line_numbers(self, analyzer, temp_files):
        """Test that line numbers are correctly tracked for each duplicate location."""
        duplicates = analyzer.analyze_files(temp_files)

        if duplicates:
            duplicate = list(duplicates.values())[0]

            # Line numbers should be valid
            for line_num in duplicate.line_numbers:
                assert isinstance(line_num, int), "Line number should be integer"
                assert line_num >= 1, "Line numbers should start from 1"

    def test_consolidation_opportunities_from_fixed_duplicates(self, analyzer, temp_files):
        """Test that consolidation opportunities are generated from detected duplicates."""
        # First, analyze files
        duplicates = analyzer.analyze_files(temp_files)

        # Then find consolidation opportunities
        opportunities = analyzer.find_consolidation_opportunities()

        if duplicates:
            # Should have consolidation opportunities for detected duplicates
            assert len(opportunities) > 0, \
                "Should find consolidation opportunities when duplicates are detected"

            # Verify each opportunity references valid files
            for opp in opportunities:
                assert len(opp.locations) >= 2, \
                    "Consolidation opportunity should reference multiple locations"

    def test_report_generation_with_fixed_duplicates(self, analyzer, temp_files):
        """Test that report generation works correctly after fix."""
        # Analyze and generate report
        duplicates = analyzer.analyze_files(temp_files)
        opportunities = analyzer.find_consolidation_opportunities()
        report = analyzer.generate_report()

        # Report should be non-empty
        assert report, "Report should be generated"
        assert "Deduplication Analysis Report" in report, "Report should have title"

        # If duplicates were found, report should mention them
        if duplicates:
            assert "Duplicate Code Blocks:" in report, "Report should list duplicates"
            assert str(len(duplicates)) in report, "Report should show count of duplicates"

    def test_len_locations_check_now_executes(self, analyzer, temp_files):
        """
        Test that the 'if len(locations) > 1' branch now actually executes.

        This was the core bug - the condition never evaluated to True before.
        """
        duplicates = analyzer.analyze_files(temp_files)

        # If we have duplicates, it means the len(locations) > 1 check executed
        assert len(duplicates) > 0, \
            "Bug fix should allow duplicates to be detected (len(locations) > 1 should execute)"

    def test_multiple_duplicates_in_same_file(self, analyzer):
        """Test detection of duplicate blocks within the same file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            # File with repeated code block
            file_with_repeats = tmpdir / "repeated.py"
            file_with_repeats.write_text(
                "def function_a():\n"
                "    x = 10\n"
                "    return x\n"
                "\n"
                "def function_b():\n"
                "    x = 10\n"
                "    return x\n"
            )

            duplicates = analyzer.analyze_files([file_with_repeats])

            # Should detect duplicate within same file
            if duplicates:
                duplicate = list(duplicates.values())[0]
                # Both occurrences should be in same file
                assert len(duplicate.file_paths) >= 2, \
                    "Should detect duplicate blocks within same file"
                assert all(str(file_with_repeats) in fp for fp in duplicate.file_paths), \
                    "Both occurrences should reference the same file"

    def test_exact_hash_matching(self, analyzer):
        """Test that exact code blocks produce same hash and are properly matched."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            # Identical code in two files
            identical_code = "def identical():\n    return 42\n    return 42\n"

            file_a = tmpdir / "a.py"
            file_a.write_text(identical_code)

            file_b = tmpdir / "b.py"
            file_b.write_text(identical_code)

            duplicates = analyzer.analyze_files([file_a, file_b])

            # Should find the identical code as duplicates
            assert len(duplicates) > 0, "Identical code should be detected as duplicates"


class TestDeduplicationEdgeCases:
    """Test edge cases and error conditions."""

    def test_empty_files(self):
        """Test handling of empty files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            empty_file = tmpdir / "empty.py"
            empty_file.write_text("")

            analyzer = DeduplicationAnalyzer()
            duplicates = analyzer.analyze_files([empty_file])

            # Empty file should not cause errors
            assert isinstance(duplicates, dict), "Should handle empty files gracefully"

    def test_very_small_files(self):
        """Test handling of files smaller than min_block_size."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            small_file = tmpdir / "small.py"
            small_file.write_text("x = 1\n")

            analyzer = DeduplicationAnalyzer(min_block_size=5)
            duplicates = analyzer.analyze_files([small_file])

            # Small file should not cause errors
            assert isinstance(duplicates, dict), "Should handle small files gracefully"

    def test_nonexistent_file(self):
        """Test handling of nonexistent files."""
        analyzer = DeduplicationAnalyzer()
        nonexistent = Path("/tmp/this_file_does_not_exist_12345.py")

        # Should handle gracefully without crashing
        duplicates = analyzer.analyze_files([nonexistent])
        assert isinstance(duplicates, dict), "Should handle nonexistent files gracefully"


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "--tb=short"])
