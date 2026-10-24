"""CLI contracts with literal expected identities, independent of search scoring.

Synthetic registry: land covers drive-a and has alpha/beta; sea covers drive-b
and has gamma. Every row has the single search term 'needle' exactly once.
Thus domain/drive/index selection is set intersection, and a limit of one keeps
alpha before beta by canonical-path order (merge.py's documented tie breaker).
Registry version 1 follows registry.py; exit 2 follows search.py/argparse's error
contract. Positive limits/timeouts are input constraints, not engineering limits.
"""

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

PACKAGE_DIR = Path(__file__).resolve().parents[3] / "scripts/data/drive-index-search"


@pytest.fixture
def synthetic_registry(tmp_path):
    entries = []
    for name, domain, drive, identities in (
        ("land", "land", "drive-a", ("alpha", "beta")),
        ("sea", "marine", "drive-b", ("gamma",)),
    ):
        rows = tmp_path / f"{name}.jsonl"
        rows.write_text(
            "".join(json.dumps({"path": str(tmp_path / identity), "text": "needle"})
                    + "\n" for identity in identities),
            encoding="utf-8",
        )
        entries.append({
            "id": name, "adapter": "jsonl", "path": str(rows),
            "coverage": {"drives": [drive]}, "domains": [domain],
            "adapter_params": {"path_field": "path", "search_fields": ["text"]},
        })
    registry = tmp_path / "registry.yml"
    registry.write_text(yaml.safe_dump({"version": 1, "indexes": entries}),
                        encoding="utf-8")
    return registry


def run_search(registry, *args):
    return subprocess.run(
        [sys.executable, str(PACKAGE_DIR / "search.py"), "--registry", str(registry),
         *args],
        # Preserve real metrics behavior while keeping test output in scratch.
        env={**os.environ, "DRIVE_SEARCH_METRICS_DIR": str(registry.parent / "metrics")},
        capture_output=True, text=True, check=False,
    )


@pytest.mark.parametrize("as_json", (False, True), ids=("text", "json"))
@pytest.mark.parametrize(("options", "identities"), (
    ([], ("alpha", "beta", "gamma")),
    (["--domain", "land"], ("alpha", "beta")),
    (["--drive", "drive-b"], ("gamma",)),
    (["--index", "land"], ("alpha", "beta")),
    (["--index", "land", "--index", "sea"], ("alpha", "beta", "gamma")),
    (["--limit", "1"], ("alpha",)),
    (["--index", "land", "--domain", "marine"], ()),
    (["--domain", "absent"], ()),
))
def test_selection_and_limit_in_every_format(synthetic_registry, as_json,
                                           options, identities):
    result = run_search(synthetic_registry, "needle", *options,
                        *(["--json"] if as_json else []))
    assert result.returncode == 0, result.stderr
    assert result.stderr == ""
    if as_json:
        rows = json.loads(result.stdout)["results"]
        paths = [row["canonical_path"] for row in rows]
    else:
        paths = [line.split("\t")[2] for line in result.stdout.splitlines()]
    assert paths == [str(synthetic_registry.parent / name) for name in identities]


@pytest.mark.parametrize("json_first", (False, True))
@pytest.mark.parametrize("arguments", (
    [],
    ["needle", "--limit", "bad"],
    ["needle", "--limit", "0"],
    ["needle", "--limit", "-1"],
    ["needle", "--limit"],
    ["needle", "--unknown"],
    ["needle", "--csv"],
    ["needle", "--timeout-per-index", "bad"],
    ["needle", "--timeout-per-index", "0"],
    ["needle", "--timeout-per-index", "-1"],
    ["needle", "--timeout-per-index", "nan"],
    ["needle", "--timeout-per-index", "inf"],
))
def test_pre_execution_errors_use_requested_json(synthetic_registry, arguments,
                                               json_first):
    args = ["--json", *arguments] if json_first else [*arguments, "--json"]
    result = run_search(synthetic_registry, *args)
    assert result.returncode == 2
    payload = json.loads(result.stdout)
    assert payload["error"]["code"] == "argument_error"
    assert payload["error"]["message"]
    assert "Traceback" not in result.stderr
    assert not (synthetic_registry.parent / "metrics").exists()


@pytest.mark.parametrize("as_json", (False, True), ids=("text", "json"))
def test_registry_error_is_explicit(synthetic_registry, as_json):
    synthetic_registry.write_text("version: 1\nindexes: invalid\n", encoding="utf-8")
    result = run_search(synthetic_registry, "needle", *(["--json"] if as_json else []))
    assert result.returncode == 2
    if as_json:
        assert json.loads(result.stdout)["error"] == {
            "code": "registry_error", "message": "indexes must be a list",
        }
    else:
        assert result.stdout == ""
    assert "indexes must be a list" in result.stderr


def test_text_argument_error_stays_readable(synthetic_registry):
    result = run_search(synthetic_registry, "needle", "--limit", "bad")
    assert result.returncode == 2
    assert result.stdout == ""
    assert "--limit" in result.stderr


def test_end_of_options_does_not_select_json(synthetic_registry):
    result = run_search(synthetic_registry, "--limit", "bad", "--", "--json")
    assert result.returncode == 2
    assert result.stdout == ""
    assert "--limit" in result.stderr


@pytest.mark.parametrize("flag", ("--j", "--json=no"))
def test_output_selector_errors_remain_json(synthetic_registry, flag):
    result = run_search(synthetic_registry, "needle", "--limit", "bad", flag)
    assert result.returncode == 2
    assert json.loads(result.stdout)["error"]["code"] == "argument_error"


@pytest.mark.parametrize("as_json", (False, True), ids=("text", "json"))
def test_query_with_no_matches(synthetic_registry, as_json):
    result = run_search(synthetic_registry, "absent", *(["--json"] if as_json else []))
    assert result.returncode == 0, result.stderr
    assert (json.loads(result.stdout)["results"] if as_json else result.stdout) in ([], "")
