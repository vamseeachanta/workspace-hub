"""TDD tests for skill-preference-weights.py (WRK-5088)."""
import json
import tempfile
from pathlib import Path

import pytest
import yaml

from scripts.skills.skill_preference_weights import (
    load_executions,
    compute_preferences,
    write_preferences_yaml,
)


@pytest.fixture
def sample_executions(tmp_path):
    """Create sample skill-executions.jsonl with varied frequencies."""
    path = tmp_path / "skill-executions.jsonl"
    entries = [
        # work-queue: 10 invocations (high frequency)
        *[{"skill_name": "work-queue", "timestamp": f"2026-03-{10+i}T10:00:00", "session_id": f"s{i}", "project": "workspace-hub", "duration_s": 1} for i in range(10)],
        # session-start: 7 invocations
        *[{"skill_name": "session-start", "timestamp": f"2026-03-{10+i}T10:00:00", "session_id": f"s{i}", "project": "workspace-hub", "duration_s": 0} for i in range(7)],
        # tdd-obra: 3 invocations (below threshold)
        *[{"skill_name": "tdd-obra", "timestamp": f"2026-03-{10+i}T10:00:00", "session_id": f"s{i}", "project": "workspace-hub", "duration_s": 2} for i in range(3)],
        # Skill (generic tool invocations): 2 (below threshold)
        *[{"skill_name": "Skill", "timestamp": f"2026-03-{10+i}T10:00:00", "session_id": f"s{i}", "project": "workspace-hub", "duration_s": 0} for i in range(2)],
    ]
    with open(path, "w") as f:
        for e in entries:
            f.write(json.dumps(e) + "\n")
    return path


@pytest.fixture
def empty_executions(tmp_path):
    """Create empty executions file."""
    path = tmp_path / "skill-executions.jsonl"
    path.write_text("")
    return path


class TestLoadExecutions:
    def test_loads_valid_jsonl(self, sample_executions):
        execs = load_executions(sample_executions)
        assert len(execs) == 22

    def test_empty_file(self, empty_executions):
        execs = load_executions(empty_executions)
        assert execs == []

    def test_missing_file(self, tmp_path):
        execs = load_executions(tmp_path / "nonexistent.jsonl")
        assert execs == []


class TestComputePreferences:
    def test_computes_frequency_counts(self, sample_executions):
        execs = load_executions(sample_executions)
        prefs = compute_preferences(execs, min_samples=5)
        # Only work-queue (10) and session-start (7) meet threshold
        skill_names = [p["skill"] for p in prefs]
        assert "work-queue" in skill_names
        assert "session-start" in skill_names

    def test_excludes_below_threshold(self, sample_executions):
        execs = load_executions(sample_executions)
        prefs = compute_preferences(execs, min_samples=5)
        skill_names = [p["skill"] for p in prefs]
        assert "tdd-obra" not in skill_names  # only 3
        assert "Skill" not in skill_names  # only 2

    def test_filters_generic_skill_tool(self, sample_executions):
        execs = load_executions(sample_executions)
        prefs = compute_preferences(execs, min_samples=1)  # low threshold
        skill_names = [p["skill"] for p in prefs]
        assert "Skill" not in skill_names  # generic tool, not a real skill

    def test_sorted_by_frequency_desc(self, sample_executions):
        execs = load_executions(sample_executions)
        prefs = compute_preferences(execs, min_samples=5)
        assert prefs[0]["skill"] == "work-queue"
        assert prefs[0]["invocation_count"] == 10

    def test_includes_required_fields(self, sample_executions):
        execs = load_executions(sample_executions)
        prefs = compute_preferences(execs, min_samples=5)
        required = {"skill", "invocation_count", "unique_sessions", "avg_duration_s", "weight"}
        for p in prefs:
            assert required.issubset(set(p.keys())), f"Missing: {required - set(p.keys())}"

    def test_weight_normalized(self, sample_executions):
        execs = load_executions(sample_executions)
        prefs = compute_preferences(execs, min_samples=5)
        weights = [p["weight"] for p in prefs]
        assert max(weights) == 1.0
        assert all(0 < w <= 1.0 for w in weights)

    def test_empty_input(self):
        prefs = compute_preferences([], min_samples=5)
        assert prefs == []


class TestWritePreferencesYaml:
    def test_writes_valid_yaml(self, tmp_path, sample_executions):
        execs = load_executions(sample_executions)
        prefs = compute_preferences(execs, min_samples=5)
        output = tmp_path / "skill-preferences.yaml"
        write_preferences_yaml(prefs, output)
        data = yaml.safe_load(output.read_text())
        assert "generated_at" in data
        assert "min_samples" in data
        assert "preferences" in data
        assert len(data["preferences"]) == 2

    def test_empty_prefs_still_writes(self, tmp_path):
        output = tmp_path / "skill-preferences.yaml"
        write_preferences_yaml([], output)
        data = yaml.safe_load(output.read_text())
        assert data["preferences"] == []
