"""Tests for PipelineState — JSON-based incremental state tracking."""

import json
from pathlib import Path

import pytest
from data.pipeline.state import PipelineState


@pytest.fixture
def state_dir(tmp_path):
    return tmp_path / "pipeline-state"


@pytest.fixture
def state(state_dir):
    return PipelineState(state_dir)


class TestPipelineState:
    def test_get_returns_none_for_unknown(self, state):
        assert state.get("nonexistent") is None

    def test_save_and_get_roundtrip(self, state):
        state.save("eia_prod", last_value="2026-03-01", record_count=42,
                   run_at="2026-03-12T10:00:00")
        result = state.get("eia_prod")
        assert result["last_value"] == "2026-03-01"
        assert result["record_count"] == 42
        assert result["run_at"] == "2026-03-12T10:00:00"

    def test_save_creates_state_dir(self, tmp_path):
        new_dir = tmp_path / "new-state"
        s = PipelineState(new_dir)
        s.save("test", last_value="v1", record_count=1, run_at="2026-03-12")
        assert new_dir.exists()

    def test_save_overwrites_previous(self, state):
        state.save("p1", last_value="v1", record_count=10, run_at="t1")
        state.save("p1", last_value="v2", record_count=20, run_at="t2")
        result = state.get("p1")
        assert result["last_value"] == "v2"
        assert result["record_count"] == 20

    def test_state_persists_to_json_file(self, state, state_dir):
        state.save("demo", last_value="x", record_count=5, run_at="t")
        fp = state_dir / "demo.json"
        assert fp.exists()
        data = json.loads(fp.read_text())
        assert data["last_value"] == "x"

    def test_multiple_pipelines_independent(self, state):
        state.save("a", last_value="1", record_count=1, run_at="t1")
        state.save("b", last_value="2", record_count=2, run_at="t2")
        assert state.get("a")["last_value"] == "1"
        assert state.get("b")["last_value"] == "2"
