from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "docs/standards/TIER1_INDEXING_AND_CODE_PLACEMENT_CONTRACT.md"
CHECKLIST = ROOT / "docs/standards/TIER1_INDEXING_CHECKLIST.md"
DOCS_README = ROOT / "docs/README.md"
STALE_REFERENCE_TEST = ROOT / "tests/docs/test_banned_stale_references.py"

NEGATIVE_SCORECARD_AUTHORITY = (
    "MUST NOT treat any tier-1 indexing scorecard under docs/reports/ "
    "as required canonical authority"
)
ALLOWED_STATUSES = {"present", "partial", "missing", "not-applicable"}
SCOPE_REPOS = {"workspace-hub", "digitalmodel", "assetutilities", "aceengineer-website"}


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _section(text: str, heading: str) -> str:
    pattern = rf"^## {re.escape(heading)}\n(?P<body>.*?)(?=^## |\Z)"
    match = re.search(pattern, text, flags=re.MULTILINE | re.DOTALL)
    assert match, f"missing section: {heading}"
    return match.group("body")


def test_tier1_contract_doc_exists() -> None:
    assert CONTRACT.exists()


def test_tier1_contract_requires_trusted_routing_surfaces_and_authorities() -> None:
    text = _read(CONTRACT)

    required_phrases = [
        "AGENTS.md",
        "README.md",
        "docs/README.md",
        "docs/maps/<repo>-operator-map.md",
        "docs/registry/module-routing.yaml",
        "Required canonical machine-readable registry",
        "code/tests/docs routing table",
        "source-hygiene rules",
        "docs/standards/CONTROL_PLANE_CONTRACT.md",
        "authority for canonical repo entry points and routing surfaces",
        "docs/standards/FILE_STRUCTURE_TAXONOMY.md",
        "authority for baseline top-level repo anatomy",
    ]

    for phrase in required_phrases:
        assert phrase in text


def test_tier1_contract_requires_repo_vs_bulk_artifact_store_rule() -> None:
    text = _read(CONTRACT)

    assert "repo-vs-bulk-artifact-store" in text
    assert "bulk-artifact-store" in text
    assert ">= 10 MB" in text
    assert ">= 1000 files" in text
    assert "binding threshold authority: docs/standards/DATA_PLACEMENT.md" in text
    assert "/mnt/ace/data" in text
    assert "current workspace-hub implementation example" in text


def test_tier1_contract_defines_curated_vs_raw_inventory_boundary() -> None:
    text = _read(CONTRACT)

    assert "curated routing surfaces" in text
    assert "raw inventory" in text
    assert "docs/CONTENT_INDEX.md" in text


def test_tier1_contract_defines_legacy_retirement_rule() -> None:
    text = _read(CONTRACT)
    section = _section(text, "Legacy Product-Doc Retirement Rule")

    assert "allowed" in section.lower()
    assert "migration" in section.lower() or "retirement" in section.lower()
    assert "banned" in section.lower()
    assert "active navigation authority" in section or "active routing authority" in section

    categories = re.findall(r"^- \[x\] `[^`]+`", section, flags=re.MULTILINE)
    assert len(categories) >= 3


def test_tier1_contract_links_child_issues_and_daily_freshness_followthrough() -> None:
    text = _read(CONTRACT)
    freshness = _section(text, "Daily Freshness Review")

    for issue in ("#2461", "#2462", "#2463", "#2464", "#2465"):
        assert issue in text

    assert "#2465" in freshness
    assert "daily freshness review" in freshness
    assert "every 24 hours" in freshness or "once per day" in freshness
    assert "refreshing or regenerating `docs/reports/tier-1-indexing-freshness-latest.md`" in freshness


def test_tier1_contract_forbids_scorecard_as_required_canonical_authority() -> None:
    assert NEGATIVE_SCORECARD_AUTHORITY in _read(CONTRACT)


def test_tier1_checklist_covers_all_scope_repos_and_child_issues() -> None:
    text = _read(CHECKLIST)

    for repo in SCOPE_REPOS:
        assert f"repo_name: {repo}" in text

    for issue in ("#2461", "#2462", "#2463", "#2464"):
        assert issue in text


def test_tier1_checklist_repeats_scorecard_negative_authority_rule() -> None:
    assert NEGATIVE_SCORECARD_AUTHORITY in _read(CHECKLIST)


def test_tier1_checklist_records_surface_status_per_repo() -> None:
    text = _read(CHECKLIST)

    for repo in SCOPE_REPOS:
        pattern = rf"repo_name: {re.escape(repo)}(?P<body>.*?)(?=\n### |\Z)"
        match = re.search(pattern, text, flags=re.DOTALL)
        assert match, f"missing checklist block for {repo}"
        body = match.group("body")
        for field in ("operator_map_status", "registry_status", "data_placement_status", "evidence_source"):
            assert f"{field}:" in body
        for field in ("operator_map_status", "registry_status", "data_placement_status"):
            value = re.search(rf"{field}: ([a-z-]+)", body)
            assert value, f"missing value for {field} in {repo}"
            assert value.group(1) in ALLOWED_STATUSES


def test_docs_readme_links_contract_and_checklist() -> None:
    text = _read(DOCS_README)

    assert "standards/TIER1_INDEXING_AND_CODE_PLACEMENT_CONTRACT.md" in text
    assert "standards/TIER1_INDEXING_CHECKLIST.md" in text


def test_new_contract_docs_are_under_curated_stale_reference_guard() -> None:
    text = _read(STALE_REFERENCE_TEST)

    assert '"docs/standards/TIER1_INDEXING_AND_CODE_PLACEMENT_CONTRACT.md"' in text
    assert '"docs/standards/TIER1_INDEXING_CHECKLIST.md"' in text
