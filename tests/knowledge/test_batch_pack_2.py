import hashlib
import json
import sys
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from scripts.knowledge import run_batch_pack_2 as bp2


def test_catalog_phase_a_complete_set_is_dot_omae_otc():
    catalog = yaml.safe_load((ROOT / "data/document-index/conference-paper-catalog.yaml").read_text())

    complete = {
        item["name"]
        for item in catalog["conferences"]
        if item.get("indexing_status") == "phase_a_complete"
    }

    assert complete == {"DOT", "OMAE", "OTC"}
    assert "ISOPE" not in complete


def test_safe_open_rejects_reading_conference_pdf_dir():
    with pytest.raises(bp2.PathGuardError):
        bp2.safe_open("/mnt/ace/docs/conferences/DOT/example.pdf")


def test_safe_open_rejects_pathlib_path_objects():
    with pytest.raises(bp2.PathGuardError):
        bp2.safe_open(Path("/mnt/ace/docs/conferences/DOT/example.pdf"))


@pytest.mark.parametrize("mode", ["w", "a", "x", "r+"])
def test_safe_open_rejects_write_modes(mode):
    with pytest.raises(ValueError, match="mode"):
        bp2.safe_open(ROOT / "data/document-index/conference-paper-catalog.yaml", mode)


def test_tokenize_preserves_underscores():
    assert bp2.tokenize_v1("Stress_Concentration in Risers") == [
        "stress_concentration",
        "in",
        "risers",
    ]


@pytest.mark.parametrize(
    ("title", "expected"),
    [
        ("Pipeline integrity for deepwater export lines", ("pipeline", [])),
        ("Riser analysis", ("pipeline", [])),
        ("VIV fatigue in deepwater risers", ("VIV", ["pipeline"])),
        ("VIV jumper fracture stress_concentration", ("VIV", ["pipeline", "structural"])),
        ("VIV fatigue on pipelines", ("VIV", ["pipeline"])),
        ("A general conference welcome note", ("misc", [])),
    ],
)
def test_classify_paper_domain_ranked(title, expected):
    assert bp2.classify_paper_domain_ranked(title) == expected


def test_cross_link_jsonl_schema_rejects_misc_in_secondary():
    candidate = {
        "stub_id": "bp2-pipeline-001",
        "schema_version": "1.2",
        "source_issue": 2369,
        "title": "Pipeline integrity",
        "engineering_domain": "pipeline",
        "secondary_domains": ["pipeline", "misc"],
        "target_wiki": "engineering",
        "target_wiki_path_hint": "concepts/pipeline-integrity.md",
        "paper_count": 2,
        "top_paper_ids": ["DOT-1"],
        "topic_label": "pipeline | integrity",
        "duplicate_candidate_path": None,
        "cluster_quality_caveat": "single-pass-deterministic",
        "cross_link_candidates": [],
        "generated_at": "2026-01-01T00:00:00Z",
        "generator": "scripts/knowledge/run_batch_pack_2.py",
        "generator_version": "1.0",
    }

    with pytest.raises(bp2.SchemaValidationError, match="secondary_domains.*misc"):
        bp2.validate_cross_link_candidate(candidate)


def test_stopwords_sha_is_pinned():
    stopwords_path = ROOT / "scripts/knowledge/data/stopwords_en_v1.txt"
    digest = hashlib.sha256(stopwords_path.read_bytes()).hexdigest()

    assert bp2.STOPWORDS_SHA == digest


def test_runner_dot_subslice_outputs_report_and_jsonl(tmp_path):
    report = tmp_path / "report.md"
    links = tmp_path / "links.jsonl"
    skipped = tmp_path / "skipped.jsonl"

    result = bp2.run_batch_pack_2(
        ROOT / "data/document-index/conference-paper-catalog.yaml",
        ROOT / "data/document-index/conference-phase-a-results.jsonl",
        report,
        cross_link_path=links,
        skipped_path=skipped,
        collections=["DOT"],
        now="2026-01-01T00:00:00Z",
    )

    assert result.processed_collections == ["DOT"]
    assert result.deferred_collections["ISOPE"] == "not_indexed"
    assert result.paper_count > 0
    assert report.exists()
    assert links.exists()
    assert skipped.exists()

    body = report.read_text()
    assert "Processed collections: DOT" in body
    assert "## ISOPE re-index follow-on (proposed body)" in body

    first_link = json.loads(links.read_text().splitlines()[0])
    bp2.validate_cross_link_candidate(first_link)
    assert first_link["generated_at"] == "2026-01-01T00:00:00Z"


def test_runner_dot_subslice_is_idempotent_with_fixed_now(tmp_path):
    outputs = []
    for idx in range(2):
        report = tmp_path / f"report-{idx}.md"
        links = tmp_path / f"links-{idx}.jsonl"
        skipped = tmp_path / f"skipped-{idx}.jsonl"
        bp2.run_batch_pack_2(
            ROOT / "data/document-index/conference-paper-catalog.yaml",
            ROOT / "data/document-index/conference-phase-a-results.jsonl",
            report,
            cross_link_path=links,
            skipped_path=skipped,
            collections=["DOT"],
            now="2026-01-01T00:00:00Z",
        )
        outputs.append((report.read_bytes(), links.read_bytes(), skipped.read_bytes()))

    assert outputs[0] == outputs[1]
