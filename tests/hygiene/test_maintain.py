"""Scheduling contract tests use a synthetic collector; no installed software probes."""
import os
import subprocess
from pathlib import Path

import yaml
from test_repo_sync import manifest

ROOT = Path(__file__).resolve().parents[2]


def test_failed_sync_still_collects_and_preserves_exit_status(tmp_path):
    collector = tmp_path / "collector.sh"
    collector.write_text("printf 'schema_version: 4\\ndimensions: {}\\n'\n")
    output = tmp_path / "equality.yaml"
    env = os.environ.copy()
    env.update(HYGIENE_MANIFEST=str(manifest(tmp_path)), HYGIENE_ROOT=str(tmp_path),
               HYGIENE_STATE=str(tmp_path / "status.json"), HYGIENE_EQUALITY_OUTPUT=str(output),
               HYGIENE_PUBLIC_ALIAS="node", HYGIENE_COLLECTOR=str(collector),
               HYGIENE_COLLECT_TIMEOUT_SECONDS="10")
    result = subprocess.run(["bash", str(ROOT / "scripts/hygiene/maintain.sh")],
                            env=env, text=True, check=False, capture_output=True, timeout=30)
    assert result.returncode != 0
    row = yaml.safe_load(output.read_text())["dimensions"]["repo_hygiene"]["repos"][0]
    assert row["status"] == "missing"


def test_collector_failure_does_not_replace_previous_evidence(tmp_path):
    collector = tmp_path / "collector.sh"
    collector.write_text("printf 'schema_version: 4\\ndimensions: {}\\n'\nexit 1\n")
    output = tmp_path / "equality.yaml"
    output.write_text("retained\n")
    env = os.environ.copy()
    env.update(HYGIENE_MANIFEST=str(manifest(tmp_path)), HYGIENE_ROOT=str(tmp_path),
               HYGIENE_STATE=str(tmp_path / "status.json"), HYGIENE_EQUALITY_OUTPUT=str(output),
               HYGIENE_PUBLIC_ALIAS="node", HYGIENE_COLLECTOR=str(collector),
               HYGIENE_COLLECT_TIMEOUT_SECONDS="10")
    result = subprocess.run(["bash", str(ROOT / "scripts/hygiene/maintain.sh")],
                            env=env, text=True, check=False, capture_output=True, timeout=30)
    assert result.returncode != 0
    assert output.read_text() == "retained\n"
