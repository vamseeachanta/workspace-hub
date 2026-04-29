"""Regression checks for #2521 OCIMF Tandem preview unblocker."""

from __future__ import annotations

import json
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[4]
OCIMF_DOC_KEY = "sha256:5e5f61e785295f0ac849399bb302cb5192ca84c108e6a57e82b8cc83b8b431af"
SUMMARY_PATH = REPO_ROOT / "data/document-index/summaries" / f"{OCIMF_DOC_KEY}.json"
HANDOFF_PATH = REPO_ROOT / "docs/reports/acma-wiki-unblock-2245-handoff.yaml"
SOURCE_PATH = "/mnt/ace/acma-codes/OCIMF/OCIMF-Tandem Mooring and Offloading Guidelines for Conventional Tankers at FPSO Facilities.pdf"


def test_2521_ocimf_summary_artifact_unblocks_preview_gate() -> None:
    assert SUMMARY_PATH.exists(), f"missing #2521 summary artifact: {SUMMARY_PATH}"
    payload = json.loads(SUMMARY_PATH.read_text(encoding="utf-8"))

    assert payload["sha256"] == OCIMF_DOC_KEY
    assert payload["path"] == SOURCE_PATH
    assert payload["ready_for_2227"] is True
    assert payload["issue"] == 2521
    assert payload["downstream_issue"] == 2227
    assert payload["extraction_method"] == "ocr_tesseract_first_pages"
    assert len(payload["text_preview"].strip()) >= 200
    assert len(payload["summary"].strip()) >= 80
    assert "Tandem Mooring" in payload["title"]
    assert "OCIMF" in payload["summary"] or "Oil Companies International Marine Forum" in payload["text_preview"]
    assert "raw_pdf_committed" not in payload


def test_2521_handoff_marks_ocimf_target_ready_without_claiming_csa_ready() -> None:
    assert HANDOFF_PATH.exists(), f"missing handoff: {HANDOFF_PATH}"
    handoff = yaml.safe_load(HANDOFF_PATH.read_text(encoding="utf-8"))
    targets = {item["standard_id"]: item for item in handoff["targets"]}

    assert targets["OCIMF-TANDEM-MOORING"]["ready_for_2227"] is True
    assert targets["OCIMF-TANDEM-MOORING"]["summary_artifact"].endswith(f"{OCIMF_DOC_KEY}.json")
    # CSA has been split to #2522; #2521 must not silently claim CSA readiness.
    for split_target in ("CSA-Z276.1-20", "CSA-Z276.18"):
        if split_target in targets:
            assert targets[split_target]["ready_for_2227"] is False
            assert "#2522" in str(targets[split_target].get("blocker", ""))
