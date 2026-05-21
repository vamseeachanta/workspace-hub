"""Tests for the ACMA private-wiki promotion ledger (issue #2747).

The tests exercise:
- schema/field validation (fail-closed)
- readiness classification (5 labels)
- "scored != approved" gate separation
- public-output gate enforcement
- dashboard/report summary
- revision lineage preservation
"""
from __future__ import annotations

import copy
from pathlib import Path

import pytest
import yaml

from client_llm_wiki import promotion_ledger as pl


REPO_ROOT = Path(__file__).resolve().parents[2]
EXAMPLE_YAML = (
    REPO_ROOT
    / "templates"
    / "client-llm-wiki"
    / "ledgers"
    / "promotion-ledger.example.yml"
)


def _base_entry() -> dict:
    """A clean, fully-scored, private-wiki-cleared entry. Tests mutate copies."""
    return {
        "source_id": "ACME-SOURCE-0001",
        "source_doc_key": "ACME-DOC-0001",
        "source_path": "/mnt/ace/acme/projectX/report.pdf",
        "source_class": "readable-raw-data",
        "input_residency": "private-client",
        "output_residency": "private-wiki",
        "readable_derivative_path": "derivatives/acme/projectX/report.md",
        "private_wiki_page": "pages/acme/projectX/report.md",
        "extraction": {
            "version": 2,
            "method": "pymupdf",
            "tool_version": "1.24.0",
            "extracted_at": "2026-05-21T10:15:00Z",
        },
        "confidence": {
            "raw_source_presence": 0.95,
            "readability_or_ocr_quality": 0.85,
            "extraction_completeness": 0.80,
            "metadata_completeness": 0.75,
            "citation_quality": 0.80,
            "privacy_redaction_classification": 0.90,
            "engineering_domain_confidence": 0.85,
            "report_readiness": 0.80,
            "overall": 0.82,
        },
        "score_metadata": {
            "scored_by": "human:vamsee",
            "scored_with": "manual-review:v1",
            "scored_at": "2026-05-21T11:00:00Z",
            "rationale_bucket": "human_review",
        },
        "promotion": {
            "status": "client_ready",
            "private_wiki_allowed": True,
            "public_llm_wiki_allowed": False,
            "rationale": "Reviewer + legal signed off on private wiki page.",
            "gates": {
                "reviewer_clearance": True,
                "legal_clearance": True,
                "sanitization_review": False,
                "public_release_clearance": False,
                "private_release_clearance": True,
            },
        },
        "revision_lineage": {
            "current_extraction_version": 2,
            "previous_extraction_versions": [
                {"version": 1, "extracted_at": "2026-04-01T10:00:00Z", "method": "pdftotext"},
                {"version": 0, "extracted_at": "2026-03-01T10:00:00Z", "method": "pdftotext"},
            ],
            "supersedes": None,
            "superseded_by": None,
            "revision_trigger": {
                "revisit_when_models_improve": True,
                "notes": "Re-extract when next OCR rev lands.",
            },
        },
    }


def _base_ledger(entries=None) -> dict:
    return {
        "ledger_version": 0.2,
        "client": "ACME",
        "entries": entries if entries is not None else [_base_entry()],
    }


# ---------- example YAML --------------------------------------------------- #


def test_example_yaml_parses_and_is_structurally_valid():
    """The shipped example YAML must parse and pass structural validation
    (placeholder values are allowed; the example is a schema reference)."""
    data = yaml.safe_load(EXAMPLE_YAML.read_text())
    # Structural validation only — the example uses placeholder values that
    # would not pass strict semantic validation (e.g. nulls for extraction).
    pl.validate_structure(data)


def test_validate_passes_for_fully_populated_entry():
    pl.validate(_base_ledger())


# ---------- fail-closed missing field tests -------------------------------- #


@pytest.mark.parametrize(
    "missing_path",
    [
        ("source_doc_key",),
        ("source_class",),
        ("input_residency",),
        ("output_residency",),
        ("extraction", "version"),
        ("score_metadata",),
        ("score_metadata", "scored_by"),
        ("score_metadata", "scored_at"),
        ("score_metadata", "rationale_bucket"),
        ("promotion", "gates"),
        ("promotion", "gates", "reviewer_clearance"),
        ("revision_lineage",),
        ("revision_lineage", "current_extraction_version"),
        ("revision_lineage", "previous_extraction_versions"),
    ],
)
def test_validate_fails_closed_on_missing_required_field(missing_path):
    entry = _base_entry()
    cursor = entry
    for key in missing_path[:-1]:
        cursor = cursor[key]
    del cursor[missing_path[-1]]
    with pytest.raises(pl.LedgerValidationError):
        pl.validate(_base_ledger([entry]))


def test_validate_fails_closed_on_missing_confidence_dimension():
    entry = _base_entry()
    del entry["confidence"]["report_readiness"]
    with pytest.raises(pl.LedgerValidationError):
        pl.validate(_base_ledger([entry]))


def test_validate_fails_closed_on_missing_overall_confidence():
    entry = _base_entry()
    del entry["confidence"]["overall"]
    with pytest.raises(pl.LedgerValidationError):
        pl.validate(_base_ledger([entry]))


@pytest.mark.parametrize(
    "path_to_null",
    [
        ("extraction", "method"),
        ("extraction", "tool_version"),
        ("extraction", "extracted_at"),
        ("score_metadata", "scored_by"),
        ("score_metadata", "scored_with"),
        ("score_metadata", "scored_at"),
    ],
)
def test_validate_fails_closed_on_null_provenance_or_score_metadata(path_to_null):
    entry = _base_entry()
    cursor = entry
    for key in path_to_null[:-1]:
        cursor = cursor[key]
    cursor[path_to_null[-1]] = None
    with pytest.raises(pl.LedgerValidationError):
        pl.validate(_base_ledger([entry]))


@pytest.mark.parametrize(
    "path_to_blank",
    [
        ("extraction", "method"),
        ("extraction", "tool_version"),
        ("extraction", "extracted_at"),
        ("score_metadata", "scored_by"),
        ("score_metadata", "scored_with"),
        ("score_metadata", "scored_at"),
    ],
)
def test_validate_fails_closed_on_blank_provenance_or_score_metadata(path_to_blank):
    entry = _base_entry()
    cursor = entry
    for key in path_to_blank[:-1]:
        cursor = cursor[key]
    cursor[path_to_blank[-1]] = "   "
    with pytest.raises(pl.LedgerValidationError):
        pl.validate(_base_ledger([entry]))


@pytest.mark.parametrize(
    "field,value",
    [
        ("source_id", None),
        ("source_id", "   "),
        ("source_doc_key", None),
        ("source_doc_key", "   "),
        ("source_path", None),
        ("source_path", ""),
    ],
)
def test_validate_fails_closed_on_blank_identity_and_source_fields(field, value):
    entry = _base_entry()
    entry[field] = value
    with pytest.raises(pl.LedgerValidationError):
        pl.validate(_base_ledger([entry]))


@pytest.mark.parametrize("version", [None, "2", 2.5, True, -1])
def test_validate_fails_closed_on_invalid_extraction_version(version):
    entry = _base_entry()
    entry["extraction"]["version"] = version
    entry["revision_lineage"]["current_extraction_version"] = version
    with pytest.raises(pl.LedgerValidationError):
        pl.validate(_base_ledger([entry]))


# ---------- gate / approval enforcement ------------------------------------ #


def test_public_output_requires_all_clearance_gates():
    """An entry declaring public output must carry sanitization + legal +
    reviewer + public_release_clearance + rationale. Missing any => fail."""
    entry = _base_entry()
    entry["output_residency"] = "public-llm-wiki"
    entry["promotion"]["public_llm_wiki_allowed"] = True
    # All gates default to "missing"; only private gates were set in base.
    with pytest.raises(pl.LedgerValidationError):
        pl.validate(_base_ledger([entry]))


def test_public_output_accepted_when_all_gates_present():
    entry = _base_entry()
    entry["output_residency"] = "public-llm-wiki"
    entry["promotion"]["public_llm_wiki_allowed"] = True
    entry["promotion"]["rationale"] = (
        "Sanitization REDACT pass complete; FLAG-FOR-REVIEW signed off; "
        "legal cleared; reviewer cleared; public release approved."
    )
    entry["promotion"]["gates"] = {
        "reviewer_clearance": True,
        "legal_clearance": True,
        "sanitization_review": True,
        "public_release_clearance": True,
        "private_release_clearance": True,
    }
    pl.validate(_base_ledger([entry]))


def test_public_allowance_requires_nonempty_rationale():
    entry = _base_entry()
    entry["output_residency"] = "public-llm-wiki"
    entry["promotion"]["public_llm_wiki_allowed"] = True
    entry["promotion"]["rationale"] = ""
    entry["promotion"]["gates"] = {
        "reviewer_clearance": True,
        "legal_clearance": True,
        "sanitization_review": True,
        "public_release_clearance": True,
        "private_release_clearance": True,
    }
    with pytest.raises(pl.LedgerValidationError):
        pl.validate(_base_ledger([entry]))


@pytest.mark.parametrize("gate_value", ["true", "false", 1, 0, None])
def test_validate_rejects_non_boolean_gate_values(gate_value):
    entry = _base_entry()
    entry["promotion"]["gates"]["private_release_clearance"] = gate_value
    with pytest.raises(pl.LedgerValidationError):
        pl.validate(_base_ledger([entry]))


@pytest.mark.parametrize("allowance_field", ["private_wiki_allowed", "public_llm_wiki_allowed"])
@pytest.mark.parametrize("allowance_value", ["true", "false", 1, 0, None])
def test_validate_rejects_non_boolean_allowance_values(allowance_field, allowance_value):
    entry = _base_entry()
    entry["promotion"][allowance_field] = allowance_value
    with pytest.raises(pl.LedgerValidationError):
        pl.validate(_base_ledger([entry]))


def test_private_allowance_requires_private_clearance_gates():
    entry = _base_entry()
    entry["promotion"]["private_wiki_allowed"] = True
    entry["promotion"]["gates"]["private_release_clearance"] = False
    with pytest.raises(pl.LedgerValidationError):
        pl.validate(_base_ledger([entry]))


def test_public_residency_requires_public_allowance_flag():
    entry = _base_entry()
    entry["output_residency"] = "public-llm-wiki"
    entry["promotion"]["public_llm_wiki_allowed"] = False
    entry["promotion"]["rationale"] = "Reviewer, legal, sanitization, and public release cleared."
    entry["promotion"]["gates"] = {
        "reviewer_clearance": True,
        "legal_clearance": True,
        "sanitization_review": True,
        "public_release_clearance": True,
        "private_release_clearance": True,
    }
    with pytest.raises(pl.LedgerValidationError):
        pl.validate(_base_ledger([entry]))


def test_classify_does_not_treat_truthy_string_gates_as_ready():
    entry = _base_entry()
    entry["promotion"]["private_wiki_allowed"] = True
    entry["promotion"]["gates"]["reviewer_clearance"] = "true"
    entry["promotion"]["gates"]["private_release_clearance"] = "true"
    assert pl.classify_readiness(entry) == "needs-human-review"


def test_classify_does_not_treat_truthy_string_allowance_as_ready():
    entry = _base_entry()
    entry["promotion"]["private_wiki_allowed"] = "true"
    assert pl.classify_readiness(entry) == "needs-human-review"


# ---------- scored-but-not-approved separation ----------------------------- #


def test_high_score_alone_is_not_client_ready():
    """An entry can have excellent confidence yet lack any release clearance.
    classify_readiness must return needs_human_review, not client_ready."""
    entry = _base_entry()
    entry["promotion"]["private_wiki_allowed"] = False
    entry["promotion"]["gates"]["reviewer_clearance"] = False
    entry["promotion"]["gates"]["private_release_clearance"] = False
    entry["promotion"]["status"] = "client_ready"  # operator may have over-claimed
    assert pl.classify_readiness(entry) == "needs-human-review"


# ---------- threshold classification --------------------------------------- #


def test_classify_not_started_when_extraction_absent():
    entry = _base_entry()
    entry["extraction"]["method"] = None
    entry["extraction"]["tool_version"] = None
    entry["extraction"]["extracted_at"] = None
    entry["extraction"]["version"] = 0
    for k in entry["confidence"]:
        entry["confidence"][k] = 0.0
    entry["score_metadata"]["rationale_bucket"] = "not_started"
    entry["promotion"]["status"] = "not_started"
    entry["promotion"]["private_wiki_allowed"] = False
    entry["promotion"]["gates"]["reviewer_clearance"] = False
    entry["promotion"]["gates"]["legal_clearance"] = False
    entry["promotion"]["gates"]["private_release_clearance"] = False
    assert pl.classify_readiness(entry) == "not-started"


def test_classify_partial_when_low_overall_and_no_clearance():
    entry = _base_entry()
    for k in entry["confidence"]:
        entry["confidence"][k] = 0.4
    entry["confidence"]["overall"] = 0.4
    entry["promotion"]["private_wiki_allowed"] = False
    entry["promotion"]["gates"]["reviewer_clearance"] = False
    entry["promotion"]["gates"]["legal_clearance"] = False
    entry["promotion"]["gates"]["private_release_clearance"] = False
    assert pl.classify_readiness(entry) == "partial"


def test_classify_usable_with_caveats_when_mid_score_no_clearance():
    entry = _base_entry()
    for k in entry["confidence"]:
        entry["confidence"][k] = 0.65
    entry["confidence"]["overall"] = 0.65
    entry["promotion"]["private_wiki_allowed"] = False
    entry["promotion"]["gates"]["reviewer_clearance"] = False
    entry["promotion"]["gates"]["legal_clearance"] = False
    entry["promotion"]["gates"]["private_release_clearance"] = False
    assert pl.classify_readiness(entry) == "usable-with-caveats"


def test_classify_client_ready_when_high_score_and_clearance():
    entry = _base_entry()  # already client-ready scoring + private clearance
    assert pl.classify_readiness(entry) == "client-ready"


def test_classify_needs_human_review_when_high_score_but_low_privacy_dimension():
    """A single weak privacy/redaction confidence dimension must block
    client-ready regardless of overall score (caps logic per README)."""
    entry = _base_entry()
    entry["confidence"]["privacy_redaction_classification"] = 0.2
    assert pl.classify_readiness(entry) == "needs-human-review"


# ---------- dashboard / summary -------------------------------------------- #


def test_summarize_groups_entries_by_readiness():
    not_started = _base_entry()
    not_started["source_id"] = "ACME-SOURCE-0002"
    not_started["extraction"]["method"] = None
    not_started["extraction"]["tool_version"] = None
    not_started["extraction"]["extracted_at"] = None
    not_started["extraction"]["version"] = 0
    for k in not_started["confidence"]:
        not_started["confidence"][k] = 0.0
    not_started["score_metadata"]["rationale_bucket"] = "not_started"
    not_started["promotion"]["status"] = "not_started"
    not_started["promotion"]["private_wiki_allowed"] = False
    not_started["promotion"]["gates"] = {
        "reviewer_clearance": False,
        "legal_clearance": False,
        "sanitization_review": False,
        "public_release_clearance": False,
        "private_release_clearance": False,
    }

    partial = copy.deepcopy(not_started)
    partial["source_id"] = "ACME-SOURCE-0003"
    for k in partial["confidence"]:
        partial["confidence"][k] = 0.4
    partial["confidence"]["overall"] = 0.4
    partial["extraction"]["method"] = "pdftotext"
    partial["extraction"]["tool_version"] = "4.04"
    partial["extraction"]["extracted_at"] = "2026-05-10T00:00:00Z"
    partial["extraction"]["version"] = 1

    ready = _base_entry()  # ACME-SOURCE-0001 client-ready
    summary = pl.summarize(_base_ledger([not_started, partial, ready]))

    assert summary["counts"]["not-started"] == 1
    assert summary["counts"]["partial"] == 1
    assert summary["counts"]["client-ready"] == 1
    assert summary["counts"]["usable-with-caveats"] == 0
    assert summary["counts"]["needs-human-review"] == 0

    ready_ids = {e["source_id"] for e in summary["ready"]}
    blocked_ids = {e["source_id"] for e in summary["blocked"]}
    assert ready_ids == {"ACME-SOURCE-0001"}
    assert blocked_ids == {"ACME-SOURCE-0002", "ACME-SOURCE-0003"}


def test_summarize_surfaces_low_confidence_items():
    weak = _base_entry()
    weak["source_id"] = "ACME-SOURCE-0010"
    weak["confidence"]["privacy_redaction_classification"] = 0.1
    summary = pl.summarize(_base_ledger([weak]))
    # Low-confidence dimension must downgrade the entry out of ready set.
    assert summary["counts"]["needs-human-review"] == 1
    assert any(e["source_id"] == "ACME-SOURCE-0010" for e in summary["blocked"])


# ---------- revision lineage ----------------------------------------------- #


def test_revision_lineage_preserves_prior_versions():
    entry = _base_entry()
    assert entry["revision_lineage"]["current_extraction_version"] == 2
    prior_versions = [
        p["version"] for p in entry["revision_lineage"]["previous_extraction_versions"]
    ]
    assert prior_versions == [1, 0]


def test_revision_lineage_current_version_must_match_extraction_version():
    entry = _base_entry()
    entry["revision_lineage"]["current_extraction_version"] = 1  # mismatched
    with pytest.raises(pl.LedgerValidationError):
        pl.validate(_base_ledger([entry]))


def test_revision_lineage_previous_versions_must_be_list():
    entry = _base_entry()
    entry["revision_lineage"]["previous_extraction_versions"] = None
    with pytest.raises(pl.LedgerValidationError):
        pl.validate(_base_ledger([entry]))


def test_revision_lineage_previous_versions_must_have_valid_prior_shape():
    entry = _base_entry()
    entry["revision_lineage"]["previous_extraction_versions"] = [
        {"version": 2, "extracted_at": "2026-05-21T10:15:00Z", "method": "pymupdf"}
    ]
    with pytest.raises(pl.LedgerValidationError):
        pl.validate(_base_ledger([entry]))


def test_revision_lineage_previous_versions_must_be_unique():
    entry = _base_entry()
    entry["revision_lineage"]["previous_extraction_versions"] = [
        {"version": 1, "extracted_at": "2026-04-01T10:00:00Z", "method": "pdftotext"},
        {"version": 1, "extracted_at": "2026-04-02T10:00:00Z", "method": "pymupdf"},
    ]
    with pytest.raises(pl.LedgerValidationError):
        pl.validate(_base_ledger([entry]))
