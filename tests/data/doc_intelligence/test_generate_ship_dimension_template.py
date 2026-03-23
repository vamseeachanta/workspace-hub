"""Tests for ship dimension template generation."""

import os
import subprocess
import sys
from pathlib import Path

import yaml

from scripts.data.doc_intelligence.generate_ship_dimension_template import (
    DIMENSION_FIELDS,
    build_dimension_entries,
    build_template_document,
)

REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPT = str(
    REPO_ROOT
    / "scripts"
    / "data"
    / "doc-intelligence"
    / "generate-ship-dimension-template.py"
)


def _sample_plans() -> list[dict]:
    return [
        {
            "stem": "ddg-01-profile",
            "hull_code": "DDG",
            "hull_number": "01",
            "vessel_type": "destroyer",
            "filename": "ddg-01-profile.pdf",
            "has_text": False,
        },
        {
            "stem": "ffg-12-general-arrangement",
            "hull_code": "FFG",
            "hull_number": "12",
            "vessel_type": "frigate",
            "filename": "ffg-12-general-arrangement.pdf",
            "has_text": True,
        },
    ]


def _run_cli(*args: str) -> subprocess.CompletedProcess:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(REPO_ROOT)
    return subprocess.run(
        [sys.executable, SCRIPT, *args],
        capture_output=True,
        text=True,
        env=env,
        timeout=30,
    )


class TestBuildDimensionEntries:
    def test_skips_text_extractable_plans(self):
        entries = build_dimension_entries(_sample_plans())

        assert len(entries) == 1
        assert entries[0]["stem"] == "ddg-01-profile"

    def test_initializes_pending_dimension_fields(self):
        entries = build_dimension_entries(_sample_plans())

        assert entries[0]["entry_status"] == "pending"
        assert entries[0]["source_plan"] == "ddg-01-profile.pdf"
        assert entries[0]["dimensions"] == {field: None for field in DIMENSION_FIELDS}


class TestBuildTemplateDocument:
    def test_returns_expected_document_shape(self):
        document = build_template_document(_sample_plans())

        assert document["version"] == "1.0.0"
        assert document["description"] == "Ship dimension template for manual data entry"
        assert document["total_entries"] == 1
        assert len(document["entries"]) == 1
        assert isinstance(document["generated_at"], str)


class TestCliGeneration:
    def test_dry_run_prints_template_yaml(self, tmp_dir):
        plans_index = tmp_dir / "ship-plans-index.yaml"
        plans_index.write_text(yaml.safe_dump({"plans": _sample_plans()}, sort_keys=False))

        result = _run_cli("--plans-index", str(plans_index), "--dry-run")

        assert result.returncode == 0
        loaded = yaml.safe_load(result.stdout)
        assert loaded["total_entries"] == 1
        assert loaded["entries"][0]["dimensions"] == {
            field: None for field in DIMENSION_FIELDS
        }

    def test_writes_output_file(self, tmp_dir):
        plans_index = tmp_dir / "ship-plans-index.yaml"
        output = tmp_dir / "ship-dimensions.yaml"
        plans_index.write_text(yaml.safe_dump({"plans": _sample_plans()}, sort_keys=False))

        result = _run_cli(
            "--plans-index",
            str(plans_index),
            "--output",
            str(output),
        )

        assert result.returncode == 0
        assert output.exists()
        loaded = yaml.safe_load(output.read_text())
        assert loaded["total_entries"] == 1
        assert loaded["entries"][0]["source_plan"] == "ddg-01-profile.pdf"
