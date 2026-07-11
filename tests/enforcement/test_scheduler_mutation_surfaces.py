"""Contract tests for the tracked scheduler-mutation inventory."""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest
import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]
CHECKER = REPO_ROOT / "scripts/enforcement/check-scheduler-mutation-surfaces.py"
REGISTRY = REPO_ROOT / "config/scheduled-tasks/mutation-surfaces.yaml"

DIRECT = {
    "scripts/cron/cron_apply.py",
    "scripts/coordination/context/setup_cron.sh",
    "scripts/operations/maintenance/setup_maintenance_cron.sh",
    "scripts/setup/setup-engineering-update-cron.sh",
    "scripts/install/setup-kanban-loader-timer.sh",
    "scripts/windows/setup-scheduler-tasks.ps1",
    "scripts/coordination/context/setup_scheduled_task.ps1",
    "scripts/solver/setup-scheduler.ps1",
}
TRANSITIVE = {
    "scripts/cron/setup-cron.sh",
    "scripts/setup/new-machine-setup.sh",
    "scripts/cron/harness-update.sh",
}


def load_checker():
    spec = importlib.util.spec_from_file_location("scheduler_mutation_checker", CHECKER)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_current_mutation_inventory_is_registered():
    assert CHECKER.is_file(), "checker must exist"
    assert REGISTRY.is_file(), "registry must exist"
    checker = load_checker()
    records = checker.read_index_records(REPO_ROOT)
    discovered = checker.discover_mutation_surfaces(records)
    registry = yaml.safe_load(REGISTRY.read_bytes())
    result = checker.validate_registry(registry, discovered, records)
    assert result.errors == []
    assert discovered.direct == DIRECT
    assert discovered.transitive == TRANSITIVE
    assert {row["path"] for row in registry["surfaces"]} == DIRECT | TRANSITIVE


def test_cli_reports_machine_readable_failures_and_success():
    completed = subprocess.run(
        [sys.executable, str(CHECKER), "--json"],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
    payload = json.loads(completed.stdout)
    assert payload == {
        "direct": sorted(DIRECT),
        "errors": [],
        "status": "ok",
        "transitive": sorted(TRANSITIVE),
    }


@pytest.mark.parametrize(
    ("path", "body", "kind"),
    [
        (b"scripts/new-writer.sh", b"printf x | crontab -\n", "direct"),
        (b"scripts/new-writer.ps1", b"Register-ScheduledTask -TaskName X\n", "direct"),
        (b"scripts/wrapper.sh", b"bash scripts/cron/setup-cron.sh\n", "transitive"),
    ],
)
def test_unregistered_mutation_surface_fails(path, body, kind):
    checker = load_checker()
    records = checker.read_index_records(REPO_ROOT)
    records[path] = body
    discovered = checker.discover_mutation_surfaces(records)
    registry = yaml.safe_load(REGISTRY.read_bytes())
    result = checker.validate_registry(registry, discovered, records)
    assert any(path.decode() in error for error in result.errors)
    assert path.decode() in getattr(discovered, kind)


def test_read_only_crontab_helpers_are_not_mutators():
    checker = load_checker()
    discovered = checker.discover_mutation_surfaces(
        {
            b"scripts/status.sh": b"crontab -l\n",
            b"scripts/status.py": b"subprocess.run(['crontab', '-l'])\n",
            b"scripts/status.ps1": b"Get-ScheduledTask -TaskName X\n",
        }
    )
    assert discovered.direct == set()
    assert discovered.transitive == set()


def test_forensic_sentinel_is_path_restricted():
    checker = load_checker()
    literal = b"Register-ScheduledTask -TaskName X # scheduler-mutation-forensic\n"
    allowed = checker.discover_mutation_surfaces(
        {b"tests/enforcement/test_scheduler_mutation_surfaces.py": literal}
    )
    production = checker.discover_mutation_surfaces({b"scripts/evil.ps1": literal})
    assert allowed.direct == set()
    assert production.direct == {"scripts/evil.ps1"}


def test_status_lattice_is_deterministic():
    checker = load_checker()
    safe = checker.derive_status(
        branches=[{"destructive": True, "strength": "exact"}],
        attestations=[True],
        required_transactions=[True],
    )
    assert safe == "compliant"
    for strength in ("substring", "unknown"):
        assert checker.derive_status(
            branches=[{"destructive": True, "strength": strength}],
            attestations=[True],
            required_transactions=[True],
        ) == "migration-required"
    assert checker.derive_status([], [False], [True]) == "migration-required"
    assert checker.derive_status([], [True], [False]) == "migration-required"


def test_digest_framing_is_unambiguous_and_byte_sorted():
    checker = load_checker()
    registry = b"registry"
    left = {b"a": b"bc", b"ab": b"c"}
    right = {b"a": b"b", b"cab": b"c"}
    assert checker.input_digest(registry, left) != checker.input_digest(registry, right)
    assert checker.input_digest(registry, left) == checker.input_digest(
        registry, dict(reversed(list(left.items())))
    )
    odd = {b"line\nname": b"x", b"tab\tname": b"y", b"-dash": b"z", b"bad-\xff": b"q"}
    assert len(checker.input_digest(registry, odd)) == 64


def test_cat_file_transport_requires_nul_mode(tmp_path):
    checker = load_checker()
    git = tmp_path / "git"
    git.write_text(
        "#!/bin/sh\n"
        "if [ \"$1\" = ls-files ]; then exit 0; fi\n"
        "echo 'unknown switch Z' >&2\nexit 129\n"
    )
    git.chmod(0o755)
    with pytest.raises(checker.GitTransportError, match="Git.*-Z"):
        checker.read_index_records(tmp_path, git_command=str(git))
