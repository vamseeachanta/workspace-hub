from __future__ import annotations

import importlib.util
from pathlib import Path


def _load_html_module():
    repo_root = Path(__file__).resolve().parents[2]
    script_path = repo_root / "scripts" / "work-queue" / "generate-html-review.py"
    spec = importlib.util.spec_from_file_location("generate_html_review", script_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_collect_test_evidence_detects_missing_files(tmp_path: Path):
    mod = _load_html_module()
    evidence = mod.collect_test_evidence(str(tmp_path))

    assert evidence["example_pack_present"] is False
    assert evidence["variation_tests_present"] is False
    assert "No variation-test summary available" in evidence["variation_summary"]


def test_collect_test_evidence_extracts_variation_summary(tmp_path: Path):
    mod = _load_html_module()
    (tmp_path / "example-pack.md").write_text("# Example Pack\n", encoding="utf-8")
    (tmp_path / "variation-test-results.md").write_text(
        "# Variation Test Results\n\nPASS - all variations covered\n- detail\n",
        encoding="utf-8",
    )

    evidence = mod.collect_test_evidence(str(tmp_path))

    assert evidence["example_pack_present"] is True
    assert evidence["variation_tests_present"] is True
    assert evidence["variation_summary"] == "PASS - all variations covered"

