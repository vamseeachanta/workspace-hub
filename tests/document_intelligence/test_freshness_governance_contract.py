from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]
CONTRACT_PATH = REPO_ROOT / "docs/document-intelligence/freshness-governance-contract.md"
CADENCES_PATH = REPO_ROOT / "data/document-index/freshness-cadences.yaml"
REGISTRY_PATH = REPO_ROOT / "data/document-index/intelligence-accessibility-registry.yaml"


def _load_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def test_freshness_governance_contract_locks_scope_and_vocabulary():
    contract = CONTRACT_PATH.read_text(encoding="utf-8")

    required_terms = [
        "FRESH / MODERATE / STALE",
        "nightly / weekly / monthly / quarterly / on-demand",
        "data/document-index/freshness-cadences.yaml",
        "docs/document-intelligence/freshness-cadence-matrix.md",
        "source-of-truth precedence",
        "scanner output",
        "registry metadata",
        "matrix values",
        "#2483",
        "#2484",
    ]

    for term in required_terms:
        assert term in contract


def test_freshness_cadence_registry_declares_governance_schema():
    cadences = _load_yaml(CADENCES_PATH)

    assert cadences["schema_version"] == "1.1.0"
    assert cadences["canonical_artifact"] == "data/document-index/freshness-cadences.yaml"
    assert cadences["derived_human_matrix"] == "docs/document-intelligence/freshness-cadence-matrix.md"
    assert cadences["status_vocabulary"] == ["FRESH", "MODERATE", "STALE"]
    assert cadences["cadence_vocabulary"] == [
        "nightly",
        "weekly",
        "monthly",
        "quarterly",
        "on-demand",
    ]
    assert cadences["source_of_truth_precedence"] == [
        "scanner_output_for_measured_age",
        "freshness_cadences_yaml_for_expected_cadence_and_threshold",
        "intelligence_accessibility_registry_for_asset_metadata",
        "freshness_cadence_matrix_for_human_review",
    ]
    assert cadences["registry_field_contract"]["freshness_cadence"]["allowed_values"] == [
        "nightly",
        "weekly",
        "monthly",
        "quarterly",
        "on-demand",
    ]
    assert cadences["registry_field_contract"]["staleness_status"]["allowed_values"] == [
        "FRESH",
        "MODERATE",
        "STALE",
    ]


def test_accessibility_registry_uses_canonical_cadence_values():
    registry = _load_yaml(REGISTRY_PATH)
    allowed = {"nightly", "weekly", "monthly", "quarterly", "on-demand", None}

    seen = {asset.get("freshness_cadence") for asset in registry["assets"]}
    assert seen <= allowed
    assert "daily" not in seen
