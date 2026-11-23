"""Tests for table quality filters — WRK-1256.

Tests cover:
1. Content-hash dedup (identical repeated tables)
2. Watermark pattern detection (IHS Licensee, DNV copyright)
3. Min-content gate (≥3 data rows, ≥2 numeric columns)
4. Quality rating integration
"""

import pytest

from scripts.data.doc_intelligence.table_quality import (
    classify_table_quality,
    is_watermark,
    meets_content_threshold,
    dedup_tables,
)


# --- Watermark detection ---

class TestIsWatermark:
    def test_ihs_licensee_watermark(self):
        table = {
            "columns": [""],
            "rows": [
                ["Document provided by IHS Licensee=INSTITUTO MEXICANO DEL PETROLEO/3139900100,"],
                ["User=, 11/08/2002 18:48:34 MST Questions or comments about this message: please"],
                ["call the Document Policy Management Group at 1-800-451-1584."],
            ],
        }
        assert is_watermark(table) is True

    def test_ihs_variant_casing(self):
        table = {
            "columns": [""],
            "rows": [
                ["document provided by IHS licensee=SOME_COMPANY/12345,"],
                ["User=, 01/01/2020 Questions or comments"],
            ],
        }
        assert is_watermark(table) is True

    def test_dnv_copyright_watermark(self):
        table = {
            "columns": [""],
            "rows": [
                ["Det Norske Veritas AS. All rights reserved."],
                ["No reproduction without written permission."],
            ],
        }
        assert is_watermark(table) is True

    def test_real_table_not_watermark(self):
        table = {
            "columns": ["S-N curve", "m1", "loga1"],
            "rows": [
                ["B1", "4.0", "15.117"],
                ["B2", "4.0", "14.885"],
                ["C", "3.0", "12.592"],
            ],
        }
        assert is_watermark(table) is False

    def test_empty_table_not_watermark(self):
        table = {"columns": [], "rows": []}
        assert is_watermark(table) is False


# --- Min-content gate ---

class TestMeetsContentThreshold:
    def test_good_table_passes(self):
        table = {
            "columns": ["Curve", "m", "log_a"],
            "rows": [
                ["B1", "4.0", "15.117"],
                ["B2", "4.0", "14.885"],
                ["C", "3.0", "12.592"],
                ["D", "3.0", "12.164"],
            ],
        }
        assert meets_content_threshold(table) is True

    def test_too_few_rows_fails(self):
        table = {
            "columns": ["A", "B"],
            "rows": [["x", "1.0"], ["y", "2.0"]],
        }
        assert meets_content_threshold(table) is False

    def test_no_numeric_columns_fails(self):
        table = {
            "columns": ["Name", "Type", "Note"],
            "rows": [
                ["alpha", "steel", "ok"],
                ["beta", "copper", "ok"],
                ["gamma", "iron", "ok"],
            ],
        }
        assert meets_content_threshold(table) is False

    def test_empty_rows_fail(self):
        table = {
            "columns": ["A"],
            "rows": [[""], [""], [""]],
        }
        assert meets_content_threshold(table) is False

    def test_single_numeric_column_fails(self):
        """Need ≥2 columns with numeric values."""
        table = {
            "columns": ["Label", "Value"],
            "rows": [
                ["a", "1.0"],
                ["b", "2.0"],
                ["c", "3.0"],
            ],
        }
        # "Label" column has no numerics, "Value" has 3 — only 1 numeric column
        assert meets_content_threshold(table) is False

    def test_two_numeric_columns_passes(self):
        table = {
            "columns": ["X", "Y", "Z"],
            "rows": [
                ["1.0", "2.0", "text"],
                ["3.0", "4.0", "text"],
                ["5.0", "6.0", "text"],
            ],
        }
        assert meets_content_threshold(table) is True


# --- Dedup ---

class TestDedupTables:
    def test_removes_identical_tables(self):
        table_a = {
            "columns": ["A"],
            "rows": [["same content"], ["repeated"]],
        }
        table_b = {
            "columns": ["A"],
            "rows": [["same content"], ["repeated"]],
        }
        table_c = {
            "columns": ["B"],
            "rows": [["different"]],
        }
        result = dedup_tables([table_a, table_b, table_c])
        assert len(result) == 2

    def test_keeps_unique_tables(self):
        tables = [
            {"columns": ["X"], "rows": [["1"]]},
            {"columns": ["Y"], "rows": [["2"]]},
            {"columns": ["Z"], "rows": [["3"]]},
        ]
        result = dedup_tables(tables)
        assert len(result) == 3

    def test_removes_many_duplicates(self):
        """Simulates API RP 2A: 242 identical watermark tables."""
        watermark = {
            "columns": [""],
            "rows": [["IHS Licensee notice"], ["same on every page"]],
        }
        tables = [watermark.copy() for _ in range(242)]
        tables.append({"columns": ["Real"], "rows": [["data"]]})
        result = dedup_tables(tables)
        assert len(result) == 2  # 1 watermark + 1 real

    def test_empty_list(self):
        assert dedup_tables([]) == []


# --- Quality classification ---

class TestClassifyTableQuality:
    def test_watermark_classified_as_junk(self):
        table = {
            "columns": [""],
            "rows": [
                ["Document provided by IHS Licensee=COMPANY/123,"],
                ["User=, 01/01/2020"],
            ],
        }
        assert classify_table_quality(table) == "junk"

    def test_empty_table_classified_as_junk(self):
        table = {"columns": [], "rows": []}
        assert classify_table_quality(table) == "junk"

    def test_below_threshold_classified_as_junk(self):
        table = {
            "columns": ["A"],
            "rows": [[""], [""]],
        }
        assert classify_table_quality(table) == "junk"

    def test_good_table_classified_as_usable(self):
        """≥5 data rows + ≥2 numeric columns = usable."""
        table = {
            "columns": ["Curve", "m", "log_a", "limit"],
            "rows": [
                ["B1", "4.0", "15.117", "106.97"],
                ["B2", "4.0", "14.885", "93.59"],
                ["C", "3.0", "12.592", "73.10"],
                ["D", "3.0", "12.164", "52.63"],
                ["E", "3.0", "12.010", "46.78"],
            ],
        }
        assert classify_table_quality(table) == "usable"

    def test_partial_table(self):
        """3-4 data rows with ≥2 numeric columns = partial."""
        table = {
            "columns": ["Depth", "Pressure", "Temp"],
            "rows": [
                ["100", "200", "25.0"],
                ["200", "400", "30.0"],
                ["300", "600", "35.0"],
            ],
        }
        result = classify_table_quality(table)
        assert result == "partial"
