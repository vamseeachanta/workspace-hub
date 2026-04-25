from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = REPO_ROOT / "scripts" / "knowledge" / "validate_inventory_readiness.py"
CANONICAL_CONFIG = REPO_ROOT / "config" / "knowledge" / "inventory-readiness.yaml"


def load_module():
    spec = importlib.util.spec_from_file_location("validate_inventory_readiness", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def validator():
    return load_module()


@pytest.fixture
def base_matrix() -> dict:
    return {
        "schema_version": 1,
        "provider_queue_snapshot": {
            "generated_at": "2026-04-25T09:20:15.784834Z",
            "source": "docs/reports/provider-work-queue.md",
            "current_counts": {
                "codex_candidates": 4,
                "gemini_tasks": 1,
                "claude_reviews": 17,
            },
        },
        "package_families": [
            {
                "id": "og_standards_to_gtm",
                "title": "O&G standards source-to-GTM readiness",
                "owner_provider": "codex",
                "preferred_next_provider": "codex",
                "readiness": {
                    "raw_data": "READY",
                    "inventory": "READY",
                    "llm_wiki": "PARTIAL",
                    "calculation_code": "PARTIAL",
                    "parametric_outputs": "MISSING",
                    "website_gtm": "MISSING",
                },
                "evidence": {
                    "raw_data_paths": ["/mnt/ace/O&G-Standards/_inventory.db"],
                    "inventory_artifacts": ["tools/SCHEMA_COMPARISON.md"],
                    "wiki_doc_keys": [],
                    "calculation_artifacts": [],
                    "parametric_artifacts": [],
                    "website_gtm_artifacts": [],
                    "stale_artifacts": [],
                    "issue_refs": [
                        {
                            "issue": 2464,
                            "relation": "downstream_candidate",
                            "approval_state": "plan-approved",
                            "produces_stages": ["inventory"],
                            "implemented_artifacts": [],
                            "artifact_contract": "curated tier-1 routing index",
                        },
                        {
                            "issue": 2403,
                            "relation": "downstream_candidate",
                            "approval_state": "plan-approved",
                            "produces_stages": ["llm_wiki"],
                            "implemented_artifacts": [],
                            "artifact_contract": "embeddings model-selection spike",
                        },
                        {
                            "issue": 2481,
                            "relation": "reference",
                            "approval_state": "plan-review",
                            "produces_stages": ["calculation_code"],
                            "implemented_artifacts": [],
                            "artifact_contract": "calculation output citation contract",
                        },
                    ],
                },
                "dependency_roles": [
                    {
                        "issue": 2471,
                        "role": "downstream_only",
                        "reason": "live downstream dependency, not required for this matrix",
                    }
                ],
                "dispatch": {
                    "ready_for_provider": "codex",
                    "rationale": "implement the readiness validator/report spine for #2487",
                    "dependency_issues": [2464, 2403, 2481],
                    "expected_output_artifact": "docs/reports/inventory-readiness-matrix-2026-04-25.md",
                },
            }
        ],
    }


def write_yaml(tmp_path: Path, data: dict) -> Path:
    path = tmp_path / "matrix.yaml"
    path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
    return path


def assert_invalid(validator, data: dict, tmp_path: Path, *expected: str) -> None:
    path = write_yaml(tmp_path, data)
    with pytest.raises(validator.InventoryReadinessError) as exc:
        validator.load_and_validate(path)
    message = str(exc.value)
    for needle in expected:
        assert needle in message


def test_valid_minimal_matrix_passes(validator, base_matrix):
    result = validator.validate_matrix(base_matrix)
    assert result["package_count"] == 1
    assert result["dispatch_counts"]["codex"] == 1


def test_missing_required_top_level_key_fails(validator, base_matrix, tmp_path):
    base_matrix.pop("package_families")
    assert_invalid(validator, base_matrix, tmp_path, "package_families")


def test_unknown_readiness_status_fails(validator, base_matrix, tmp_path):
    base_matrix["package_families"][0]["readiness"]["raw_data"] = "DONE"
    assert_invalid(validator, base_matrix, tmp_path, "raw_data", "DONE")


def test_ready_without_stage_evidence_fails_without_mutating_yaml(validator, base_matrix, tmp_path):
    family = base_matrix["package_families"][0]
    family["readiness"]["llm_wiki"] = "READY"
    path = write_yaml(tmp_path, base_matrix)
    before = path.read_text(encoding="utf-8")
    with pytest.raises(validator.InventoryReadinessError) as exc:
        validator.load_and_validate(path)
    assert "llm_wiki" in str(exc.value)
    assert "wiki_doc_keys" in str(exc.value)
    assert path.read_text(encoding="utf-8") == before


def test_missing_doc_key_for_wiki_ready_fails(validator, base_matrix, tmp_path):
    base_matrix["package_families"][0]["readiness"]["llm_wiki"] = "READY"
    assert_invalid(validator, base_matrix, tmp_path, "doc_key", "wiki_doc_keys")


def test_approved_plan_without_implemented_artifact_cannot_make_ready(validator, base_matrix, tmp_path):
    family = base_matrix["package_families"][0]
    family["readiness"]["calculation_code"] = "READY"
    assert_invalid(validator, base_matrix, tmp_path, "calculation_code", "implemented")
    family["readiness"]["calculation_code"] = "PARTIAL"
    assert validator.validate_matrix(base_matrix)["package_count"] == 1


def test_typed_issue_ref_wrong_stage_cannot_satisfy_partial_claim(validator, base_matrix, tmp_path):
    family = base_matrix["package_families"][0]
    family["readiness"]["website_gtm"] = "PARTIAL"
    family["readiness"]["llm_wiki"] = "MISSING"
    family["readiness"]["calculation_code"] = "MISSING"
    family["evidence"]["issue_refs"] = [
        {
            "issue": 2346,
            "relation": "downstream_candidate",
            "approval_state": "plan-approved",
            "produces_stages": ["calculation_code"],
            "implemented_artifacts": [],
            "artifact_contract": "wrong stage",
        }
    ]
    family["dispatch"]["dependency_issues"] = [2346]
    assert_invalid(validator, base_matrix, tmp_path, "website_gtm", "PARTIAL", "stage-specific")


def test_stale_requires_stale_evidence(validator, base_matrix, tmp_path):
    base_matrix["package_families"][0]["readiness"]["inventory"] = "STALE"
    assert_invalid(validator, base_matrix, tmp_path, "STALE", "stale_artifacts")


def test_missing_config_path_fails(validator, tmp_path):
    missing = tmp_path / "missing.yaml"
    with pytest.raises(validator.InventoryReadinessError) as exc:
        validator.load_and_validate(missing)
    assert str(missing) in str(exc.value)


def test_invalid_provider_snapshot_null_contract_fails(validator, base_matrix, tmp_path):
    snapshot = base_matrix["provider_queue_snapshot"]
    snapshot["source"] = None
    snapshot["current_counts"]["codex_candidates"] = 4
    snapshot["current_counts"]["gemini_tasks"] = None
    snapshot["current_counts"]["claude_reviews"] = None
    assert_invalid(validator, base_matrix, tmp_path, "current_counts", "null")


def test_missing_nested_required_field_names_path(validator, base_matrix, tmp_path):
    del base_matrix["package_families"][0]["dispatch"]["rationale"]
    assert_invalid(validator, base_matrix, tmp_path, "package_families[0].dispatch.rationale")


def test_blocked_requires_blocking_dependency(validator, base_matrix, tmp_path):
    base_matrix["package_families"][0]["readiness"]["parametric_outputs"] = "BLOCKED"
    assert_invalid(validator, base_matrix, tmp_path, "BLOCKED", "blocking")


def test_dependency_role_enum_enforced(validator, base_matrix, tmp_path):
    base_matrix["package_families"][0]["dependency_roles"][0]["role"] = "maybe"
    assert_invalid(validator, base_matrix, tmp_path, "dependency_roles[0].role", "maybe")


def test_duplicate_package_ids_fail(validator, base_matrix, tmp_path):
    base_matrix["package_families"].append(dict(base_matrix["package_families"][0]))
    assert_invalid(validator, base_matrix, tmp_path, "duplicate", "og_standards_to_gtm")


def test_unknown_provider_fails(validator, base_matrix, tmp_path):
    base_matrix["package_families"][0]["dispatch"]["ready_for_provider"] = "llama"
    assert_invalid(validator, base_matrix, tmp_path, "ready_for_provider", "llama")


def test_zero_package_families_fails(validator, base_matrix, tmp_path):
    base_matrix["package_families"] = []
    assert_invalid(validator, base_matrix, tmp_path, "package_families", "at least one")


def test_null_queue_counts_render_unknown(validator, base_matrix):
    snapshot = base_matrix["provider_queue_snapshot"]
    snapshot["source"] = None
    snapshot["current_counts"] = {
        "codex_candidates": None,
        "gemini_tasks": None,
        "claude_reviews": None,
    }
    validated = validator.validate_matrix(base_matrix)
    report = validator.render_markdown(validated, base_matrix)
    assert "codex_candidates | unknown" in report
    assert "gemini_tasks | unknown" in report
    assert "claude_reviews | unknown" in report


def test_report_groups_dispatch_by_provider(validator, base_matrix):
    rows = base_matrix["package_families"]
    for provider in ["gemini", "claude"]:
        clone = yaml.safe_load(yaml.safe_dump(rows[0]))
        clone["id"] = f"{provider}_package"
        clone["title"] = f"{provider.title()} package"
        clone["owner_provider"] = provider
        clone["preferred_next_provider"] = provider
        clone["dispatch"]["ready_for_provider"] = provider
        rows.append(clone)
    validated = validator.validate_matrix(base_matrix)
    report = validator.render_markdown(validated, base_matrix)
    assert "## Codex Dispatch" in report
    assert "## Gemini Dispatch" in report
    assert "## Claude Dispatch" in report


def test_current_provider_counts_are_observed_not_thresholds(validator, base_matrix):
    base_matrix["provider_queue_snapshot"]["current_counts"] = {
        "codex_candidates": 4,
        "gemini_tasks": 1,
        "claude_reviews": 17,
    }
    assert validator.validate_matrix(base_matrix)["provider_queue_snapshot"]["current_counts"]["codex_candidates"] == 4


def test_expected_output_artifact_may_be_null_for_unrun_recon(validator, base_matrix):
    family = base_matrix["package_families"][0]
    family["owner_provider"] = "gemini"
    family["preferred_next_provider"] = "gemini"
    family["dispatch"]["ready_for_provider"] = "gemini"
    family["dispatch"]["rationale"] = "run unexecuted scouting; expected output will be created by the scouting task"
    family["dispatch"]["expected_output_artifact"] = None
    assert validator.validate_matrix(base_matrix)["dispatch_counts"]["gemini"] == 1


def test_dispatch_dependency_issues_mirror_non_reference_issue_refs(validator, base_matrix, tmp_path):
    family = base_matrix["package_families"][0]
    family["dispatch"]["dependency_issues"] = [2464]
    assert_invalid(validator, base_matrix, tmp_path, "dispatch.dependency_issues", "2403")


def test_report_includes_blocked_partial_missing_evidence_section(validator, base_matrix):
    validated = validator.validate_matrix(base_matrix)
    report = validator.render_markdown(validated, base_matrix)
    assert "## Blocked / partial / missing evidence" in report
    assert "llm_wiki" in report
    assert "calculation_code" in report
    assert "parametric_outputs" in report
    assert "approved-plan evidence only" in report


def test_cli_validate_only_does_not_write_report(tmp_path):
    output = tmp_path / "should-not-exist.md"
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT_PATH),
            "--config",
            str(CANONICAL_CONFIG),
            "--output",
            str(output),
            "--validate-only",
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert not output.exists()
