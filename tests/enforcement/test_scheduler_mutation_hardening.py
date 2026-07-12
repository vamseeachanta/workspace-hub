"""Adversarial hardening tests for the scheduler mutation contract."""
from __future__ import annotations

import copy
import importlib.util
import re
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
        lambda _c, _r, x: x.update(schema_version=1),
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


@pytest.mark.parametrize(
    "body",
    [
        b'writer=crontab\nprintf x | "$writer" -\n',
        b'writer=crontab; printf x | "$writer" -\n',
        b'writer=crontab && command "$writer" -\n',
        b'writer=crontab || builtin "$writer" -\n',
        b'writer=crontab\nprintf x | command "$writer" -\n',
        b'writer=crontab\nbuiltin "$writer" - < input\n',
        b'writer=crontab\nenv MODE=safe "$writer" -\n',
        b"$writer = 'Register-ScheduledTask'\n& $writer -TaskName X\n",
        b'$writer = "Register-ScheduledTask"; & "$writer" -TaskName X\n',
        b"$writer = 'Set-ScheduledTask'\n. $writer -TaskName X\n",
        b"$writer = 'Unregister-ScheduledTask'\nInvoke-Expression \"$writer -TaskName X\"\n",
    ],
)
def test_neutral_scheduler_primitive_aliases_fail_closed(body):
    checker = load_checker()
    found = checker.discover_mutation_surfaces({b"scripts/neutral-alias.sh": body})
    assert found.unknown_edges == {"scripts/neutral-alias.sh"}


def test_windows_operation_set_includes_remove_and_replace_routes():
    checker, records, registry = current_contract()
    expected = {"remove:unregister-fixed-task", "replace:unregister-register-fixed-task"}
    assert checker.derive_windows_task_operations(records) == expected
    row = next(
        item for item in registry["surfaces"]
        if item["path"] == "scripts/windows/setup-scheduler-tasks.ps1"
    )
    assert {operation["id"] for operation in row["operations"]} == expected


def test_windows_operation_set_rejects_omitted_same_primitive_route():
    def mutate(_checker, _records, registry):
        row = next(
            item for item in registry["surfaces"]
            if item["path"] == "scripts/windows/setup-scheduler-tasks.ps1"
        )
        row["operations"] = row["operations"][:1]

    assert any("Windows operation set" in error for error in validate_changed(mutate).errors)


@pytest.mark.parametrize(
    ("old", "new", "missing"),
    [
        (
            b"Unregister-ScheduledTask -TaskName $Name -TaskPath $TaskPath -Confirm:$false",
            b"Write-Host removed-route-unregister",
            "remove:unregister-fixed-task",
        ),
        (
            b"        Unregister-ScheduledTask -TaskName $Name -TaskPath $TaskPath -Confirm:$false\n",
            b"        Write-Host removed-replacement-unregister\n",
            "replace:unregister-register-fixed-task",
        ),
        (
            b"        Register-ScheduledTask `\n",
            b"        Write-Host removed-replacement-register `\n",
            "replace:unregister-register-fixed-task",
        ),
    ],
)
def test_windows_operation_derivation_is_route_bounded(old, new, missing):
    checker, records, _registry = current_contract()
    source = b"scripts/windows/setup-scheduler-tasks.ps1"
    body = records[source]
    if missing == "remove:unregister-fixed-task":
        start = body.index(b"if ($RemoveMode)")
        end = body.index(b"    if ($PSCmdlet.ParameterSetName", start)
        records[source] = body[:start] + body[start:end].replace(old, new, 1) + body[end:]
    else:
        remove_end = body.index(b"    if ($PSCmdlet.ParameterSetName", body.index(b"if ($RemoveMode)"))
        start = body.index(b"    $existing = Get-ScheduledTask", remove_end)
        records[source] = body[:start] + body[start:].replace(old, new, 1)
    derived = checker.derive_windows_task_operations(records)
    assert missing not in derived
    other = {
        "remove:unregister-fixed-task",
        "replace:unregister-register-fixed-task",
    } - {missing}
    assert other <= derived


def test_transaction_attestations_reject_semantic_inversions():
    checker, records, _ = current_contract()
    source = b"scripts/cron/cron_apply.py"
    body = records[source]
    mutations = [
        body.replace(b"A, plan = _build_cutover(selection, classes, ownership, _read)", b"A, plan = '', {}"),
        body.replace(
            b"with _flock(LOCKFILE):\n        current = _read()",
            b"with _flock(LOCKFILE):\n        current = A",
            1,
        ),
        body.replace(b"backup = create_backup(canonical_id, ts, A)", b"backup = create_backup(canonical_id, ts, '')"),
    ]
    names = ["python-baseline-snapshot-v1", "python-prewrite-cas-v1", "python-backup-baseline-v1"]
    for name, mutated in zip(names, mutations):
        records[source] = mutated
        assert not checker.evaluate_attestation(name, records, source)
        records[source] = body


def test_transaction_attestations_reject_reorder_decoy_and_wrong_scope():
    checker, records, _ = current_contract()
    source = b"scripts/cron/cron_apply.py"
    body = records[source]
    backup = b"        backup = create_backup(canonical_id, ts, A)\n"
    write = b"        observation = _write_observation(plan[\"new_text\"], _read, _write)\n"
    records[source] = body.replace(backup + write, write + backup)
    assert not checker.evaluate_attestation("python-backup-baseline-v1", records, source)
    records[source] = body.replace(write, b"    observation = _write_observation(plan[\"new_text\"], _read, _write)\n")
    assert not checker.evaluate_attestation("python-lock-scope-v1", records, source)
    records[source] = body.replace(b"            _write(A)", b"        _write(A)")
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
    assert checker.derive_cron_classifier_branches(records) == {
        "canonical-exact-line", "legacy-exact-line"
    }
    cron = next(row for row in registry["surfaces"] if row["path"] == "scripts/cron/cron_apply.py")
    ids = {branch["id"] for branch in cron["operations"][0]["authority_branches"]}
    assert ids == {"canonical-exact-line", "legacy-exact-line"}


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


@pytest.mark.parametrize("shape", ["nested", "try"])
def test_prewrite_and_rollback_reject_conditional_abort_fallthrough(shape):
    checker, records, _ = current_contract()
    source = b"scripts/cron/cron_apply.py"
    text = records[source].decode()
    for left, name in (("A", "python-prewrite-cas-v1"), ("C", "python-rollback-after-cas-v1")):
        original = f"if current != {left}:"
        if shape == "nested":
            replacement = original + "\n            if False:" if left == "C" else original + "\n                if False:"
        else:
            replacement = original + "\n            try:" if left == "C" else original + "\n                try:"
        mutated = text.replace(original, replacement, 1)
        records[source] = mutated.encode()
        assert not checker.evaluate_attestation(name, records, source)
        records[source] = text.encode()


@pytest.mark.parametrize("shape", ["nested", "try"])
def test_python_host_guard_rejects_conditional_return_fallthrough(shape):
    checker, records, _ = current_contract()
    source = b"scripts/cron/cron_apply.py"
    text = records[source].decode()
    marker = "if mid != physical_mid:"
    insertion = "\n        if False:" if shape == "nested" else "\n        try:"
    records[source] = text.replace(marker, marker + insertion, 1).encode()
    assert not checker.evaluate_attestation("python-physical-host-equality-guard-v1", records, source)


def test_executable_single_string_sentinel_is_not_suppressed():
    checker = load_checker()
    body = b'import subprocess\nsubprocess.run("crontab -", shell=True)  # scheduler-mutation-forensic\n'
    found = checker.discover_mutation_surfaces({checker.CHECKER: body})
    assert found.direct == {checker.CHECKER.decode()}


@pytest.mark.parametrize(
    ("source", "attestation", "decoy"),
    [
        (
            b"scripts/windows/setup-scheduler-tasks.ps1",
            "windows-current-user-principal-v1",
            b'if ($false) { $principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME; Register-ScheduledTask -TaskName X -Principal $principal }\n',
        ),
        (
            b"scripts/coordination/context/setup_scheduled_task.ps1",
            "context-windows-task-path-name-v1",
            b'function NeverCalled { $TaskPath = "\\Claude\\"; Register-ScheduledTask -TaskName X -TaskPath $TaskPath }\n',
        ),
        (
            b"scripts/solver/setup-scheduler.ps1",
            "windows-task-set-operation-v1",
            b'if ($false) { if (Get-ScheduledTask -TaskName X) { Set-ScheduledTask -TaskName X } else { Register-ScheduledTask -TaskName X } }\n',
        ),
    ],
)
def test_windows_attestations_reject_dead_scope_decoys(source, attestation, decoy):
    checker, records, _ = current_contract()
    live = records[source]
    records[source] = re.sub(
        rb"(?m)^(?!\s*#).*?(?:Register|Unregister|Set)-ScheduledTask.*$",
        b"Write-Host removed-live-mutation",
        live,
    ) + decoy
    assert not checker.evaluate_attestation(attestation, records, source)


@pytest.mark.parametrize("container", ["if False:", "def never_called():"])
@pytest.mark.parametrize(
    ("attestation", "block"),
    [
        (
            "python-prewrite-cas-v1",
            """with _flock(LOCKFILE):
    current = _read()
    if current != A:
        return {}
    backup = create_backup(canonical_id, ts, A)
    _write(plan['new_text'])
    after = _read()
""",
        ),
        (
            "python-rollback-after-cas-v1",
            """with _flock(LOCKFILE):
    current = _read()
    if current != after:
        return {}
    _write(A)
""",
        ),
    ],
)
def test_transaction_attestations_reject_entire_dead_lock(container, attestation, block):
    checker = load_checker()
    indented = "\n".join(f"        {line}" for line in block.splitlines())
    source = (
        "def run_cutover():\n"
        "    A = _read()\n"
        f"    {container}\n"
        f"{indented}\n"
    ).encode()
    records = {b"scripts/cron/cron_apply.py": source}
    assert not checker.evaluate_attestation(
        attestation, records, b"scripts/cron/cron_apply.py"
    )


def test_adjacent_inert_literal_does_not_authorize_sentinel_suppression():
    checker = load_checker()
    body = (
        b'PATTERN = "ScheduledTask"\n'
        b'subprocess.run("crontab -", shell=True)  '
        b'# scheduler-mutation-forensic\n'
    )
    found = checker.discover_mutation_surfaces({checker.CHECKER: body})
    assert found.direct == {checker.CHECKER.decode()}
