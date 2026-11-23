"""Tests for TDD fixture curation — group extracted examples by topic."""

import json
import os
import tempfile

import pytest
import yaml


@pytest.fixture
def sample_reports():
    """Create temp dir with sample extraction reports."""
    with tempfile.TemporaryDirectory() as tmpdir:
        reports_dir = os.path.join(tmpdir, "reports")
        os.makedirs(reports_dir)

        # Report with stability examples
        r1 = {
            "document": "EN400-Chapter4",
            "worked_examples": [
                {
                    "number": "4.1",
                    "title": "GZ from cross curves",
                    "expected_value": 0.94,
                    "output_unit": "ft",
                    "input_count": 3,
                },
                {
                    "number": "4.2",
                    "title": "Free surface correction",
                    "expected_value": 0.555,
                    "output_unit": "ft",
                    "input_count": 5,
                },
            ],
        }
        with open(os.path.join(reports_dir, "en400-ch4-extraction-report.yaml"), "w") as f:
            yaml.dump(r1, f)

        # Report with resistance examples
        r2 = {
            "document": "EN400-Chapter7",
            "worked_examples": [
                {
                    "number": "7.1",
                    "title": "SHP from EHP",
                    "expected_value": 50000.0,
                    "output_unit": "HP",
                    "input_count": 2,
                },
            ],
        }
        with open(os.path.join(reports_dir, "en400-ch7-extraction-report.yaml"), "w") as f:
            yaml.dump(r2, f)

        # Report with no examples
        r3 = {
            "document": "SOLAS",
            "worked_examples": [],
        }
        with open(os.path.join(reports_dir, "solas-extraction-report.yaml"), "w") as f:
            yaml.dump(r3, f)

        yield {
            "reports_dir": reports_dir,
            "output_dir": os.path.join(tmpdir, "fixtures"),
            "jsonl_path": os.path.join(tmpdir, "worked_examples.jsonl"),
        }


class TestCollectExamples:
    """Collect worked examples from extraction reports."""

    def test_collects_from_multiple_reports(self, sample_reports):
        from scripts.data.doc_intelligence.curate_tdd_fixtures import (
            collect_examples_from_reports,
        )

        examples = collect_examples_from_reports(
            sample_reports["reports_dir"]
        )
        assert len(examples) == 3

    def test_skips_empty_reports(self, sample_reports):
        from scripts.data.doc_intelligence.curate_tdd_fixtures import (
            collect_examples_from_reports,
        )

        examples = collect_examples_from_reports(
            sample_reports["reports_dir"]
        )
        docs = {e["source_book"] for e in examples}
        assert "SOLAS" not in docs

    def test_sets_use_as_test_flag(self, sample_reports):
        from scripts.data.doc_intelligence.curate_tdd_fixtures import (
            collect_examples_from_reports,
        )

        examples = collect_examples_from_reports(
            sample_reports["reports_dir"]
        )
        testable = [e for e in examples if e["use_as_test"]]
        assert len(testable) >= 2  # those with input_count > 0


class TestMergeIntoJSONL:
    """Merge deep examples into worked_examples.jsonl."""

    def test_merge_creates_jsonl(self, sample_reports):
        from scripts.data.doc_intelligence.curate_tdd_fixtures import (
            collect_examples_from_reports,
            merge_into_jsonl,
        )

        examples = collect_examples_from_reports(
            sample_reports["reports_dir"]
        )
        # Write some existing shallow records
        with open(sample_reports["jsonl_path"], "w") as f:
            f.write(json.dumps({"number": "4.1", "title": "old"}) + "\n")

        stats = merge_into_jsonl(
            examples, sample_reports["jsonl_path"]
        )
        assert stats["deep_added"] == 3
        assert stats["total"] >= 3

    def test_deep_overwrites_shallow(self, sample_reports):
        from scripts.data.doc_intelligence.curate_tdd_fixtures import (
            collect_examples_from_reports,
            merge_into_jsonl,
        )

        examples = collect_examples_from_reports(
            sample_reports["reports_dir"]
        )
        with open(sample_reports["jsonl_path"], "w") as f:
            f.write(json.dumps({
                "number": "4.1",
                "title": "GZ from cross curves",
                "source_book": "EN400-Chapter4",
            }) + "\n")

        merge_into_jsonl(examples, sample_reports["jsonl_path"])

        with open(sample_reports["jsonl_path"]) as f:
            records = [json.loads(l) for l in f if l.strip()]

        # Should not have duplicate — deep replaces shallow
        ex41 = [r for r in records if r.get("number") == "4.1"
                and r.get("source_book") == "EN400-Chapter4"]
        assert len(ex41) == 1
        assert ex41[0]["extraction_source"] == "deep"
