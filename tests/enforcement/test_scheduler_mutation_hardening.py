"""Adversarial hardening tests for the scheduler mutation contract."""
from __future__ import annotations

import copy
import importlib.util
import sys
from pathlib import Path

import pytest
import yaml

REPO = Path(__file__).resolve().parents[2]
CHECKER = REPO / "scripts/enforcement/check-scheduler-mutation-surfaces.py"
REGISTRY = REPO / "config/scheduled-tasks/mutation-surfaces.yaml"


def load_checker():
    spec = importlib.util.spec_from_file_location("scheduler_hardening_checker", CHECKER)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def current_contract():
    checker = load_checker()
    records = checker.read_index_records(REPO)
    return checker, records, yaml.safe_load(REGISTRY.read_bytes())


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
        lambda _c, _r, x: x["surfaces"][0]["operations"][0].update(target_kind="remote-magic"),
        lambda _c, _r, x: x["surfaces"][0]["operations"][0]["authority_branches"][0].update(strength="trusted-because-note"),
        lambda _c, _r, x: x["disposition_groups"][0]["issue"].update(number=3470),
    ],
)
def test_closed_schema_rejects_unknown_versions_keys_enums_and_self_issue(mutator):
    assert validate_changed(mutator).errors


def test_declared_operations_equal_discovered_primitives_per_path():
    def mutate(_checker, records, _registry):
        records[b"scripts/windows/setup-scheduler-tasks.ps1"] += b"\nSet-ScheduledTask -TaskName Added\n"

    assert any("primitive" in error for error in validate_changed(mutate).errors)


def test_transaction_attestations_reject_semantic_inversions():
    checker, records, _ = current_contract()
    source = b"scripts/cron/cron_apply.py"
    body = records[source]
    mutations = [
        body.replace(b"A = _read()", b"A = ''"),
        body.replace(b"current = _read()", b"current = A", 1),
        body.replace(b"backup = create_backup(canonical_id, ts, A)", b"backup = create_backup(canonical_id, ts, '')"),
    ]
    names = ["python-baseline-snapshot-v1", "python-prewrite-cas-v1", "python-backup-baseline-v1"]
    for name, mutated in zip(names, mutations):
        records[source] = mutated
        assert not checker.evaluate_attestation(name, records, source)


def test_transaction_attestations_reject_reorder_decoy_and_wrong_scope():
    checker, records, _ = current_contract()
    source = b"scripts/cron/cron_apply.py"
    body = records[source]
    backup = b"        backup = create_backup(canonical_id, ts, A)\n"
    write = b"        _write(plan[\"new_text\"])\n"
    records[source] = body.replace(backup + write, write + backup)
    assert not checker.evaluate_attestation("python-backup-baseline-v1", records, source)
    records[source] = body.replace(b"        _write(plan[\"new_text\"])\n", b"    _write(plan[\"new_text\"])\n")
    assert not checker.evaluate_attestation("python-lock-scope-v1", records, source)
    records[source] = body.replace(b"                _write(A)", b"            _write(A)")
    assert not checker.evaluate_attestation("python-rollback-after-cas-v1", records, source)


def test_classifier_rejects_fourth_route_reusing_existing_reason():
    checker, records, _ = current_contract()
    source = b"scripts/cron/cron_transaction.py"
    needle = b"    return {\"line\": line, \"class\": \"uncataloged\", \"reason\": \"no-match\"}"
    extra = b"    if line == 'extra':\n        return {'line': line, 'class': 'cataloged', 'reason': 'catalog-command'}\n"
    records[source] = records[source].replace(needle, extra + needle)
    assert checker.derive_cron_classifier_branches(records) is None


def test_installed_fingerprint_mechanisms_are_derived_from_catalog():
    checker, records, registry = current_contract()
    assert checker.derive_installed_fingerprint_branches(records) == {
        "installed-fingerprint-token", "installed-fingerprint-substring"
    }
    cron = next(row for row in registry["surfaces"] if row["path"] == "scripts/cron/cron_apply.py")
    ids = {branch["id"] for branch in cron["operations"][0]["authority_branches"]}
    assert {"installed-fingerprint-token", "installed-fingerprint-substring"} <= ids


def test_wrapper_guard_must_precede_mutation_exec_and_reject_decoy():
    checker, records, _ = current_contract()
    source = b"scripts/cron/setup-cron.sh"
    body = records[source]
    exec_line = b'exec uv run --script "$CRON_APPLY" "${APPLY_ARGS[@]}"\n'
    records[source] = exec_line + body.replace(exec_line, b"")
    assert not checker.evaluate_attestation("shell-physical-host-equality-guard-v1", records, source)
    records[source] = body.replace(b"exit 2\nfi", b"echo exit-2-decoy\nfi")
    assert not checker.evaluate_attestation("shell-physical-host-equality-guard-v1", records, source)


def test_executable_sentinel_in_forensic_path_is_not_suppressed():
    checker = load_checker()
    body = b'import subprocess\nsubprocess.run(["crontab", "-"])  # scheduler-mutation-forensic\n'
    found = checker.discover_mutation_surfaces({checker.CHECKER: body})
    assert found.direct == {checker.CHECKER.decode()}


def test_disposition_mapping_is_checker_owned_and_bidirectional():
    def wrong_issue(_checker, _records, registry):
        registry["disposition_groups"][0]["issue"]["number"] = 9999

    def wrong_row_group(_checker, _records, registry):
        registry["surfaces"][0]["disposition_group"] = "legacy-crontab-writers"

    def duplicate_group(_checker, _records, registry):
        registry["disposition_groups"].append(copy.deepcopy(registry["disposition_groups"][0]))

    for mutation in (wrong_issue, wrong_row_group, duplicate_group):
        assert validate_changed(mutation).errors


def test_branch_strength_requires_source_attestation_and_duplicate_ids_fail():
    def mutate(_checker, _records, registry):
        windows = next(row for row in registry["surfaces"] if row["path"] == "scripts/coordination/context/setup_scheduled_task.ps1")
        branch = windows["operations"][0]["authority_branches"][0]
        windows["operations"][0]["authority_branches"].append(copy.deepcopy(branch))

    assert any("branch" in error for error in validate_changed(mutate).errors)


def test_wrapper_call_form_and_local_guard_are_source_attested():
    def mutate(_checker, records, _registry):
        source = b"scripts/cron/setup-cron.sh"
        records[source] = records[source].replace(b'exec uv run --script "$CRON_APPLY"', b'echo "$CRON_APPLY"')

    assert any("call" in error or "guard" in error for error in validate_changed(mutate).errors)


def test_production_sentinel_and_raw_systemd_writer_cannot_bypass_discovery():
    checker = load_checker()
    body = b'cat > "$HOME/.config/systemd/user/x.service" # scheduler-mutation-forensic\n'
    found = checker.discover_mutation_surfaces({b"scripts/prod.sh": body})
    assert found.primitives["scripts/prod.sh"] == {"systemd-user-unit-write"}


def test_digest_union_excludes_registry_record_and_rejects_missing_mapping():
    checker, records, registry = current_contract()
    assert checker.REGISTRY not in checker.digest_record_union(registry, records)
    registry["surfaces"][0]["operations"][0]["attestations"].append("missing-id")
    with pytest.raises((KeyError, ValueError)):
        checker.digest_record_union(registry, records)
