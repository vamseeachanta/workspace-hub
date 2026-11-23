"""Tests for ManifestManager — atomic YAML pipeline manifest."""

from pathlib import Path

import pytest
import yaml
from data.pipeline.manifest import ManifestManager


@pytest.fixture
def manifest_path(tmp_path):
    return tmp_path / "pipeline-manifest.yaml"


@pytest.fixture
def mgr(manifest_path):
    return ManifestManager(manifest_path)


class TestManifestManager:
    def test_read_returns_empty_when_no_file(self, mgr):
        result = mgr.read()
        assert result == {"pipelines": {}}

    def test_update_creates_entry(self, mgr):
        mgr.update(
            pipeline_name="eia_prod",
            source_url="https://api.eia.gov/v2/petroleum",
            refresh_cadence="weekly",
            last_run="2026-03-12T10:00:00",
            record_count=500,
            output_path="data/eia/eia_petroleum_weekly.jsonl",
        )
        data = mgr.read()
        assert "eia_prod" in data["pipelines"]
        entry = data["pipelines"]["eia_prod"]
        assert entry["record_count"] == 500
        assert entry["refresh_cadence"] == "weekly"

    def test_update_overwrites_existing_entry(self, mgr):
        mgr.update("p1", "url1", "daily", "t1", 10, "out1")
        mgr.update("p1", "url1", "daily", "t2", 20, "out1")
        entry = mgr.read()["pipelines"]["p1"]
        assert entry["record_count"] == 20
        assert entry["last_run"] == "t2"

    def test_multiple_pipelines_coexist(self, mgr):
        mgr.update("a", "url_a", "daily", "t1", 1, "out_a")
        mgr.update("b", "url_b", "weekly", "t2", 2, "out_b")
        data = mgr.read()
        assert len(data["pipelines"]) == 2
        assert data["pipelines"]["a"]["source_url"] == "url_a"
        assert data["pipelines"]["b"]["source_url"] == "url_b"

    def test_manifest_persists_as_yaml(self, mgr, manifest_path):
        mgr.update("demo", "url", "monthly", "t", 5, "out")
        assert manifest_path.exists()
        raw = yaml.safe_load(manifest_path.read_text())
        assert raw["pipelines"]["demo"]["record_count"] == 5

    def test_atomic_write_no_partial(self, mgr, manifest_path):
        mgr.update("x", "url", "daily", "t", 1, "out")
        # File should exist and be valid YAML after write
        content = manifest_path.read_text()
        data = yaml.safe_load(content)
        assert data is not None
