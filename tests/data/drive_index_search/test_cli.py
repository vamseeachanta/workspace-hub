import json
import os
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
CLI = REPO_ROOT / "scripts" / "data" / "drive-index-search" / "search.py"


def _run(args):
    return subprocess.run(
        [sys.executable, str(CLI), *args],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def test_unreachable_index_degrades(fixture_registry):
    result = _run(["mooring", "--registry", str(fixture_registry), "--json", "--limit", "5"])

    payload = json.loads(result.stdout)
    assert result.returncode == 0
    assert "unreachable" in result.stderr
    assert any(gap["id"] == "fixture_missing" for gap in payload["coverage_gaps"])
    assert payload["results"]


def test_all_indexes_unreachable_exit_code(fixture_registry):
    result = _run(
        [
            "mooring",
            "--registry",
            str(fixture_registry),
            "--json",
            "--index",
            "fixture_missing",
        ]
    )

    payload = json.loads(result.stdout)
    assert result.returncode == 2
    assert payload["results"] == []
    assert payload["coverage_gaps"][0]["reason"] == "unreachable"


def test_cli_domain_drive_fastpath(fixture_registry):
    result = _run(
        [
            "installation",
            "--registry",
            str(fixture_registry),
            "--json",
            "--drive",
            "/canonical/dde",
        ]
    )

    payload = json.loads(result.stdout)
    assert result.returncode == 0
    assert payload["indexes_queried"] == ["fixture_jsonl", "fixture_yaml", "fixture_missing"]
    assert any(row["source_index"] == "fixture_yaml" for row in payload["results"])


def test_cli_json_schema(fixture_registry):
    result = _run(["mooring", "--registry", str(fixture_registry), "--json", "--limit", "3"])

    payload = json.loads(result.stdout)
    assert set(payload) == {
        "query",
        "generated_at",
        "indexes_queried",
        "coverage_gaps",
        "results",
    }
    assert {
        "canonical_path",
        "raw_path",
        "source_index",
        "adapter",
        "score",
        "rank_basis",
        "meta",
    }.issubset(payload["results"][0])


def test_cli_limit_respected(fixture_registry):
    result = _run(["mooring", "--registry", str(fixture_registry), "--json", "--limit", "2"])

    payload = json.loads(result.stdout)
    assert result.returncode == 0
    assert len(payload["results"]) == 2


def test_empty_selection_returns_zero(fixture_registry):
    result = _run(
        [
            "mooring",
            "--registry",
            str(fixture_registry),
            "--json",
            "--drive",
            "/uncovered",
        ]
    )

    payload = json.loads(result.stdout)
    assert result.returncode == 0
    assert payload["indexes_queried"] == []
    assert payload["coverage_gaps"] == []


def test_registry_error_exit_code(fixture_registry, tmp_path):
    bad = tmp_path / "bad.yml"
    bad.write_text(Path(fixture_registry).read_text().replace("adapter: jsonl", "adapter: nope", 1))

    result = _run(["mooring", "--registry", str(bad), "--json"])

    assert result.returncode == 2
    assert "nope" in result.stderr
