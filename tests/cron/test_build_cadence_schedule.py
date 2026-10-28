"""Synthetic, hand-enumerated examples for the cadence index CLI.

All schedule numbers are authored fixture values, not production data. Expected
rows below are independent transcriptions: primary has the hostname override,
secondary has the default, and the alternate token resolves to primary. This
precedence follows cron_render.build_context/effective_schedule.
"""
from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys

import pytest
import yaml


REPO = Path(__file__).resolve().parents[2]  # tests/cron is two levels below root.
ENTRYPOINT = REPO / "scripts" / "cron" / "build-cadence-schedule.sh"
RENDERER = ENTRYPOINT.with_name("cadence_schedule.py")
REGISTRY = """\
machines:
  primary:
    hostname: target-primary
    hostname_aliases: [alternate]
  secondary:
    hostname: target-secondary
"""
CATALOG = """\
tasks:
  - id: zeta
    cadence: weekly
    scheduler: windows-task-scheduler
    machines: [secondary]
    schedule: weekly trigger
    command: unused
  - id: alpha
    cadence: nightly
    machines: [secondary, alternate, primary]
    schedule: '17 3 * * *'
    schedule_by_machine:
      ' TARGET-PRIMARY ': '23 4 * * *'
      primary: '31 5 * * *'
      alternate: '41 6 * * *'
    command: unused
  - id: beta
    machines: []
    schedule: '*/13 * * * *'
    command: unused
"""
# Independently hand-enumerated, ordered by task then canonical target.
EXPECTED = """\
# Cadence schedule

Declared schedules only; this index does not install or execute tasks.
Cadence is unspecified where the catalog does not declare it.

| Task | Cadence | Scheduler | Target | Schedule |
| --- | --- | --- | --- | --- |
| alpha | nightly | cron | primary | 23 4 * * * |
| alpha | nightly | cron | secondary | 17 3 * * * |
| beta | unspecified | cron | unspecified | */13 * * * * |
| zeta | weekly | windows-task-scheduler | secondary | weekly trigger |
"""


def run_cli(tmp_path, catalog=CATALOG, *, registry=REGISTRY, shell=True):
    source = tmp_path / "input.yaml"
    source.write_text(catalog, encoding="utf-8", newline="\n")
    registry_path = tmp_path / "registry.yaml"
    registry_path.write_text(registry, encoding="utf-8", newline="\n")
    output = tmp_path / "index.md"
    command = ["bash", str(ENTRYPOINT)] if shell else [sys.executable, str(RENDERER)]
    # The wrapper uses the already provisioned interpreter; no tool downloads.
    env = {**os.environ, "PYTHON": sys.executable}
    result = subprocess.run(
        [*command, "--input", str(source), "--output", str(output),
         "--registry", str(registry_path)],
        env=env, cwd=tmp_path, capture_output=True, text=True, check=False,
    )
    return result, output


@pytest.mark.parametrize("shell", [True, False])
def test_cli_exact_rows_and_order_independent_of_input(tmp_path, shell):
    first, output = run_cli(tmp_path, shell=shell)
    assert first.returncode == 0, first.stderr  # CLI success convention.
    assert output.read_text(encoding="utf-8") == EXPECTED
    data = yaml.safe_load(CATALOG)
    data["tasks"].reverse()
    for task in data["tasks"]:
        task["machines"].reverse()
        if "schedule_by_machine" in task:
            task["schedule_by_machine"] = dict(reversed(task["schedule_by_machine"].items()))
    second, output = run_cli(tmp_path, yaml.safe_dump(data), shell=shell)
    assert second.returncode == 0, second.stderr
    assert output.read_text(encoding="utf-8") == EXPECTED


def test_aliases_match_shared_renderer(tmp_path, monkeypatch):
    monkeypatch.syspath_prepend(str(RENDERER.parent))
    import cron_render

    task = yaml.safe_load(CATALOG)["tasks"][1]  # alpha is second in this fixture.
    registry = yaml.safe_load(REGISTRY)
    for token in ("primary", "alternate", "TARGET-PRIMARY"):
        context = cron_render.build_context(token, registry=registry)
        assert cron_render.effective_schedule(task, context) == "23 4 * * *"
    result, output = run_cli(tmp_path)
    assert result.returncode == 0, result.stderr
    assert "| alpha | nightly | cron | primary | 23 4 * * * |" in output.read_text(encoding="utf-8")
    assert "| alternate |" not in output.read_text(encoding="utf-8")


def test_commands_are_not_executed_or_copied(tmp_path):
    marker = tmp_path / "must-not-exist"
    data = yaml.safe_load(CATALOG)
    for task in data["tasks"]:
        task["command"] = f'touch "{marker}"'
    result, output = run_cli(tmp_path, yaml.safe_dump(data))
    assert result.returncode == 0, result.stderr
    assert not marker.exists()
    assert output.read_text(encoding="utf-8") == EXPECTED


@pytest.mark.parametrize("catalog, error", [
    ("[", "YAML"),
    ("", "mapping"),
    ("[]", "mapping"),
    ("{}", "tasks"),
    ("tasks: null", "tasks"),
    ("tasks: {}", "tasks"),
    ("tasks: [null]", "mapping"),
    ("tasks: [{schedule: '* * * * *'}]", "id"),
    ("tasks: [{id: false, schedule: '* * * * *'}]", "id"),
    ("tasks: [{id: alpha, schedule: '* * * * *'}, {id: alpha, schedule: '* * * * *'}]", "duplicate"),
    ("tasks: [{id: alpha}]", "schedule"),
    ("tasks: [{id: alpha, schedule: false}]", "schedule"),
    ("tasks: [{id: alpha, schedule: ''}]", "schedule"),
    ("tasks: [{id: alpha, schedule: invalid}]", "schedule"),
    ("tasks: [{id: alpha, schedule: '* * * * *', scheduler: unknown}]", "scheduler"),
    ("tasks: [{id: alpha, schedule: '* * * * *', cadence: []}]", "cadence"),
    ("tasks: [{id: alpha, schedule: '* * * * *', machines: primary}]", "machines"),
    ("tasks: [{id: alpha, schedule: '* * * * *', machines: [null]}]", "machines"),
    ("tasks: [{id: alpha, schedule: '* * * * *', schedule_by_machine: []}]", "schedule_by_machine"),
    ("tasks: [{id: alpha, schedule: '* * * * *', schedule_by_machine: {primary: false}}]", "schedule"),
])
def test_invalid_catalog_leaves_no_successful_index(tmp_path, catalog, error):
    result, output = run_cli(tmp_path, catalog)
    assert result.returncode != 0
    assert error in result.stderr
    assert "# Cadence schedule" not in result.stdout
    assert not output.exists()
    output.write_text("previous output\n", encoding="utf-8", newline="\n")
    result, output = run_cli(tmp_path, catalog)
    assert result.returncode != 0
    assert output.read_text(encoding="utf-8") == "previous output\n"


@pytest.mark.parametrize("registry", [
    "[", "[]", "machines: []", "machines: {primary: null}",
    "machines: {primary: {hostname_aliases: alternate}}",
])
def test_invalid_registry_fails_before_output(tmp_path, registry):
    result, output = run_cli(tmp_path, registry=registry)
    assert result.returncode != 0
    assert "registry" in result.stderr.lower()
    assert not output.exists()


@pytest.mark.parametrize("left, right", [
    ({"hostname_aliases": ["shared"]}, {"hostname_aliases": [" SHARED "]}),
    ({"hostname": "shared"}, {"hostname": " SHARED "}),
    ({"hostname": "shared"}, {"hostname_aliases": [" SHARED "]}),
    ({"hostname_aliases": [" SECONDARY "]}, {}),
    ({"hostname": " SECONDARY "}, {}),
])
@pytest.mark.parametrize("reverse", [False, True])
def test_registry_token_collisions_preserve_output(tmp_path, left, right, reverse):
    machines = {"primary": left, "secondary": right}
    if reverse:
        machines = dict(reversed(machines.items()))
    registry = yaml.safe_dump({"machines": machines}, sort_keys=False)
    output = tmp_path / "index.md"
    previous = b"previous output\n"
    output.write_bytes(previous)
    result, output = run_cli(tmp_path, registry=registry)
    assert result.returncode != 0
    assert "registry token collision" in result.stderr
    assert output.read_bytes() == previous


@pytest.mark.parametrize("reverse", [False, True])
def test_registry_canonical_id_collisions_preserve_output(tmp_path, reverse):
    machines = {"primary": {}, " PRIMARY ": {}}
    if reverse:
        machines = dict(reversed(machines.items()))
    output = tmp_path / "index.md"
    output.write_bytes(b"previous output\n")
    result, output = run_cli(
        tmp_path, registry=yaml.safe_dump({"machines": machines}, sort_keys=False),
    )
    assert result.returncode != 0
    assert "registry token collision" in result.stderr
    assert output.read_bytes() == b"previous output\n"


def test_registry_repeated_tokens_for_same_target_are_allowed(tmp_path):
    registry = yaml.safe_load(REGISTRY)
    registry["machines"]["primary"]["hostname_aliases"] += [
        " PRIMARY ", " TARGET-PRIMARY ", " ALTERNATE ",
    ]
    result, output = run_cli(tmp_path, registry=yaml.safe_dump(registry))
    assert result.returncode == 0, result.stderr
    assert output.read_text(encoding="utf-8") == EXPECTED


def test_missing_input_fails_without_output(tmp_path):
    result, output = run_cli(tmp_path)
    assert result.returncode == 0, result.stderr
    output_before = output.read_bytes()
    result = subprocess.run(
        [sys.executable, str(RENDERER), "--input", str(tmp_path / "absent.yaml"),
         "--output", str(output)], capture_output=True, text=True, check=False,
    )
    assert result.returncode != 0
    assert "input" in result.stderr.lower()
    assert output.read_bytes() == output_before


def test_empty_catalog_and_markdown_escaping(tmp_path):
    result, output = run_cli(tmp_path, "tasks: []")
    assert result.returncode == 0, result.stderr
    assert "| Task | Cadence | Scheduler | Target | Schedule |" in output.read_text(encoding="utf-8")
    data = {"tasks": [{"id": "a|<b>", "cadence": "one\ntwo", "schedule": "* * * * *"}]}
    result, output = run_cli(tmp_path, yaml.safe_dump(data))
    assert result.returncode == 0, result.stderr
    assert "| a&#124;&lt;b&gt; | one<br>two | cron | unspecified | * * * * * |" in output.read_text(encoding="utf-8")


def test_input_cannot_be_overwritten(tmp_path):
    source = tmp_path / "input.yaml"
    source.write_text(CATALOG, encoding="utf-8", newline="\n")
    result = subprocess.run(
        [sys.executable, str(RENDERER), "--input", str(source), "--output", str(source)],
        capture_output=True, text=True, check=False,
    )
    assert result.returncode != 0
    assert source.read_text(encoding="utf-8") == CATALOG


def test_requested_alias_keeps_precedence(tmp_path):
    registry = """\
machines:
  primary:
    hostname: target-primary
    hostname_aliases: [earlier, requested]
"""
    catalog = """\
tasks:
  - id: alpha
    machines: [requested]
    schedule: '17 3 * * *'
    schedule_by_machine:
      earlier: '23 4 * * *'
      requested: '31 5 * * *'
"""
    result, output = run_cli(tmp_path, catalog, registry=registry)
    assert result.returncode == 0, result.stderr
    # Manual precedence: requested input token precedes the remaining aliases.
    assert "| alpha | unspecified | cron | primary | 31 5 * * * |" in output.read_text(encoding="utf-8")


def test_conflicting_alias_rows_are_rejected(tmp_path):
    registry = "machines: {primary: {hostname_aliases: [earlier, requested]}}"
    catalog = """\
tasks:
  - id: alpha
    machines: [earlier, requested]
    schedule: '* * * * *'
    schedule_by_machine:
      earlier: '23 4 * * *'
      requested: '31 5 * * *'
"""
    result, output = run_cli(tmp_path, catalog, registry=registry)
    assert result.returncode != 0
    assert "conflicting" in result.stderr
    assert not output.exists()


def test_duplicate_yaml_keys_are_rejected(tmp_path):
    result, output = run_cli(tmp_path, "tasks: []\ntasks: []\n")
    assert result.returncode != 0
    assert "YAML" in result.stderr
    assert not output.exists()


@pytest.mark.parametrize("schedule", ["* * * * ?", "wrong cron field values here"])
def test_invalid_cron_fields_are_rejected(tmp_path, schedule):
    catalog = yaml.safe_dump({"tasks": [{"id": "alpha", "schedule": schedule}]})
    result, output = run_cli(tmp_path, catalog)
    assert result.returncode != 0
    assert "schedule" in result.stderr
    assert not output.exists()


def test_cron_macro_is_preserved(tmp_path):
    catalog = "tasks: [{id: alpha, schedule: '@daily'}]"
    result, output = run_cli(tmp_path, catalog)
    assert result.returncode == 0, result.stderr
    assert "| alpha | unspecified | cron | unspecified | @daily |" in output.read_text(encoding="utf-8")
