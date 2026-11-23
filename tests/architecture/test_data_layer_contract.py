from __future__ import annotations

from pathlib import Path

import re

import yaml

ROOT = Path(__file__).resolve().parents[2]
INVENTORY_PATH = ROOT / "tests/fixtures/architecture/data_source_inventory.yaml"
PROMOTION_CASES_PATH = ROOT / "tests/fixtures/architecture/data_promotion_cases.yaml"
CONTRACT_PATH = ROOT / "docs/architecture/data-layer-contract.md"
INVENTORY_DOC_PATH = ROOT / "docs/architecture/data-source-inventory.md"
GAP_DOC_PATH = ROOT / "docs/architecture/data-boundary-violations-and-gaps.md"
PROMOTION_DOC_PATH = ROOT / "docs/architecture/llm-wiki-data-promotion-gates.md"
FOLLOWUP_ALIAS_PATH = ROOT / "docs/architecture/followups/issue-migrate-ace-data-alias.md"
FOLLOWUP_REPO_PLACEMENT_PATH = ROOT / "docs/architecture/followups/issue-canonical-llm-wiki-repo-placement.md"
LEGAL_DENY_LIST_PATH = ROOT / ".legal-deny-list.yaml"
SCANNED_PUBLIC_ARTIFACTS = [
    CONTRACT_PATH,
    INVENTORY_DOC_PATH,
    GAP_DOC_PATH,
    PROMOTION_DOC_PATH,
    FOLLOWUP_ALIAS_PATH,
    FOLLOWUP_REPO_PLACEMENT_PATH,
    INVENTORY_PATH,
    PROMOTION_CASES_PATH,
]
TEMP_EVIDENCE_PATTERNS = [re.escape("/tmp/2727-evidence")]

REQUIRED_INVENTORY_DOC_COLUMNS = {
    "source_id",
    "source_class",
    "owner",
    "canonical_home",
    "allowed_artifacts",
    "forbidden_artifacts",
    "retention_rule",
    "publication_rule",
    "provenance",
    "license_posture",
    "sensitivity",
    "promotion_gate",
    "output_residency",
}

REQUIRED_SOURCE_KEYS = {
    "source_id",
    "source_class",
    "owner",
    "canonical_home",
    "path_class",
    "source_registry_kind",
    "registry_ref",
    "allowed_artifacts",
    "forbidden_artifacts",
    "retention_rule",
    "publication_rule",
    "provenance",
    "license_posture",
    "sensitivity",
    "promotion_gate",
    "output_residency",
    "runtime_probe",
    "notes",
}

REQUIRED_RUNTIME_PROBE_KEYS = {"command", "machine", "timestamp", "status"}
SEED_SOURCE_CLASSES = {
    "mnt_workspace_control_plane",
    "repo_ecosystem_data",
    "public_collection_data",
    "engineering_reference_data",
    "mounted_standards_literature",
    "client_project_data",
    "llm_wiki_raw_staging",
    "public_llm_wiki_content",
    "generated_index_query_surface",
    "report_artifact_surface",
}


def load_legal_deny_patterns() -> list[tuple[str, int]]:
    deny = yaml.safe_load(LEGAL_DENY_LIST_PATH.read_text())
    flags_by_pattern: list[tuple[str, int]] = []
    for section in ["client_references", "proprietary_tools", "client_infrastructure"]:
        for item in deny.get(section, []):
            pattern = item.get("pattern")
            if not pattern:
                continue
            flags = 0 if item.get("case_sensitive", False) else re.IGNORECASE
            flags_by_pattern.append((pattern, flags))
    assert flags_by_pattern, "legal deny list must provide boundary patterns"
    return flags_by_pattern


def load_inventory() -> dict:
    return yaml.safe_load(INVENTORY_PATH.read_text())


def load_promotion_cases() -> dict:
    return yaml.safe_load(PROMOTION_CASES_PATH.read_text())


def source_rows() -> list[dict]:
    return load_inventory()["sources"]


def by_id(source_id: str) -> dict:
    return {row["source_id"]: row for row in source_rows()}[source_id]


def test_contract_docs_define_all_data_levels_and_crosswalk():
    text = CONTRACT_PATH.read_text()
    for level in ["D-L1", "D-L2", "D-L3", "D-L4"]:
        assert level in text
    assert "Data residence crosswalk" in text
    assert "raw-data" in text
    assert "readable-raw-data" in text
    assert "llm-wiki-private" in text
    assert "llm-wiki-public" in text
    assert "docs/BUSINESS_BRAIN.md" in text
    assert "docs/DATA_RESIDENCE_POLICY.md" in text


def test_data_inventory_required_seed_sources():
    rows = source_rows()
    assert SEED_SOURCE_CLASSES <= {row["source_class"] for row in rows}
    for source_id in [
        "mnt_ace_raw_documents",
        "mnt_local_analysis_repos",
        "worldenergydata_public_sources",
        "digitalmodel_reference_data",
        "mounted_standards_literature",
        "client_present_001",
        "client_private_wiki_target_provisioning_001",
        "llm_wiki_raw_staging",
        "public_llm_wiki",
        "generated_chatbot_index",
    ]:
        assert source_id in {row["source_id"] for row in rows}


def test_every_source_has_owner_provenance_and_bucket_contract_columns():
    allowed_registry_kinds = {
        "mounted_source_registry",
        "repo_registry",
        "document_index_registry",
        "manual_seed",
        "unavailable",
    }
    for row in source_rows():
        assert REQUIRED_SOURCE_KEYS <= row.keys(), row["source_id"]
        assert REQUIRED_RUNTIME_PROBE_KEYS <= row["runtime_probe"].keys(), row["source_id"]
        for key in REQUIRED_SOURCE_KEYS - {"registry_ref"}:
            assert row[key] not in (None, "", []), (row["source_id"], key)
        assert row["source_registry_kind"] in allowed_registry_kinds
        if row["source_registry_kind"] != "unavailable":
            assert row["registry_ref"], row["source_id"]
        assert row["allowed_artifacts"]
        assert row["forbidden_artifacts"]


def test_private_sources_default_non_public_and_redacted():
    for row in source_rows():
        if row["sensitivity"] in {"private", "client_confidential", "licensed_reference"}:
            assert row["output_residency"] != "llm-wiki-public", row["source_id"]
            assert "public llm-wiki" not in " ".join(row["allowed_artifacts"]).lower()
        rendered = yaml.safe_dump(row)
        for pattern, flags in load_legal_deny_patterns():
            assert not re.search(pattern, rendered, flags), row["source_id"]
        assert "[redacted-client-root]" not in rendered.lower()


def test_client_sources_require_private_client_wiki_or_explicit_provisioning_blocker():
    client_rows = [row for row in source_rows() if row["source_class"] == "client_project_data"]
    assert client_rows
    targets = {row["source_id"] for row in source_rows() if row["source_class"] == "private_client_wiki_target"}
    assert "client_private_wiki_target_provisioning_001" in targets
    routed_targets = set()
    for row in client_rows:
        assert row["output_residency"] == "llm-wiki-private"
        assert row["publication_rule"].startswith("No public publication")
        assert row.get("private_wiki_target") in targets or row["source_registry_kind"] == "unavailable"
        if row.get("private_wiki_target"):
            routed_targets.add(row["private_wiki_target"])
        assert "public" in " ".join(row["forbidden_artifacts"]).lower()
    assert "client_private_wiki_target_provisioning_001" in routed_targets
    private_target_rows = [row for row in source_rows() if row["source_class"] == "private_client_wiki_target"]
    unused_targets = {row["source_id"] for row in private_target_rows} - routed_targets
    assert not unused_targets
    redacted_target = by_id("client_private_wiki_target_provisioning_001")
    assert redacted_target["runtime_probe"]["status"] == "redacted_not_publicly_probed"
    assert redacted_target["runtime_probe"]["command"] == "redacted-private-target-probe"


def test_raw_to_public_requires_intermediate_gate():
    cases = load_promotion_cases()["cases"]
    direct_private_public = [case for case in cases if case["case_id"] == "direct_private_raw_to_public_llm_wiki"]
    assert direct_private_public and direct_private_public[0]["expected"] == "deny"
    assert "D-L2" in direct_private_public[0]["required_evidence"]
    allowed_public = [case for case in cases if case["case_id"] == "reviewed_public_domain_to_public_llm_wiki"]
    assert allowed_public and allowed_public[0]["expected"] == "allow"


def test_generated_indexes_inherit_corpus_posture():
    for row in source_rows():
        if row["source_class"] == "generated_index_query_surface":
            assert row["output_residency"] in {"llm-wiki-private", "llm-wiki-public"}
            if "client" in " ".join(row.get("corpus_sources", [])).lower():
                assert row["output_residency"] == "llm-wiki-private"
                assert "public chatbot" in " ".join(row["forbidden_artifacts"]).lower()


def test_human_inventory_matches_yaml_source_ids_and_has_required_bucket_contract_columns():
    text = INVENTORY_DOC_PATH.read_text()
    header_line = next(line for line in text.splitlines() if line.startswith("| source_id |"))
    for column in REQUIRED_INVENTORY_DOC_COLUMNS:
        assert column in header_line
    for row in source_rows():
        assert row["source_id"] in text
        assert row["source_class"] in text
        assert f"`{row['canonical_home']}`" in text
        assert row["retention_rule"] in text
        assert row["publication_rule"] in text
        assert row["provenance"] in text
    assert "/mnt/ace-data" not in [row["canonical_home"] for row in source_rows()]
    assert "delete the /mnt/ace-data symlink" in text


def test_new_public_artifacts_do_not_expose_private_literals_or_temp_evidence_paths():
    deny_patterns = load_legal_deny_patterns() + [(pattern, 0) for pattern in TEMP_EVIDENCE_PATTERNS]
    forbidden_public_literals = ["".join(["ac", "ma"]), "".join(["AC", "MA"]), "/mnt/local-analysis/" + "".join(["ac", "ma"]) + "-llm-wiki"]
    for path in SCANNED_PUBLIC_ARTIFACTS:
        text = path.read_text()
        for pattern, flags in deny_patterns:
            assert not re.search(pattern, text, flags), path
        for literal in forbidden_public_literals:
            assert literal not in text, path


def test_mounted_standards_literature_uses_registry_grounded_canonical_path():
    rows = {row["source_id"]: row for row in source_rows()}
    standards = rows["mounted_standards_literature"]
    assert standards["canonical_home"] == "/mnt/ace/docs/_standards"
    assert standards["registry_ref"] == "data/document-index/mounted-source-registry.yaml"
    registry_text = (ROOT / standards["registry_ref"]).read_text()
    assert "mount_root: /mnt/ace/docs/_standards" in registry_text
    assert standards["runtime_probe"]["command"] == "test -d /mnt/ace/docs/_standards"
    assert standards["runtime_probe"]["status"] == "present_recorded"


def test_absent_runtime_probes_are_marked_absent_not_present():
    for row in source_rows():
        probe = row["runtime_probe"]
        if "not present" in row.get("notes", "").lower() or "not found" in row.get("notes", "").lower():
            assert probe["status"] == "absent_recorded", row["source_id"]


def test_boundary_violation_inventory_present_with_search_evidence_and_follow_up_drafts():
    gap = yaml.safe_load(GAP_DOC_PATH.read_text().split("```yaml", 1)[1].split("```", 1)[0])
    assert gap["searches"]
    for search in gap["searches"]:
        for key in ["command", "machine", "timestamp", "paths_scanned", "excluded_patterns", "matches", "conclusion"]:
            assert key in search
        assert search["conclusion"]
        assert "<private-client-root-denylist-pattern>" not in search["command"]
    issue_titles = {draft["title"] for draft in gap["follow_up_issue_drafts"]}
    assert any("/mnt/ace-data" in title for title in issue_titles)
    assert any("canonical" in title.lower() and "llm-wiki" in title.lower() for title in issue_titles)
    for draft in gap["follow_up_issue_drafts"]:
        assert draft["body_file"]
        assert draft["gh_issue_create_command"].startswith("gh issue create")


def test_promotion_doc_names_llm_wiki_raw_public_and_report_boundaries():
    text = PROMOTION_DOC_PATH.read_text()
    for phrase in [
        "raw/private llm-wiki staging",
        "public llm-wiki",
        "client-facing HTML",
        "limited PDFs",
        "chatbot",
        "<client-private-wiki-root>",
        "docs/BUSINESS_BRAIN.md",
        "docs/DATA_RESIDENCE_POLICY.md",
    ]:
        assert phrase in text
