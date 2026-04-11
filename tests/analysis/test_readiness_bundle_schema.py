"""Schema validation tests for readiness evidence bundles."""

from __future__ import annotations

import copy
import importlib.util
import sys
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = (
    REPO_ROOT / "docs" / "modules" / "ai" / "readiness-evidence-bundle.schema.yaml"
)
SCRIPT_PATH = REPO_ROOT / "scripts" / "analysis" / "readiness_bundle_schema.py"
FIXTURES_DIR = REPO_ROOT / "tests" / "fixtures" / "readiness"


def _load_fixture(name: str) -> dict:
    return yaml.safe_load((FIXTURES_DIR / name).read_text())


_spec = importlib.util.spec_from_file_location("readiness_bundle_schema", SCRIPT_PATH)
readiness_bundle_schema = importlib.util.module_from_spec(_spec)
sys.modules["readiness_bundle_schema"] = readiness_bundle_schema
_spec.loader.exec_module(readiness_bundle_schema)


class TestReadinessBundleSchemaContract:
    def test_schema_file_exists(self) -> None:
        assert SCHEMA_PATH.is_file()

    def test_schema_declares_required_top_level_fields(self) -> None:
        schema = yaml.safe_load(SCHEMA_PATH.read_text())
        assert schema["properties"]["schema_version"]["const"] == "1.0"
        assert set(schema["required"]) >= {
            "schema_version",
            "machine",
            "collected_at",
            "source_writer",
            "access",
            "checks",
            "overall",
        }
        assert set(schema["properties"]["machine"]["required"]) >= {
            "id",
            "hostname",
            "user",
            "os",
        }

    @pytest.mark.parametrize(
        ("field_path", "expected_enum"),
        [
            (("properties", "access", "properties", "mode", "enum"), ["ssh", "local_no_ssh"]),
            (
                ("properties", "checks", "items", "properties", "status", "enum"),
                ["pass", "warn", "fail", "error", "skip"],
            ),
            (
                ("properties", "overall", "properties", "verdict", "enum"),
                ["ready", "degraded", "blocked", "unknown"],
            ),
        ],
    )
    def test_schema_declares_normalized_enums(
        self, field_path: tuple[str, ...], expected_enum: list[str]
    ) -> None:
        schema = yaml.safe_load(SCHEMA_PATH.read_text())
        current = schema
        for key in field_path:
            current = current[key]
        assert current == expected_enum


class TestReadinessBundleFixtures:
    @pytest.mark.parametrize(
        "fixture_name",
        [
            "linux-valid.yaml",
            "windows-valid.yaml",
        ],
    )
    def test_valid_examples_pass_schema_validation(self, fixture_name: str) -> None:
        errors = readiness_bundle_schema.validate_bundle_file(FIXTURES_DIR / fixture_name)
        assert errors == []

    @pytest.mark.parametrize(
        ("fixture_name", "expected_fragment"),
        [
            ("invalid-access-mode.yaml", "access/mode"),
            ("invalid-timestamp.yaml", "collected_at"),
            ("missing-required-field.yaml", "machine"),
        ],
    )
    def test_invalid_examples_fail_schema_validation(
        self, fixture_name: str, expected_fragment: str
    ) -> None:
        errors = readiness_bundle_schema.validate_bundle_file(FIXTURES_DIR / fixture_name)
        assert errors
        assert any(expected_fragment in error for error in errors)

    def test_linux_and_windows_examples_cover_distinct_access_modes(self) -> None:
        linux_bundle = yaml.safe_load((FIXTURES_DIR / "linux-valid.yaml").read_text())
        windows_bundle = yaml.safe_load((FIXTURES_DIR / "windows-valid.yaml").read_text())

        assert linux_bundle["machine"]["os"] == "linux"
        assert linux_bundle["access"]["mode"] == "ssh"
        assert linux_bundle["access"]["launcher"] == "ssh"
        assert windows_bundle["machine"]["os"] == "windows"
        assert windows_bundle["access"]["mode"] == "local_no_ssh"
        assert windows_bundle["access"]["launcher"] == "scheduled_task"

    def test_schema_requires_canonical_check_ids(self) -> None:
        schema = yaml.safe_load(SCHEMA_PATH.read_text())
        required_check_ids = {
            rule["contains"]["properties"]["id"]["const"]
            for rule in schema["properties"]["checks"]["allOf"]
        }
        assert required_check_ids == {
            "workspace-root",
            "access-mode",
            "ai-cli",
            "licensed-tools",
        }

    def test_valid_examples_allow_fractional_second_timestamps(self) -> None:
        linux_bundle = _load_fixture("linux-valid.yaml")
        windows_bundle = _load_fixture("windows-valid.yaml")

        assert "." in linux_bundle["collected_at"]
        assert "." in windows_bundle["collected_at"]

    @pytest.mark.parametrize(
        ("fixture_name", "check_id", "evidence", "expected_fragment"),
        [
            ("linux-valid.yaml", "access-mode", {}, "checks/0/evidence"),
            ("linux-valid.yaml", "workspace-root", {}, "checks/1/evidence"),
            (
                "linux-valid.yaml",
                "ai-cli",
                {"claude": True},
                "checks/2/evidence",
            ),
            (
                "windows-valid.yaml",
                "licensed-tools",
                {"seats_in_use": 3},
                "checks/3/evidence",
            ),
        ],
    )
    def test_canonical_check_evidence_requires_expected_fields(
        self,
        fixture_name: str,
        check_id: str,
        evidence: dict[str, object],
        expected_fragment: str,
    ) -> None:
        bundle = copy.deepcopy(_load_fixture(fixture_name))
        check = next(item for item in bundle["checks"] if item["id"] == check_id)
        check["evidence"] = evidence

        errors = readiness_bundle_schema.validate_bundle(bundle)

        assert errors
        assert any(expected_fragment in error for error in errors)

    def test_schema_declares_canonical_check_evidence_contracts(self) -> None:
        schema = yaml.safe_load(SCHEMA_PATH.read_text())
        item_rules = schema["properties"]["checks"]["items"]["allOf"]
        canonical_evidence_rules = {
            rule["if"]["properties"]["id"]["const"]: rule["then"]["properties"]["evidence"]
            for rule in item_rules
            if "if" in rule and "then" in rule
        }
        definitions = schema["definitions"]

        assert canonical_evidence_rules["access-mode"]["$ref"] == "#/definitions/access_mode_evidence"
        assert definitions["access_mode_evidence"]["required"] == ["transport"]
        assert canonical_evidence_rules["workspace-root"]["$ref"] == "#/definitions/workspace_root_evidence"
        assert definitions["workspace_root_evidence"]["required"] == ["path"]
        assert canonical_evidence_rules["ai-cli"]["$ref"] == "#/definitions/ai_cli_evidence"
        assert definitions["ai_cli_evidence"]["required"] == ["claude", "codex"]
        assert canonical_evidence_rules["licensed-tools"]["oneOf"]
