"""Schema validation tests for readiness evidence bundles."""

from __future__ import annotations

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

    @pytest.mark.parametrize(
        ("field_path", "expected_enum"),
        [
            (("properties", "access", "properties", "mode", "enum"), ["ssh", "local_gui"]),
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
        assert windows_bundle["machine"]["os"] == "windows"
        assert windows_bundle["access"]["mode"] == "local_gui"
