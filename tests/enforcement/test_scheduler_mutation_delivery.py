"""Delivery tests for scheduler mutation HTML and CI wiring."""
from __future__ import annotations

import importlib.util
import html
import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
CHECKER = ROOT / "scripts/enforcement/check-scheduler-mutation-surfaces.py"
REGISTRY = ROOT / "config/scheduled-tasks/mutation-surfaces.yaml"
REPORT = ROOT / "docs/reports/2026-07-11-issue-3470-scheduler-mutation-safety.html"
WORKFLOW = ROOT / ".github/workflows/enforcement-gate.yml"
MAIN_WORKFLOW = ROOT / ".github/workflows/scheduler-mutation-main.yml"
RULE = ROOT / ".claude/rules/scheduler-mutation-safety.md"
MERGE_RULE = ROOT / ".claude/rules/merge-authorization.md"
OPS = ROOT / "docs/ops/scheduled-tasks.md"


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
        for operation in row.get("operations", []):
            key = html.escape(f'{row["path"]}::{operation["id"]}', quote=True)
            opening = (
                f'<section class="operation" data-operation="{key}" '
                f'data-target-kind="{html.escape(operation["target_kind"], quote=True)}" '
                f'data-scheduler-identity="{html.escape(operation["scheduler_identity"], quote=True)}" '
                f'data-execution-host-binding="{html.escape(operation["execution_host_binding"], quote=True)}">'
            )
            assert text.count(opening) == 1
            for branch in operation["authority_branches"]:
                authority_key = html.escape(f'{key}::{branch["id"]}', quote=True)
                authority = html.escape(
                    f'{branch["id"]}:{branch["mechanism"]}/{branch["strength"]}'
                )
                expected_branch = (
                    f'<li data-authority="{authority_key}" '
                    f'data-mechanism="{html.escape(branch["mechanism"], quote=True)}" '
                    f'data-strength="{html.escape(branch["strength"], quote=True)}">'
                    f'{authority}</li>'
                )
                assert text.count(expected_branch) == 1
            gaps = [name for name, value in operation["transaction"].items() if not value]
            expected = ", ".join(f"{name}=false" for name in gaps) or "none"
            gap = f'<span class="transaction-gaps" data-transaction-for="{key}">{expected}</span>'
            assert text.count(gap) == 1
        if row.get("delegation"):
            assert row["delegation"]["immediate_callee"] in text
    assert 'issues/3475"' not in text
    for issue in range(3476, 3480):
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


def test_delivery_contract_is_in_digest_union():
    checker, records, registry, *_ = contract_inputs()
    union = checker.digest_record_union(registry, records)
    digest_sources = (
        b"tests/enforcement/test_scheduler_mutation_delivery.py",
        b".github/workflows/enforcement-gate.yml",
        b".github/workflows/scheduler-mutation-main.yml",
    )
    first = checker.input_digest(records[checker.REGISTRY], union)
    for source in digest_sources:
        assert source in union
        mutated = dict(union)
        mutated[source] += b"\n# contract change"
        second = checker.input_digest(records[checker.REGISTRY], mutated)
        assert first != second


def test_rule_and_ops_define_scheduler_target_binding_contract():
    rule = RULE.read_text()
    ops = OPS.read_text()
    for phrase in (
        "scheduler identity",
        "physical-local",
        "explicit-remote-transport",
    ):
        assert phrase in rule
    for phrase in (
        "current-user-cron",
        "root-cron",
        "systemd-user",
        "windows-current-user-task",
        "physical-local",
        "explicit-remote-transport",
    ):
        assert phrase in ops


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


def test_main_push_scheduler_workflow_is_fail_closed():
    workflow_text = MAIN_WORKFLOW.read_text()
    workflow = yaml.load(workflow_text, Loader=yaml.BaseLoader)
    push = workflow["on"]["push"]
    assert push["branches"] == ["main"]
    assert "paths" not in push

    job = workflow["jobs"]["scheduler-mutation-surfaces"]
    assert job["runs-on"] == "ubuntu-latest"
    assert job.get("continue-on-error") not in {"true", True}
    steps = job["steps"]
    checkout = next(step for step in steps if step.get("uses") == "actions/checkout@v4")
    assert checkout["with"]["fetch-depth"] == "0"
    python = next(step for step in steps if step.get("uses") == "actions/setup-python@v5")
    assert python["with"]["python-version"] == "3.12"
    assert any(step.get("uses") == "astral-sh/setup-uv@v4" for step in steps)

    expected_commands = {
        "uv run python scripts/enforcement/check-scheduler-mutation-surfaces.py",
        "uv run python scripts/cron/build-cron-identity-inventory.py --check",
        (
            "uv run python scripts/enforcement/check-scheduler-mutation-surfaces.py "
            "--check-html docs/reports/2026-07-11-issue-3470-scheduler-mutation-safety.html"
        ),
    }
    runs = {step["run"].strip() for step in steps if "run" in step}
    assert runs == expected_commands
    for step in steps:
        assert step.get("continue-on-error") not in {"true", True}
    assert "|| true" not in workflow_text
    assert "set +e" not in workflow_text


def test_merge_rule_requires_clean_helper_and_landed_validation():
    rule = MERGE_RULE.read_text()
    for phrase in (
        "Explicit user authorization never waives",
        "`mergeStateStatus == CLEAN`",
        "`scripts/operations/merge-when-clean.sh --merge`",
        "`git fetch origin main`",
        "actual landed `origin/main`",
        "changed-domain generated-artifact checks",
    ):
        assert phrase in rule
