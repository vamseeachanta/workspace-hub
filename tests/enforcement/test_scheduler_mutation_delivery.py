"""Delivery tests for scheduler mutation HTML and CI wiring."""
from __future__ import annotations

import importlib.util
import html
import subprocess
import sys
from pathlib import Path

import pytest
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
INVENTORY = ROOT / "scripts/cron/build-cron-identity-inventory.py"


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
    equals_check = subprocess.run(
        [sys.executable, str(CHECKER), f"--check-html={output}"], cwd=ROOT
    )
    assert equals_check.returncode == 0
    output.write_bytes(output.read_bytes().replace(b"data-input-digest=", b"data-stale-digest="))
    stale = subprocess.run(
        [sys.executable, str(CHECKER), "--check-html", str(output)], cwd=ROOT
    )
    assert stale.returncode != 0


def test_delivery_contract_is_in_digest_union():
    checker, records, registry, *_ = contract_inputs()
    union = checker.digest_record_union(registry, records)
    delivery = b"tests/enforcement/test_scheduler_mutation_delivery.py"
    assert delivery in union
    mutated = dict(union)
    mutated[delivery] += b"\n# contract change"
    first = checker.input_digest(records[checker.REGISTRY], union)
    second = checker.input_digest(records[checker.REGISTRY], mutated)
    assert first != second

    for workflow in (
        b".github/workflows/enforcement-gate.yml",
        b".github/workflows/scheduler-mutation-main.yml",
    ):
        assert workflow in union
        changed = dict(union)
        changed[workflow] += b"\n# workflow drift"
        assert checker.input_digest(records[checker.REGISTRY], changed) != first


def test_main_push_scheduler_workflow_is_fail_closed():
    workflow = yaml.load(MAIN_WORKFLOW.read_text(), Loader=yaml.BaseLoader)
    assert workflow["on"] == {"push": {"branches": ["main"]}}
    assert "paths" not in workflow["on"]["push"]
    assert "paths-ignore" not in workflow["on"]["push"]
    job = workflow["jobs"]["scheduler-mutation-surfaces"]
    assert job["runs-on"] == "ubuntu-latest"
    assert job.get("continue-on-error") not in {"true", True}
    steps = job["steps"]
    checkout = next(step for step in steps if step.get("uses") == "actions/checkout@v4")
    assert checkout["with"]["fetch-depth"] == "0"
    assert any(
        step.get("uses") == "actions/setup-python@v5"
        and step.get("with", {}).get("python-version") == "3.12"
        for step in steps
    )
    assert any(step.get("uses") == "astral-sh/setup-uv@v4" for step in steps)
    commands = [step["run"] for step in steps if "run" in step]
    assert len(commands) == 1
    command = commands[0]
    for required in (
        "set -euo pipefail",
        "git --no-replace-objects rev-parse 'HEAD^{tree}'",
        "git --no-replace-objects ls-tree -z",
        "python -I -S",
        "--tree-oid",
        " all",
    ):
        assert required in command
    assert command.index('snapshot_helper="$(mktemp)"') < command.index(
        "trap cleanup_snapshot EXIT"
    ) < command.index('snapshot_entry="$(mktemp)"')
    assert "^([0-9a-f]{40}|[0-9a-f]{64})$" in command
    assert "[[ \"$helper_mode\" == 100644 || \"$helper_mode\" == 100755 ]]" in command
    assert '[[ "$helper_type" == blob ]]' in command
    assert 'git --no-replace-objects cat-file blob "$helper_oid"' in command
    assert (
        '[[ "$(git --no-replace-objects hash-object "$snapshot_helper")" '
        '== "$helper_oid" ]]' in command
    )
    assert (
        'python -I -S "$snapshot_helper" --tree-oid "$tree_oid" all' in command
    )
    assert "git write-tree" not in command
    assert command.count(" all") == 1
    assert "|| true" not in command
    assert "set +e" not in command


def test_merge_rule_requires_clean_helper_and_landed_validation():
    text = MERGE_RULE.read_text(encoding="utf-8")
    for phrase in (
        "mergeStateStatus",
        "CLEAN",
        "scripts/operations/merge-when-clean.sh --merge",
        "origin/main",
        "landed",
    ):
        assert phrase in text


def test_direct_tracked_entrypoints_require_captured_coordinator():
    commands = [
        [sys.executable, str(INVENTORY), "--check"],
        [sys.executable, str(INVENTORY), "--check", "--captured-tree"],
        [sys.executable, str(CHECKER)],
        [sys.executable, str(CHECKER), "--captured-tree"],
        [sys.executable, str(CHECKER), "--json"],
        [sys.executable, str(CHECKER), "--json", "--captured-tree"],
        [sys.executable, str(CHECKER), "--check-html", REPORT.relative_to(ROOT).as_posix()],
    ]
    for command in commands:
        completed = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
        assert completed.returncode != 0
        assert "captured-tree coordinator" in completed.stdout + completed.stderr


@pytest.mark.parametrize("helper_mode", ["missing", "120000", "160000"])
def test_bootstrap_rejects_missing_or_nonregular_helper(tmp_path, helper_mode):
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
    if helper_mode != "missing":
        oid = subprocess.check_output(
            ["git", "hash-object", "-w", "--stdin"], cwd=repo,
            input=b"captured target\n",
        ).decode().strip()
        subprocess.run(
            ["git", "update-index", "--add", "--cacheinfo",
             f"{helper_mode},{oid},scripts/lib/git_index_snapshot.py"],
            cwd=repo, check=True,
        )
    workflow = yaml.load(MAIN_WORKFLOW.read_text(), Loader=yaml.BaseLoader)
    command = next(
        step["run"]
        for step in workflow["jobs"]["scheduler-mutation-surfaces"]["steps"]
        if "run" in step
    )
    needle = "git --no-replace-objects rev-parse 'HEAD^{tree}'"
    command = command.replace(needle, "git --no-replace-objects write-tree")
    completed = subprocess.run(["bash", "-c", command], cwd=repo)
    assert completed.returncode != 0


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
    runs = [step["run"] for step in steps if "run" in step]
    assert len(runs) == 1
    command = runs[0]
    assert 'git --no-replace-objects rev-parse \'HEAD^{tree}\'' in command
    assert 'python -I -S "$snapshot_helper" --tree-oid "$tree_oid" all' in command
    assert "uv run python scripts/" not in command
    assert "|| true" not in command
    assert "set +e" not in command
