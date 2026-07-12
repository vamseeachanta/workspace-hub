"""Delivery tests for scheduler mutation HTML and CI wiring."""
from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
CHECKER = ROOT / "scripts/enforcement/check-scheduler-mutation-surfaces.py"
REGISTRY = ROOT / "config/scheduled-tasks/mutation-surfaces.yaml"
REPORT = ROOT / "docs/reports/2026-07-11-issue-3470-scheduler-mutation-safety.html"
WORKFLOW = ROOT / ".github/workflows/enforcement-gate.yml"


def load_checker():
    spec = importlib.util.spec_from_file_location("scheduler_delivery_checker", CHECKER)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def contract_inputs():
    checker = load_checker()
    records = checker.read_index_records(ROOT)
    registry = yaml.safe_load(records[checker.REGISTRY])
    discovery = checker.discover_mutation_surfaces(records)
    validation = checker.validate_registry(registry, discovery, records)
    digest = checker.input_digest(
        records[checker.REGISTRY], checker.digest_record_union(registry, records)
    )
    return checker, records, registry, discovery, validation, digest


def test_html_is_deterministic_complete_and_linked():
    checker, _records, registry, discovery, validation, digest = contract_inputs()
    first = checker.render_html(registry, discovery, validation, digest)
    second = checker.render_html(registry, discovery, validation, digest)
    assert first == second
    text = first.decode()
    assert f'data-input-digest="{digest}"' in text
    assert "Registry inclusion does not authorize live scheduler mutation" in text
    for row in registry["surfaces"]:
        assert text.count(f'data-surface="{row["path"]}"') == 1
    for issue in range(3475, 3480):
        assert f'href="https://github.com/vamseeachanta/workspace-hub/issues/{issue}"' in text


def test_cli_render_and_stale_check(tmp_path):
    output = tmp_path / "audit.html"
    render = subprocess.run(
        [sys.executable, str(CHECKER), "--render-html", str(output)], cwd=ROOT
    )
    assert render.returncode == 0
    assert output.is_file()
    check = subprocess.run(
        [sys.executable, str(CHECKER), "--check-html", str(output)], cwd=ROOT
    )
    assert check.returncode == 0
    output.write_bytes(output.read_bytes().replace(b"data-input-digest=", b"data-stale-digest="))
    stale = subprocess.run(
        [sys.executable, str(CHECKER), "--check-html", str(output)], cwd=ROOT
    )
    assert stale.returncode != 0


def test_enforcement_workflow_is_active_and_failure_propagating():
    workflow = yaml.load(WORKFLOW.read_text(), Loader=yaml.BaseLoader)
    assert "pull_request" in workflow["on"]
    job = workflow["jobs"]["scheduler-mutation-surfaces"]
    assert job["runs-on"] == "ubuntu-latest"
    assert job.get("continue-on-error") not in {"true", True}
    steps = job["steps"]
    checkout = next(step for step in steps if step.get("uses") == "actions/checkout@v4")
    assert checkout["with"]["fetch-depth"] == "0"
    assert any(step.get("uses") == "actions/setup-python@v5" for step in steps)
    assert any(step.get("uses") == "astral-sh/setup-uv@v4" for step in steps)
    runs = [step for step in steps if CHECKER.name in step.get("run", "")]
    assert len(runs) == 2
    assert any("--check-html" not in step["run"] for step in runs)
    assert any(f"--check-html {REPORT.relative_to(ROOT)}" in step["run"] for step in runs)
    for step in runs:
        assert step.get("continue-on-error") not in {"true", True}
        assert "|| true" not in step["run"]
        assert "set +e" not in step["run"]
