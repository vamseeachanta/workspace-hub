import hashlib
from copy import deepcopy
from pathlib import Path

from jsonschema import Draft202012Validator
import pytest
import yaml

ROOT = Path(__file__).resolve().parents[2]
ARCH = ROOT / "docs/architecture"
SCHEMA_PATH = ARCH / "execution-manifest.schema.yaml"
FIXTURE_PATH = ROOT / "tests/fixtures/architecture/execution_manifest.yaml"
ROUTING_CASES_PATH = ROOT / "tests/fixtures/architecture/execution_routing_cases.yaml"
DATA_SOURCE_INVENTORY_PATH = ROOT / "tests/fixtures/architecture/data_source_inventory.yaml"
ROUTING_POLICY_PATH = ARCH / "execution-routing-policy-view.md"
ENTRY_INVENTORY_PATH = ARCH / "execution-entry-point-inventory.md"
FOLLOW_UP_BACKLOG_PATH = ARCH / "execution-follow-up-issue-backlog.md"
CONTRACT_PATH = ARCH / "execution-layer-contract.md"
WORKSTATION_REGISTRY_PATH = ROOT / "config/workstations/registry.yaml"

REQUIRED_EXECUTION_LEVELS = {"E-L1", "E-L2", "E-L3", "E-L4"}
REQUIRED_MANIFEST_FIELDS = {
    "manifest_id",
    "issue",
    "source_ids",
    "source_registry_kind",
    "source_registry_ref",
    "input_residency",
    "output_residency",
    "tool",
    "machine",
    "provider_tool",
    "command_manifest",
    "regeneration_command",
    "replay_command",
    "environment_pin",
    "outputs",
    "checksums",
    "test_evidence",
    "legal_scan_evidence",
    "review_artifact_paths",
    "promotion_gates",
    "report_eligible",
}
EVIDENCE_FIELDS = {
    "regeneration_command",
    "replay_command",
    "environment_pin",
    "checksums",
    "test_evidence",
    "legal_scan_evidence",
    "review_artifact_paths",
}
INPUT_RESIDENCY_ENUM = {
    "raw_data",
    "readable_raw_data",
    "owner_repo_checkout",
    "target_repo_checkout",
    "domain_private_corpus",
    "registered_client_private_corpus",
    "public_llm_wiki",
}
OUTPUT_RESIDENCY_ENUM = {
    "public_llm_wiki",
    "domain_private_corpus",
    "registered_client_private_corpus",
    "ignored_internal_run_artifact",
    "no_preserve",
}
REQUIRED_OUTPUT_FIELDS = {"path", "kind", "report_handoff", "output_residency"}
REQUIRED_PUBLIC_PROMOTION_GATES = {"provenance", "license", "legal", "sanitization", "owner-review"}
SOURCE_REGISTRY_KIND_ENUM = {
    "mounted_source_registry",
    "repo_registry",
    "document_index_registry",
    "manual_seed",
    "unavailable",
}
RAW_DATA_FORBIDDEN_KEYS = {"raw_data", "data_dump", "client_payload", "source_text"}
DUPLICATED_MACHINE_TRUTH_FIELDS = {
    "hostname:",
    "tailscale_ip:",
    "os:",
    "roles:",
    "capabilities:",
    "agent_clis:",
    "tools:",
}
NAMED_REPOS = {
    "workspace-hub",
    "digitalmodel",
    "assetutilities",
    "worldenergydata",
    "llm-wiki",
    "aceengineer-website",
    "aceengineer-strategy",
}


def load_yaml(path: Path) -> dict:
    assert path.exists(), f"Missing required file: {path}"
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert isinstance(data, dict), f"{path} must contain a YAML mapping"
    return data


def assert_manifest_checksums_match_files(manifest: dict) -> None:
    checksums = manifest.get("checksums", {})
    assert isinstance(checksums, dict), "manifest checksums must be a mapping"
    for output in manifest.get("outputs", []):
        if output.get("report_handoff"):
            assert output["path"] in checksums, f"missing checksum for report handoff output: {output['path']}"
    for relative_path, expected in checksums.items():
        assert isinstance(expected, str), f"checksum for {relative_path} must be a string"
        artifact_path = ROOT / relative_path
        assert artifact_path.is_file(), f"checksum target is missing or not a file: {relative_path}"
        actual = "sha256:" + hashlib.sha256(artifact_path.read_bytes()).hexdigest()
        assert actual == expected.lower(), f"checksum mismatch for {relative_path}: expected {expected}, got {actual}"


def test_execution_levels_are_defined_in_contract():
    text = CONTRACT_PATH.read_text(encoding="utf-8")
    for level in REQUIRED_EXECUTION_LEVELS:
        assert level in text
    assert "does not own raw data" in text
    assert "validation/evidence" in text
    assert "report-layer handoff" in text
    assert "semantic checksum verifier" in text


def test_execution_manifest_required_fields():
    schema = load_yaml(SCHEMA_PATH)
    manifest = load_yaml(FIXTURE_PATH)
    required = set(schema["required"])
    assert REQUIRED_MANIFEST_FIELDS <= required
    assert REQUIRED_MANIFEST_FIELDS <= set(manifest)


def test_execution_manifest_fixture_validates_against_schema_and_registry():
    schema = load_yaml(SCHEMA_PATH)
    manifest = load_yaml(FIXTURE_PATH)
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(manifest)
    assert_manifest_checksums_match_files(manifest)
    inventory = load_yaml(DATA_SOURCE_INVENTORY_PATH)["sources"]
    source_ids = {row["source_id"] for row in inventory}
    assert set(manifest["source_ids"]) <= source_ids
    assert manifest["source_registry_kind"] in SOURCE_REGISTRY_KIND_ENUM
    assert manifest["source_registry_kind"] != "unavailable"


def test_execution_manifest_fixture_checksums_match_files():
    manifest = load_yaml(FIXTURE_PATH)
    assert_manifest_checksums_match_files(manifest)

    forged = deepcopy(manifest)
    first_path = next(iter(forged["checksums"]))
    forged["checksums"][first_path] = "sha256:" + "0" * 64
    with pytest.raises(AssertionError, match="checksum mismatch"):
        assert_manifest_checksums_match_files(forged)

    non_string_checksum = deepcopy(manifest)
    non_string_checksum["checksums"][first_path] = 123
    with pytest.raises(AssertionError, match="must be a string"):
        assert_manifest_checksums_match_files(non_string_checksum)

    omitted_handoff_checksum = deepcopy(manifest)
    handoff_path = next(output["path"] for output in manifest["outputs"] if output.get("report_handoff"))
    omitted_handoff_checksum["checksums"].pop(handoff_path)
    with pytest.raises(AssertionError, match="missing checksum"):
        assert_manifest_checksums_match_files(omitted_handoff_checksum)


def test_execution_manifest_fails_closed_for_unavailable_sources_and_public_gates():
    schema = load_yaml(SCHEMA_PATH)
    validator = Draft202012Validator(schema)
    manifest = load_yaml(FIXTURE_PATH)

    unavailable = deepcopy(manifest)
    unavailable["source_registry_kind"] = "unavailable"
    unavailable["source_registry_ref"] = ""
    unavailable["report_eligible"] = True
    assert list(validator.iter_errors(unavailable)), "unavailable registry must not be report eligible"

    public = deepcopy(manifest)
    public["output_residency"] = "public_llm_wiki"
    public["outputs"][0]["output_residency"] = "public_llm_wiki"
    public["promotion_gates"] = ["legal"]
    assert list(validator.iter_errors(public)), "public output must require the full promotion gate set"

    nested_public = deepcopy(manifest)
    nested_public["output_residency"] = "domain_private_corpus"
    nested_public["outputs"][0]["output_residency"] = "public_llm_wiki"
    nested_public["promotion_gates"] = ["legal"]
    assert list(validator.iter_errors(nested_public)), "public output items must require the full promotion gate set"

    no_handoff = deepcopy(manifest)
    no_handoff["report_eligible"] = True
    for output in no_handoff["outputs"]:
        output["report_handoff"] = False
    assert list(validator.iter_errors(no_handoff)), "report eligibility requires at least one report handoff output"

    failed_legal = deepcopy(manifest)
    failed_legal["report_eligible"] = True
    failed_legal["legal_scan_evidence"]["result"] = "fail"
    assert list(validator.iter_errors(failed_legal)), "report eligibility requires passing legal scan evidence"

    pending_checksum = deepcopy(manifest)
    pending_checksum["report_eligible"] = True
    pending_checksum["checksums"] = {"docs/architecture/execution-layer-contract.md": "pending-final-checksum"}
    assert list(validator.iter_errors(pending_checksum)), "report eligibility requires non-pending checksums"

    placeholder_checksum = deepcopy(manifest)
    placeholder_checksum["report_eligible"] = True
    placeholder_checksum["checksums"] = {
        "docs/architecture/execution-layer-contract.md": "sha256:contract-checksum-required-at-publication"
    }
    assert list(validator.iter_errors(placeholder_checksum)), "report eligibility requires sha256 digest syntax"

    for invalid_checksum in [
        "sha256:" + "a" * 63,
        "sha256:" + "g" * 64,
        "a" * 64,
        123,
    ]:
        invalid_syntax = deepcopy(manifest)
        invalid_syntax["report_eligible"] = False
        invalid_syntax["checksums"] = {"docs/architecture/execution-layer-contract.md": invalid_checksum}
        assert list(validator.iter_errors(invalid_syntax)), f"checksum syntax must reject {invalid_checksum}"

    nested_raw = deepcopy(manifest)
    nested_raw["test_evidence"][0]["source_text"] = "inline raw payload must not validate"
    assert list(validator.iter_errors(nested_raw)), "test evidence must not embed raw/private payload fields"


def test_execution_manifest_closed_residency_vocabularies_and_output_schema():
    schema = load_yaml(SCHEMA_PATH)
    manifest = load_yaml(FIXTURE_PATH)
    assert schema["additionalProperties"] is False
    assert set(schema["propertyNames"]["not"]["enum"]) == RAW_DATA_FORBIDDEN_KEYS
    assert set(schema["properties"]["input_residency"]["enum"]) == INPUT_RESIDENCY_ENUM
    assert set(schema["properties"]["output_residency"]["enum"]) == OUTPUT_RESIDENCY_ENUM
    assert manifest["input_residency"] in INPUT_RESIDENCY_ENUM
    assert manifest["output_residency"] in OUTPUT_RESIDENCY_ENUM
    output_item_schema = schema["properties"]["outputs"]["items"]
    assert output_item_schema["additionalProperties"] is False
    assert REQUIRED_OUTPUT_FIELDS <= set(output_item_schema["required"])
    assert set(output_item_schema["properties"]["output_residency"]["enum"]) == OUTPUT_RESIDENCY_ENUM
    for output in manifest["outputs"]:
        assert REQUIRED_OUTPUT_FIELDS <= set(output)
        assert output["output_residency"] in OUTPUT_RESIDENCY_ENUM


def test_execution_manifest_evidence_fields_complete():
    manifest = load_yaml(FIXTURE_PATH)
    for field in EVIDENCE_FIELDS:
        value = manifest[field]
        assert value not in (None, "", [], {}), f"{field} must be non-empty"
    assert manifest["legal_scan_evidence"]["command"] == "scripts/legal/legal-sanity-scan.sh --diff-only"
    assert manifest["review_artifact_paths"], "review artifacts are required for report handoff"


def test_no_execution_direct_publication():
    schema = load_yaml(SCHEMA_PATH)
    manifest = load_yaml(FIXTURE_PATH)
    promotion_gate_schema = schema["properties"]["promotion_gates"]
    assert set(promotion_gate_schema["items"]["enum"]) == REQUIRED_PUBLIC_PROMOTION_GATES
    if manifest["report_eligible"]:
        assert manifest["test_evidence"], "report eligibility requires tests"
        assert manifest["legal_scan_evidence"]["result"] in {"pass", "pending-required-before-publication"}
        assert manifest["review_artifact_paths"], "report eligibility requires adversarial review artifacts"
        assert manifest["output_residency"] != "public_llm_wiki" or REQUIRED_PUBLIC_PROMOTION_GATES <= set(
            manifest["promotion_gates"]
        ), "public output residency requires complete promotion gates"


def test_routing_policy_references_workstation_registry_without_duplicate_truth():
    registry = load_yaml(WORKSTATION_REGISTRY_PATH)
    policy = ROUTING_POLICY_PATH.read_text(encoding="utf-8")
    assert "config/workstations/registry.yaml" in policy
    for machine_id in ["dev-primary", "dev-secondary", "licensed-win-1", "licensed-win-2"]:
        assert machine_id in registry["machines"]
        assert machine_id in policy
    for field in DUPLICATED_MACHINE_TRUTH_FIELDS:
        assert field not in policy, f"routing policy view must not duplicate canonical field {field}"
    for dependency in ["#2119", "#1838", "#2089"]:
        assert dependency in policy
        assert "open dependenc" in policy.lower()


def test_validation_evidence_required_for_report_handoff():
    manifest = load_yaml(FIXTURE_PATH)
    assert manifest["outputs"], "manifest must declare outputs"
    for output in manifest["outputs"]:
        if output.get("report_handoff"):
            assert manifest["command_manifest"]
            assert manifest["regeneration_command"]
            assert manifest["test_evidence"]
            assert manifest["legal_scan_evidence"]
            assert manifest["checksums"]
            assert manifest["review_artifact_paths"]
            assert output["output_residency"] == manifest["output_residency"]


def test_residency_compatibility_matrix():
    cases = load_yaml(ROUTING_CASES_PATH)["cases"]
    assert any(case["expected"] == "reject" for case in cases)
    for case in cases:
        assert case["input_residency"] in INPUT_RESIDENCY_ENUM
        assert case["output_residency"] in OUTPUT_RESIDENCY_ENUM
        more_public = case["output_publicity_rank"] > case["input_publicity_rank"]
        if more_public and not case.get("promotion_gates"):
            assert case["expected"] == "reject", f"{case['case_id']} must fail closed"
        if more_public and case.get("promotion_gates"):
            assert REQUIRED_PUBLIC_PROMOTION_GATES <= set(case["promotion_gates"])
        if case["expected"] == "allow":
            assert case.get("validation_evidence")
            assert case.get("promotion_gates") or not more_public


def test_input_data_boundary_crosswalk():
    manifest = load_yaml(FIXTURE_PATH)
    assert manifest["source_ids"], "execution must reference data-layer source IDs"
    assert manifest["source_registry_kind"] in SOURCE_REGISTRY_KIND_ENUM
    inline_raw_keys = {"raw_data", "data_dump", "client_payload", "source_text"}
    assert not inline_raw_keys & set(manifest), "execution manifest must not own inline raw data"
    assert manifest["source_registry_ref"], "manifest must point to the applicable registry or blocked source issue"


def test_execution_entry_point_inventory_covers_named_repos():
    text = ENTRY_INVENTORY_PATH.read_text(encoding="utf-8")
    for repo in NAMED_REPOS:
        assert f"| {repo} |" in text
    assert "Enumeration command" in text
    assert "unavailable" in text.lower() or "not available" in text.lower()
    assert "client_projects/" not in text, "tracked inventory must not leak client child paths"


def test_follow_up_issue_bundle_present():
    text = FOLLOW_UP_BACKLOG_PATH.read_text(encoding="utf-8")
    for phrase in [
        "gh issue create",
        "execution manifest validator",
        "runtime enforcement",
        "machine/provider routing registry adapter",
        "#2728",
    ]:
        assert phrase in text
    fence_lines = [line.strip() for line in text.splitlines() if line.strip().startswith("```")]
    assert fence_lines.count("```bash") == fence_lines.count("```")
    for body_file in [
        "docs/architecture/follow-up-bodies/execution-manifest-validator.md",
        "docs/architecture/follow-up-bodies/execution-runtime-enforcement.md",
        "docs/architecture/follow-up-bodies/execution-routing-registry-adapter.md",
        "docs/architecture/follow-up-bodies/execution-source-registry-gap.md",
    ]:
        assert (ROOT / body_file).exists(), f"Missing follow-up issue body: {body_file}"
