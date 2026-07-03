from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parents[3]
CLI = REPO_ROOT / "scripts" / "data" / "drive-index-search" / "search.py"


def _write_registry(tmp_path: Path, *, freshness: dict) -> Path:
    index = tmp_path / "index.jsonl"
    index.write_text('{"path": "/fixture/mooring.txt", "summary": "mooring analysis"}\n')
    registry = {
        "version": 1,
        "defaults": {"staleness_days": 90},
        "indexes": [
            {
                "id": "fixture_jsonl",
                "adapter": "jsonl",
                "path": str(index),
                "coverage": {"drives": ["/fixture"]},
                "freshness": freshness,
                "adapter_params": {"path_field": "path", "search_fields": ["path", "summary"]},
            }
        ],
    }
    path = tmp_path / "registry.yml"
    path.write_text(yaml.safe_dump(registry))
    return path


def _run(registry: Path, *extra: str):
    return subprocess.run(
        [sys.executable, str(CLI), "mooring", "--registry", str(registry), *extra],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def test_cli_staleness_warning_stderr(tmp_path):
    registry = _write_registry(tmp_path, freshness={"as_of": "2025-12-28", "staleness_days": 90})

    result = _run(registry)

    assert result.returncode == 0
    assert "WARNING: index fixture_jsonl is" in result.stderr
    assert "threshold 90" in result.stderr


def test_cli_prefers_state_file(tmp_path):
    state = tmp_path / "refresh-state.json"
    state.write_text(json.dumps({"finished_at": "2026-07-02T12:00:00Z", "status": "ok", "row_count": 1}))
    registry = _write_registry(
        tmp_path,
        freshness={"as_of": "2025-12-28", "staleness_days": 90, "state_file": str(state)},
    )

    result = _run(registry, "--json")
    payload = json.loads(result.stdout)

    assert result.returncode == 0
    assert payload["index_status"][0]["stale"] is False
    assert payload["index_status"][0]["last_refresh_status"] == "ok"


def test_cli_state_file_unreachable_fallback(tmp_path):
    registry = _write_registry(
        tmp_path,
        freshness={"as_of": "2025-12-28", "staleness_days": 90, "state_file": str(tmp_path / "missing.json")},
    )

    result = _run(registry, "--json")
    payload = json.loads(result.stdout)

    assert result.returncode == 0
    assert payload["index_status"][0]["stale"] is True
    assert payload["index_status"][0]["last_refresh_status"] == "unknown"


def test_cli_json_index_status_key(tmp_path):
    registry = _write_registry(tmp_path, freshness={"as_of": "2026-04-17", "staleness_days": 60})

    result = _run(registry, "--json")
    payload = json.loads(result.stdout)

    assert set(payload["index_status"][0]) == {
        "id",
        "as_of",
        "days_stale",
        "threshold_days",
        "stale",
        "last_refresh_status",
        "row_count",
    }
    assert payload["index_status"][0]["days_stale"] >= 76
    assert payload["index_status"][0]["threshold_days"] == 60
