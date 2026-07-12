"""Contract tests for the tracked scheduler-mutation inventory."""

from __future__ import annotations

import importlib.util
import copy
import os
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
    assert payload["direct"] == sorted(DIRECT)
    assert payload["transitive"] == sorted(TRANSITIVE)
    assert payload["errors"] == []
    assert payload["status"] == "ok"
    assert len(payload["input_digest"]) == 64


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


def current_contract():
    checker = load_checker()
    records = checker.read_index_records(REPO_ROOT)
    registry = yaml.safe_load(REGISTRY.read_bytes())
    return checker, records, registry


@pytest.mark.parametrize(
    ("attestation", "unsafe"),
    [
        ("python-physical-host-equality-guard-v1", b"# refusing local crontab reconciliation\n"),
        ("python-prewrite-baseline-cas-v1", b"# if current != A\n_write(new)\n"),
        ("python-rollback-after-cas-v1", b"# if current != after\n_write(A)\n"),
        ("windows-current-user-principal-v1", b"# -UserId $env:USERNAME\nRegister-ScheduledTask -TaskName X\n"),
        ("windows-task-set-operation-v1", b"# Set-ScheduledTask -TaskName\n"),
        ("shell-exact-sentinel-v1", b"# grep -vF \"$CRON_SENTINEL\"\nrun_crontab -\n"),
    ],
)
def test_closed_attestation_evaluators_reject_mutated_source_shapes(attestation, unsafe):
    checker, records, _ = current_contract()
    source = checker.attestation_source(attestation)
    records[source] = unsafe
    assert checker.evaluate_attestation(attestation, records, source) is False


def test_classifier_branch_set_is_complete_and_exact():
    checker, records, registry = current_contract()
    expected = checker.derive_cron_classifier_branches(records)
    assert expected == {"installed-fingerprint", "catalog-key-fallback", "preserved-promotion"}
    cron = next(row for row in registry["surfaces"] if row["path"] == "scripts/cron/cron_apply.py")
    cron["operations"][0]["authority_branches"].pop()
    result = checker.validate_registry(registry, checker.discover_mutation_surfaces(records), records)
    assert any("branch set" in error for error in result.errors)
    records[b"scripts/cron/cron_transaction.py"] += b"\nif extra_route: return {'class': 'cataloged'}\n"
    assert checker.derive_cron_classifier_branches(records) is None


def test_discovery_covers_every_declared_primitive():
    checker = load_checker()
    records = {
        b"scripts/a.sh": b"printf x | run_crontab -\n",
        b"scripts/b.sh": b"write_unit \"$SERVICE_PATH\"\nremove_unit \"$SERVICE_PATH\"\n",
        b"scripts/c.sh": b"run_systemctl enable --now x.timer\n",
        b"scripts/d.ps1": b"Set-ScheduledTask -TaskName X\n",
    }
    found = checker.discover_mutation_surfaces(records)
    assert found.primitives == {
        "scripts/a.sh": {"crontab-replace"},
        "scripts/b.sh": {"systemd-user-unit-write"},
        "scripts/c.sh": {"systemd-user-enable-disable"},
        "scripts/d.ps1": {"windows-task-set"},
    }


def test_config_sources_are_tracked_connected_and_corrected():
    checker, records, registry = current_contract()
    cron = next(row for row in registry["surfaces"] if row["path"] == "scripts/cron/cron_apply.py")
    branches = {b["id"]: b for b in cron["operations"][0]["authority_branches"]}
    assert branches["preserved-promotion"]["config_source"] == "config/workstations/harness-state-classes.yaml"
    branches["preserved-promotion"]["config_source"] = "missing.yaml"
    result = checker.validate_registry(registry, checker.discover_mutation_surfaces(records), records)
    assert any("config_source" in error for error in result.errors)


def test_kanban_backend_operation_set_includes_install_and_uninstall():
    checker, records, _ = current_contract()
    operations = checker.derive_kanban_operations(records)
    assert operations == {
        "install:systemd-unit-write", "install:systemd-enable",
        "install:crontab-replace", "uninstall:systemd-unit-remove",
        "uninstall:systemd-disable", "uninstall:crontab-replace",
    }
    records[b"scripts/install/setup-kanban-loader-timer.sh"] = records[b"scripts/install/setup-kanban-loader-timer.sh"].replace(b"remove_unit \"$SERVICE_PATH\"", b":")
    assert checker.derive_kanban_operations(records) != operations


def test_true_transaction_guarantees_require_specific_attestations():
    checker, records, registry = current_contract()
    cron = next(row for row in registry["surfaces"] if row["path"] == "scripts/cron/cron_apply.py")
    cron["operations"][0]["attestations"].remove("python-prewrite-cas-v1")
    result = checker.validate_registry(registry, checker.discover_mutation_surfaces(records), records)
    assert any("pre_write_cas" in error for error in result.errors)


def test_digest_uses_exact_plan_defined_union_and_cli_emits_it():
    checker, records, registry = current_contract()
    selected = checker.digest_record_union(registry, records)
    assert b".github/workflows/enforcement-gate.yml" in selected
    assert b"scripts/enforcement/check-scheduler-mutation-surfaces.py" in selected
    completed = subprocess.run([sys.executable, str(CHECKER), "--json"], cwd=REPO_ROOT, text=True, capture_output=True)
    payload = json.loads(completed.stdout)
    assert payload["input_digest"] == checker.input_digest(REGISTRY.read_bytes(), selected)


def test_index_bytes_win_over_dirty_worktree(tmp_path):
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    path = tmp_path / "tracked.sh"
    path.write_text("indexed\n")
    subprocess.run(["git", "add", "tracked.sh"], cwd=tmp_path, check=True)
    path.write_text("dirty\n")
    assert load_checker().read_index_records(tmp_path)[b"tracked.sh"] == b"indexed\n"


def test_cat_file_transport_handles_odd_path_bytes(tmp_path):
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    root = os.fsencode(tmp_path)
    fixtures = {
        b"line\nname.sh": b"newline", b"tab\tname.sh": b"tab",
        b"-leading.sh": b"dash", b"nonutf8-\xff.sh": b"bytes",
    }
    for name, body in fixtures.items():
        fd = os.open(root + b"/" + name, os.O_WRONLY | os.O_CREAT, 0o644)
        os.write(fd, body)
        os.close(fd)
        subprocess.run([b"git", b"add", b"--", name], cwd=root, check=True)
    records = load_checker().read_index_records(tmp_path)
    assert {name: records[name] for name in fixtures} == fixtures


def test_transitive_guard_and_unknown_indirection_fail_closed():
    checker, records, registry = current_contract()
    wrapper = next(row for row in registry["surfaces"] if row["kind"] == "transitive-entrypoint")
    wrapper["edge"]["target_guard_attestation"] = "unknown-id"
    result = checker.validate_registry(registry, checker.discover_mutation_surfaces(records), records)
    assert any("target_guard" in error for error in result.errors)
    found = checker.discover_mutation_surfaces({b"scripts/x.sh": b"$SCHEDULER_INSTALLER --apply\n"})
    assert "scripts/x.sh" in found.unknown_edges


def test_duplicate_operation_ids_are_rejected():
    checker, records, registry = current_contract()
    row = registry["surfaces"][0]
    row["operations"].append(copy.deepcopy(row["operations"][0]))
    result = checker.validate_registry(registry, checker.discover_mutation_surfaces(records), records)
    assert any("duplicate operation" in error for error in result.errors)


def test_dedicated_disposition_coordinates_are_exact():
    _, _, registry = current_contract()
    groups = {g["group_id"]: g["issue"]["number"] for g in registry["disposition_groups"]}
    assert groups == {
        "cron-catalog-migration": 3475, "legacy-crontab-writers": 3476,
        "kanban-dual-backend": 3477, "windows-task-writers": 3478,
        "harness-update": 3479,
    }


def validate_changed(mutator):
    checker, records, registry = current_contract()
    mutator(checker, records, registry)
    return checker.validate_registry(
        registry, checker.discover_mutation_surfaces(records), records
    )


@pytest.mark.parametrize(
    "mutator",
    [
        lambda _c, _r, x: x.update(schema_version=2),
        lambda _c, _r, x: x["surfaces"][0].update(owner="descriptive"),
        lambda _c, _r, x: x["surfaces"][0]["operations"][0].update(
            target_kind="remote-magic"
        ),
        lambda _c, _r, x: x["surfaces"][0]["operations"][0][
            "authority_branches"
        ][0].update(strength="trusted-because-note"),
        lambda _c, _r, x: x["disposition_groups"][0]["issue"].update(number=3470),
    ],
)
def test_closed_schema_rejects_unknown_versions_keys_enums_and_self_issue(mutator):
    assert validate_changed(mutator).errors


def test_declared_operations_equal_discovered_primitives_per_path():
    def mutate(_checker, records, _registry):
        records[b"scripts/windows/setup-scheduler-tasks.ps1"] += (
            b"\nSet-ScheduledTask -TaskName Added\n"
        )

    result = validate_changed(mutate)
    assert any("primitive" in error for error in result.errors)


def test_transaction_attestations_reject_semantic_inversions():
    checker, records, _ = current_contract()
    source = b"scripts/cron/cron_apply.py"
    body = records[source]
    records[source] = body.replace(b"A = _read()", b"A = ''")
    assert not checker.evaluate_attestation(
        "python-baseline-snapshot-v1", records, source
    )
    records[source] = body.replace(b"current = _read()", b"current = A", 1)
    assert not checker.evaluate_attestation("python-prewrite-cas-v1", records, source)
    records[source] = body.replace(
        b"backup = create_backup(canonical_id, ts, A)",
        b"backup = create_backup(canonical_id, ts, '')",
    )
    assert not checker.evaluate_attestation("python-backup-baseline-v1", records, source)


def test_classifier_rejects_fourth_route_reusing_existing_reason():
    checker, records, _ = current_contract()
    source = b"scripts/cron/cron_transaction.py"
    body = records[source]
    needle = b"    return {\"line\": line, \"class\": \"uncataloged\", \"reason\": \"no-match\"}"
    extra = (
        b"    if line == 'extra':\n"
        b"        return {'line': line, 'class': 'cataloged', "
        b"'reason': 'catalog-command'}\n"
    )
    records[source] = body.replace(needle, extra + needle)
    assert checker.derive_cron_classifier_branches(records) is None


def test_branch_strength_requires_source_attestation_and_duplicate_ids_fail():
    def mutate(_checker, _records, registry):
        windows = next(
            row for row in registry["surfaces"]
            if row["path"] == "scripts/coordination/context/setup_scheduled_task.ps1"
        )
        branch = windows["operations"][0]["authority_branches"][0]
        windows["operations"][0]["authority_branches"].append(copy.deepcopy(branch))

    result = validate_changed(mutate)
    assert any("branch" in error for error in result.errors)


def test_wrapper_call_form_and_local_guard_are_source_attested():
    def mutate(_checker, records, _registry):
        source = b"scripts/cron/setup-cron.sh"
        records[source] = records[source].replace(
            b'exec uv run --script "$CRON_APPLY"', b'echo "$CRON_APPLY"'
        )

    result = validate_changed(mutate)
    assert any("call" in error or "guard" in error for error in result.errors)
    checker = load_checker()
    found = checker.discover_mutation_surfaces(
        {b"scripts/x.sh": b'runner=scripts/cron/setup-cron.sh\nbash "$runner"\n'}
    )
    assert "scripts/x.sh" in found.unknown_edges


def test_production_sentinel_and_raw_systemd_writer_cannot_bypass_discovery():
    checker = load_checker()
    found = checker.discover_mutation_surfaces(
        {
            b"scripts/prod.sh": (
                b'cat > "$HOME/.config/systemd/user/x.service" '
                b'# scheduler-mutation-forensic\n'
            )
        }
    )
    assert found.direct == {"scripts/prod.sh"}
    assert found.primitives["scripts/prod.sh"] == {"systemd-user-unit-write"}


def test_digest_union_excludes_registry_record_and_rejects_missing_mapping():
    checker, records, registry = current_contract()
    selected = checker.digest_record_union(registry, records)
    assert checker.REGISTRY not in selected
    registry["surfaces"][0]["operations"][0]["attestations"].append("missing-id")
    with pytest.raises((KeyError, ValueError)):
        checker.digest_record_union(registry, records)


def test_disposition_defect_classes_match_dedicated_issues():
    _, _, registry = current_contract()
    assert {g["group_id"]: g["defect_class"] for g in registry["disposition_groups"]} == {
        "cron-catalog-migration": "mixed-destructive-ownership-authority",
        "legacy-crontab-writers": "untransactional-whole-crontab-replacement",
        "kanban-dual-backend": "untransactional-dual-backend-replacement",
        "windows-task-writers": "windows-task-mutation-without-verified-transaction",
        "harness-update": "transitive-mutation-error-swallowing",
    }
