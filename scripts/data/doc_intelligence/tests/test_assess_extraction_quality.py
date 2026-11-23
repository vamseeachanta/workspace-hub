"""Tests for assess-extraction-quality — use_as_test flagging + deep preference."""

import pytest

from scripts.data.doc_intelligence.assess_extraction_quality import (
    assess_example,
    merge_deep_over_classifier,
)


# ── assess_example tests ────────────────────────────────────────────


class TestAssessExample:
    def test_use_as_test_true_with_input_and_expected(self):
        ex = {
            "number": "1.2",
            "inputs": [{"symbol": "V", "value": 4000, "unit": "ft3"}],
            "expected_value": 114.32,
            "output_unit": "LT",
            "parser_format": "en400_dnv",
        }
        result = assess_example(ex)
        assert result["use_as_test"] is True
        assert result["extraction_source"] == "deep"

    def test_use_as_test_false_no_inputs(self):
        ex = {
            "number": "2.1",
            "inputs": [],
            "expected_value": 42.0,
            "output_unit": "m",
            "parser_format": "tupper_biran",
        }
        result = assess_example(ex)
        assert result["use_as_test"] is False

    def test_use_as_test_false_no_expected(self):
        ex = {
            "number": "3.1",
            "inputs": [{"symbol": "A", "value": 20.0, "unit": "m2"}],
            "expected_value": None,
            "output_unit": "",
            "parser_format": "en400_dnv",
        }
        result = assess_example(ex)
        assert result["use_as_test"] is False

    def test_preserves_all_fields(self):
        ex = {
            "number": "1.1",
            "title": "Test title",
            "inputs": [{"symbol": "m", "value": 1.0, "unit": "slug"}],
            "expected_value": 32.17,
            "output_unit": "lb",
            "parser_format": "en400_dnv",
            "source_book": "EN400.pdf",
            "page": 17,
            "domain": "naval-architecture",
        }
        result = assess_example(ex)
        assert result["number"] == "1.1"
        assert result["title"] == "Test title"
        assert result["source_book"] == "EN400.pdf"

    def test_attwood_no_inputs_no_test_flag(self):
        ex = {
            "number": "p3",
            "inputs": [],
            "expected_value": 11.15,
            "output_unit": "tons",
            "parser_format": "attwood_pna",
        }
        result = assess_example(ex)
        assert result["use_as_test"] is False


# ── merge_deep_over_classifier tests ────────────────────────────────


class TestMergeDeepOverClassifier:
    def test_deep_preferred_over_classifier(self):
        classifier = [
            {"text": "Example 1.1 stuff", "source": {"document": "a.pdf", "page": 1}},
            {"text": "Example 2.1 stuff", "source": {"document": "a.pdf", "page": 5}},
        ]
        deep = [
            {
                "number": "1.1",
                "source_book": "a.pdf",
                "page": 1,
                "extraction_source": "deep",
            },
        ]
        merged = merge_deep_over_classifier(classifier, deep)
        deep_records = [r for r in merged if r.get("extraction_source") == "deep"]
        assert len(deep_records) == 1

    def test_classifier_kept_when_no_deep(self):
        classifier = [
            {"text": "Example 5.1", "source": {"document": "b.pdf", "page": 10}},
        ]
        deep = []
        merged = merge_deep_over_classifier(classifier, deep)
        assert len(merged) == 1
        assert merged[0].get("extraction_source", "classifier") == "classifier"

    def test_empty_inputs_empty_output(self):
        merged = merge_deep_over_classifier([], [])
        assert merged == []
