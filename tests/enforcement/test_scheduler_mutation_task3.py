"""RED contract tests for #3475 scheduler-mutation governance closeout."""

from __future__ import annotations

import copy
import ast
import functools
import hashlib
import importlib.util
import json
import sys
from pathlib import Path

import yaml
import pytest


ROOT = Path(__file__).resolve().parents[2]
CHECKER = ROOT / "scripts/enforcement/check-scheduler-mutation-surfaces.py"
REGISTRY = ROOT / "config/scheduled-tasks/mutation-surfaces.yaml"
INVENTORY = ROOT / "docs/reports/issue-3475-command-identity-inventory.json"


def load_checker():
    spec = importlib.util.spec_from_file_location("task3_scheduler_checker", CHECKER)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


@functools.cache
def _contract_baseline():
    checker = load_checker()
    records = checker.read_index_records(ROOT)
    registry = yaml.safe_load(records[checker.REGISTRY])
    discovered = checker.discover_mutation_surfaces(records)
    return checker, records, registry, discovered


def current_contract():
    checker, records, registry, discovered = _contract_baseline()
    return checker, dict(records), copy.deepcopy(registry), copy.deepcopy(discovered)


def by_path(registry):
    return {row["path"]: row for row in registry["surfaces"]}


def test_cron_authority_is_exact_and_3475_is_resolved():
    checker, records, registry, discovered = current_contract()
    result = checker.validate_registry(registry, discovered, records)
    assert result.errors == []

    rows = by_path(registry)
    cron = rows["scripts/cron/cron_apply.py"]
    assert "disposition_group" not in cron
    operation = cron["operations"][0]
    assert operation["authority_branches"] == [
        {
            "id": "canonical-exact-line",
            "mechanism": "canonical-exact-line",
            "config_source": "config/scheduled-tasks/schedule-tasks.yaml",
            "destructive": True,
            "strength": "exact",
        },
        {
            "id": "legacy-exact-line",
            "mechanism": "legacy-exact-line",
                "config_source": "config/workstations/harness-state-classes.yaml",
            "destructive": True,
            "strength": "exact",
        },
    ]
    assert set(operation["transaction"].values()) == {True}
    assert {
        "python-postwrite-exact-state-v1",
        "python-rollback-exact-baseline-v1",
        "cron-canonical-legacy-exact-authority-v1",
    } <= set(operation["attestations"])

    inventory_digest = json.loads(INVENTORY.read_text())["input_digest"]
    assert registry["resolved_dispositions"] == [
        {
            "issue": 3475,
            "members": [
                "scripts/cron/cron_apply.py",
                "scripts/cron/setup-cron.sh",
                "scripts/setup/new-machine-setup.sh",
            ],
            "resolved_on": "2026-07-12",
            "pull_request": 3492,
            "source_digest": inventory_digest,
        }
    ]
    assert {group["issue"]["number"] for group in registry["disposition_groups"]} == {
        3476, 3477, 3478, 3479
    }


def test_transitive_surfaces_are_closed_delegations_with_visible_gaps():
    checker, records, registry, discovered = current_contract()
    result = checker.validate_registry(registry, discovered, records)
    assert result.errors == []
    rows = by_path(registry)

    for path in (
        "scripts/cron/setup-cron.sh",
        "scripts/setup/new-machine-setup.sh",
        "scripts/cron/harness-update.sh",
    ):
        row = rows[path]
        assert set(row) <= {"path", "kind", "delegation", "disposition_group"}
        delegation = row["delegation"]
        assert set(delegation) == {"immediate_callee", "terminal", "modes"}
        assert delegation["terminal"] == {
            "path": "scripts/cron/cron_apply.py",
            "operation": "reconcile-current-user-crontab",
        }
        assert delegation["modes"]
        for mode in delegation["modes"]:
            assert set(mode) == {
                "id", "mutation_mode", "args", "target", "exit", "source_attestation"
            }

    assert result.statuses["scripts/cron/setup-cron.sh"] == "compliant"
    assert result.statuses["scripts/setup/new-machine-setup.sh"] == "compliant"
    assert result.statuses["scripts/cron/harness-update.sh"] == "migration-required"
    new_modes = rows["scripts/setup/new-machine-setup.sh"]["delegation"]["modes"]
    assert any(mode["exit"] == "swallow-3490" for mode in new_modes)
    harness_modes = rows["scripts/cron/harness-update.sh"]["delegation"]["modes"]
    assert any(mode["exit"] == "swallow-3479" for mode in harness_modes)


def test_delegation_validation_fails_closed_for_broken_graphs():
    checker, records, registry, discovered = current_contract()

    cases = []
    cycle = copy.deepcopy(registry)
    by_path(cycle)["scripts/cron/setup-cron.sh"]["delegation"]["immediate_callee"] = (
        "scripts/setup/new-machine-setup.sh"
    )
    cases.append((cycle, "cycle"))

    missing = copy.deepcopy(registry)
    by_path(missing)["scripts/cron/setup-cron.sh"]["delegation"]["terminal"]["path"] = (
        "scripts/cron/missing.py"
    )
    cases.append((missing, "terminal"))

    wrong_operation = copy.deepcopy(registry)
    by_path(wrong_operation)["scripts/cron/setup-cron.sh"]["delegation"]["terminal"][
        "operation"
    ] = "not-an-operation"
    cases.append((wrong_operation, "operation"))

    wrong_edge = copy.deepcopy(registry)
    by_path(wrong_edge)["scripts/cron/setup-cron.sh"]["delegation"]["immediate_callee"] = (
        "scripts/cron/harness-update.sh"
    )
    cases.append((wrong_edge, "immediate callee"))

    for candidate, expected in cases:
        result = checker.validate_registry(candidate, discovered, records)
        assert any(expected in error.lower() for error in result.errors), result.errors


def test_direct_primitive_wrapper_cannot_inherit_terminal_compliance():
    checker, records, registry, _ = current_contract()
    records[b"scripts/cron/setup-cron.sh"] += b"\nprintf x | crontab -\n"
    discovered = checker.discover_mutation_surfaces(records)
    result = checker.validate_registry(registry, discovered, records)
    assert any("direct primitive" in error.lower() for error in result.errors)


def test_state_classes_inventory_and_workflow_are_fail_closed():
    checker, records, registry, discovered = current_contract()
    workflow = records[b".github/workflows/enforcement-gate.yml"].decode()
    assert "build-cron-identity-inventory.py --check" in workflow
    inventory_line = next(
        line for line in workflow.splitlines() if "build-cron-identity-inventory.py --check" in line
    )
    assert "|| true" not in inventory_line

    stale = copy.deepcopy(records)
    stale[b"docs/reports/issue-3475-command-identity-inventory.json"] += b" "
    result = checker.validate_registry(registry, discovered, stale)
    assert any("identity inventory" in error.lower() for error in result.errors)

    invalid = copy.deepcopy(records)
    invalid[b"config/workstations/harness-state-classes.yaml"] = (
        b"preserved_external: not-a-list\npreserved_local: []\n"
    )
    result = checker.validate_registry(registry, discovered, invalid)
    assert any("state class" in error.lower() for error in result.errors)


def test_renderer_supports_delegate_rows_and_preserves_migration_issues():
    checker, records, registry, discovered = current_contract()
    result = checker.validate_registry(registry, discovered, records)
    assert result.errors == []
    rendered = checker.render_html(registry, discovered, result, "a" * 64).decode()
    assert "canonical-exact-line" in rendered
    assert "legacy-exact-line" in rendered
    assert "swallow-3490" in rendered
    assert "swallow-3479" in rendered
    for issue in (3476, 3477, 3478, 3479):
        assert f"#{issue}" in rendered
    assert "active disposition: #3475" not in rendered


EXPECTED_MODES = {
    "scripts/cron/setup-cron.sh": [
        {"id": "default-apply", "mutation_mode": "destructive", "args": ["--machine=<canonical>", "--apply"], "target": "physical-local", "exit": "propagate", "source_attestation": "setup-default-apply-v1"},
        {"id": "dry-run", "mutation_mode": "non-mutating", "args": ["--machine=<canonical>", "--json"], "target": "physical-local", "exit": "propagate", "source_attestation": "setup-dry-run-v1"},
        {"id": "live-reload", "mutation_mode": "destructive", "args": ["--machine=<canonical>", "--apply", "--allow-live-reload"], "target": "physical-local", "exit": "propagate", "source_attestation": "setup-live-reload-v1"},
        {"id": "remote-rejection", "mutation_mode": "non-mutating", "args": ["--machine=<remote>"], "target": "physical-local", "exit": "reject", "source_attestation": "setup-remote-reject-v1"},
        {"id": "windows-skip", "mutation_mode": "non-mutating", "args": ["--machine=<windows>"], "target": "platform-selected", "exit": "skip", "source_attestation": "setup-windows-skip-v1"},
    ],
    "scripts/setup/new-machine-setup.sh": [
        {"id": "default-linux", "mutation_mode": "destructive", "args": ["setup-cron"], "target": "physical-local", "exit": "propagate", "source_attestation": "new-machine-default-v1"},
        {"id": "dry-run-preview", "mutation_mode": "non-mutating", "args": ["setup-cron", "--dry-run"], "target": "physical-local", "exit": "swallow-3490", "source_attestation": "new-machine-dry-run-v1"},
        {"id": "windows-skip", "mutation_mode": "non-mutating", "args": ["setup-cron"], "target": "platform-selected", "exit": "swallow-3490", "source_attestation": "new-machine-windows-v1"},
    ],
    "scripts/cron/harness-update.sh": [
        {"id": "scheduled-sync", "mutation_mode": "destructive", "args": ["setup-cron"], "target": "physical-local", "exit": "swallow-3479", "source_attestation": "harness-default-v1"},
        {"id": "dry-run-sync", "mutation_mode": "non-mutating", "args": ["setup-cron", "--dry-run"], "target": "physical-local", "exit": "swallow-3479", "source_attestation": "harness-dry-run-v1"},
    ],
}


def test_wrapper_mode_contracts_are_exact_and_source_bound():
    checker, records, registry, discovered = current_contract()
    rows = by_path(registry)
    for path, expected in EXPECTED_MODES.items():
        assert rows[path]["delegation"]["modes"] == expected
        removed = copy.deepcopy(registry)
        by_path(removed)[path]["delegation"]["modes"].pop()
        result = checker.validate_registry(removed, discovered, records)
        assert result.errors or result.statuses[path] != "compliant"
        for field in ("id", "mutation_mode", "args", "target", "exit", "source_attestation"):
            changed = copy.deepcopy(registry)
            mode = by_path(changed)[path]["delegation"]["modes"][0]
            mode[field] = ["wrong"] if field == "args" else f"wrong-{field}"
            result = checker.validate_registry(changed, discovered, records)
            assert result.errors or result.statuses[path] != "compliant", (path, field)


def test_preservation_attestation_proves_plan_reconstruction():
    checker, records, _registry, _discovered = current_contract()
    name = "python-postwrite-preservation-multiset-v1"
    source = checker.attestation_source(name)
    assert source == b"scripts/cron/cron_transaction.py"
    assert checker.evaluate_attestation(name, records, source)
    body = records[source]
    mutations = (
            body.replace(b'if line_class in ("ignore", "preserved_external"):\n            preserved.append(line)', b'if line_class in ("ignore", "preserved_external"):\n            continue', 1),
            body.replace(b'elif line_class != "cataloged":\n            uncataloged.append(line)', b'elif line_class != "cataloged":\n            continue', 1),
            body.replace(
                b'before = [line for line in parsed["before"] if classify(line) != "cataloged"]',
                b'before = []',
                1,
            ),
            body.replace(b'return before + block + after', b'return block', 1),
    )
    for mutated in mutations:
        changed = copy.deepcopy(records)
        changed[source] = mutated
        assert mutated != body
        assert not checker.evaluate_attestation(name, changed, source)


def test_enforcement_modules_obey_size_limits_and_extract_responsibilities():
    required = {
        "scripts/enforcement/scheduler_mutation_report.py",
        "scripts/enforcement/scheduler_mutation_delegation.py",
    }
    for relative in required:
        assert (ROOT / relative).is_file()
    production = list((ROOT / "scripts/enforcement").glob("scheduler_mutation*.py"))
    production.append(CHECKER)
    for path in set(production):
        assert len(path.read_text().splitlines()) <= 400, path
        tree = ast.parse(path.read_text())
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                assert node.end_lineno - node.lineno + 1 <= 50, (path, node.name)
    checker = load_checker()
    assert checker.render_html.__module__ == "scheduler_mutation_report"


def test_3490_gap_is_linked_in_render_and_docs():
    checker, records, registry, discovered = current_contract()
    result = checker.validate_registry(registry, discovered, records)
    rendered = checker.render_html(registry, discovered, result, "f" * 64).decode()
    url = "https://github.com/vamseeachanta/workspace-hub/issues/3490"
    assert f'href="{url}"' in rendered
    assert f"[#3490]({url})" in records[b"docs/ops/scheduled-tasks.md"].decode()


@pytest.mark.parametrize(
    ("attestation", "old", "new"),
    [
        ("setup-default-apply-v1", b'APPLY_ARGS=(--machine "$CANONICAL_MACHINE")', b'APPLY_ARGS=(--machine wrong)'),
        ("setup-default-apply-v1", b'"${APPLY_ARGS[@]}"', b'--machine "$CANONICAL_MACHINE"'),
        ("setup-default-apply-v1", b'if [[ "$DRY_RUN" == false ]]', b'if [[ "$DRY_RUN" == true ]]'),
        ("setup-dry-run-v1", b'APPLY_ARGS+=(--json)', b'APPLY_ARGS+=(--apply)'),
        ("setup-live-reload-v1", b'if [[ "$ALLOW_LIVE_RELOAD" == true ]]', b'if [[ "$ALLOW_LIVE_RELOAD" == false ]]'),
        ("setup-live-reload-v1", b'APPLY_ARGS+=(--allow-live-reload)', b'APPLY_ARGS+=(--json)'),
        ("setup-remote-reject-v1", b'if [[ "$CANONICAL_MACHINE" != "$PHYSICAL_MACHINE" ]]', b'if [[ "$CANONICAL_MACHINE" == "$PHYSICAL_MACHINE" ]]'),
        ("setup-remote-reject-v1", b'echo "Run setup-cron.sh on that machine instead." >&2\n  exit 2', b'echo "Run setup-cron.sh on that machine instead." >&2\n  exit 0'),
        ("setup-windows-skip-v1", b'--machine "$TARGET_MACHINE" --field os)', b'--machine "$TARGET_MACHINE" --field schedule_variant)'),
        ("setup-windows-skip-v1", b'if [[ "$MACHINE_OS" == "windows" ]]', b'if [[ "$MACHINE_OS" != "windows" ]]'),
        ("setup-windows-skip-v1", b'echo "This machine uses Windows Task Scheduler; Linux cron reconciliation is skipped."\n  exit 0', b'echo "This machine uses Windows Task Scheduler; Linux cron reconciliation is skipped."\n  exit 2'),
        ("new-machine-default-v1", b'bash "${WORKSPACE_HUB}/scripts/cron/setup-cron.sh"\nfi', b'bash "${WORKSPACE_HUB}/scripts/cron/setup-cron.sh" || true\nfi'),
        ("new-machine-dry-run-v1", b'setup-cron.sh" --dry-run || true', b'setup-cron.sh" || true'),
        ("new-machine-dry-run-v1", b'setup-cron.sh" --dry-run || true', b'setup-cron.sh" --dry-run'),
        ("new-machine-windows-v1", b'setup-cron.sh" || true\nelse', b'setup-cron.sh" --dry-run || true\nelse'),
        ("new-machine-windows-v1", b'setup-cron.sh" || true\nelse', b'setup-cron.sh"\nelse'),
        ("harness-default-v1", b'out=$(bash "$installer" 2>&1) || true', b'out=$(bash "$installer" --dry-run 2>&1) || true'),
        ("harness-default-v1", b'out=$(bash "$installer" 2>&1) || true', b'out=$(bash "$installer" 2>&1)'),
        ("harness-dry-run-v1", b'bash "$installer" --dry-run 2>/dev/null', b'bash "$installer" 2>/dev/null'),
        ("harness-dry-run-v1", b"| grep -cE '^[[:space:]]+[0-9*]' || true", b"| grep -cE '^[[:space:]]+[0-9*]'"),
    ],
)
def test_wrapper_attestations_reject_live_source_mutations(attestation, old, new):
    checker, records, _registry, _discovered = current_contract()
    wrapper_module = sys.modules["scheduler_mutation_wrapper_attestations"]
    source = checker.attestation_source(attestation)
    body = records[source]
    mutated = body.replace(old, new, 1)
    assert mutated != body, (attestation, old)
    records[source] = mutated
    original_pin = wrapper_module.WRAPPER_SHA256[source]
    wrapper_module.WRAPPER_SHA256[source] = hashlib.sha256(mutated).hexdigest()
    try:
        assert wrapper_module._pinned(source, records)
        assert not checker.evaluate_attestation(attestation, records, source)
    finally:
        records[source] = body
        wrapper_module.WRAPPER_SHA256[source] = original_pin


def _evaluate_self_pinned_setup(body, attestation="setup-windows-skip-v1"):
    checker, records, _registry, _discovered = current_contract()
    wrapper_module = sys.modules["scheduler_mutation_wrapper_attestations"]
    source = checker.attestation_source(attestation)
    original_body = records[source]
    original_pin = wrapper_module.WRAPPER_SHA256[source]
    records[source] = body
    wrapper_module.WRAPPER_SHA256[source] = hashlib.sha256(body).hexdigest()
    try:
        assert wrapper_module._pinned(source, records)
        return checker.evaluate_attestation(attestation, records, source)
    finally:
        records[source] = original_body
        wrapper_module.WRAPPER_SHA256[source] = original_pin


def test_setup_self_pinned_baseline_accepts_registry_os_gate():
    checker, records, _registry, _discovered = current_contract()
    wrapper_module = sys.modules["scheduler_mutation_wrapper_attestations"]
    source = checker.attestation_source("setup-windows-skip-v1")
    original_pin = wrapper_module.WRAPPER_SHA256[source]
    wrapper_module.WRAPPER_SHA256[source] = hashlib.sha256(records[source]).hexdigest()
    try:
        assert all(checker.evaluate_attestation(name, records, source)
                   for name in sorted(wrapper_module.SETUP_ATTESTATIONS))
    finally:
        wrapper_module.WRAPPER_SHA256[source] = original_pin


SETUP_WINDOWS_BLOCK = b'''MACHINE_OS="$(uv run --no-project python "$CRON_RENDER" \\
  --machine "$TARGET_MACHINE" --field os)"
if [[ "$MACHINE_OS" == "windows" ]]; then
  echo "This machine uses Windows Task Scheduler; Linux cron reconciliation is skipped."
  exit 0
fi'''
SETUP_REMOTE_BLOCK = b'''if [[ "$CANONICAL_MACHINE" != "$PHYSICAL_MACHINE" ]]; then
  echo "ERROR: refusing to reconcile local crontab for remote machine ${CANONICAL_MACHINE}" >&2
  echo "Run setup-cron.sh on that machine instead." >&2
  exit 2
fi'''


@pytest.mark.parametrize(
    ("old", "new"),
    [
        (b'MACHINE_OS="$(uv run', b'OTHER_OS="$(uv run'),
        (b'if [[ "$MACHINE_OS" == "windows" ]]', b'if [[ -n "$MACHINE_OS" ]]'),
        (b'  exit 0\nfi\nif [[ "$CANONICAL_MACHINE"', b'  exit 2\nfi\nif [[ "$CANONICAL_MACHINE"'),
        (b'if [[ "$CANONICAL_MACHINE" != "$PHYSICAL_MACHINE" ]]', b'if [[ "$CANONICAL_MACHINE" == "$PHYSICAL_MACHINE" ]]'),
        (b'  --machine "$TARGET_MACHINE" --field os)"\nif [[', b'  --machine "$TARGET_MACHINE" --field os)"\nMACHINE_OS="linux"\nif [['),
        (b'MACHINE_OS="$(uv run', b'if false; then\nMACHINE_OS="$(uv run'),
        (b'MACHINE_OS="$(uv run', b'if true; then\n  exit 0\nfi\nMACHINE_OS="$(uv run'),
        (b'exec uv run --script "$CRON_APPLY" "${APPLY_ARGS[@]}"', b'if [[ "$DRY_RUN" == impossible ]]; then\n  exec uv run --script "$CRON_APPLY" "${APPLY_ARGS[@]}"\nfi'),
        (SETUP_REMOTE_BLOCK, b'PHYSICAL_MACHINE="$CANONICAL_MACHINE"\n' + SETUP_REMOTE_BLOCK),
        (b'APPLY_ARGS=(--machine "$CANONICAL_MACHINE")', b'DRY_RUN=false\nAPPLY_ARGS=(--machine "$CANONICAL_MACHINE")'),
        (b'if [[ "$ALLOW_LIVE_RELOAD" == true ]]', b'ALLOW_LIVE_RELOAD=true\nif [[ "$ALLOW_LIVE_RELOAD" == true ]]'),
        (b'exec uv run --script "$CRON_APPLY"', b'APPLY_ARGS+=(--apply)\nexec uv run --script "$CRON_APPLY"'),
        (b'CANONICAL_MACHINE="$(uv run', b'export DRY_RUN=true\nCANONICAL_MACHINE="$(uv run'),
        (b'CANONICAL_MACHINE="$(uv run', b'if true; then exit 0; fi\nCANONICAL_MACHINE="$(uv run'),
        (b'CANONICAL_MACHINE="$(uv run', b'builtin exit 0\nCANONICAL_MACHINE="$(uv run'),
        (b'CANONICAL_MACHINE="$(uv run', b": <<'fi'\nCANONICAL_MACHINE=\"$(uv run"),
    ],
)
def test_setup_attestation_rejects_self_pinned_semantic_bypasses(old, new):
    checker, records, _registry, _discovered = current_contract()
    source = checker.attestation_source("setup-windows-skip-v1")
    mutated = records[source].replace(old, new, 1)
    assert mutated != records[source], old
    assert not _evaluate_self_pinned_setup(mutated)


@pytest.mark.parametrize(
    ("block", "prefix", "suffix"),
    [
        (SETUP_WINDOWS_BLOCK, b" exit 0\n", b""),
        (SETUP_WINDOWS_BLOCK, b"while false; do\n", b"\ndone"),
        (SETUP_WINDOWS_BLOCK, b"scheduler_decoy() {\n", b"\n}"),
        (SETUP_WINDOWS_BLOCK, b"(\n", b"\n)"),
        (SETUP_WINDOWS_BLOCK, b": <<'BODY'\n", b"\nBODY"),
        (SETUP_WINDOWS_BLOCK, b" exit 0 # bypass\n", b""),
        (SETUP_WINDOWS_BLOCK, b"if true; then exit 0; fi\n", b""),
        (SETUP_WINDOWS_BLOCK, b"builtin exit 0\n", b""),
        (SETUP_WINDOWS_BLOCK, b": <<'fi'\n", b""),
        (SETUP_REMOTE_BLOCK, b"if false; then\n", b"\nfi"),
    ],
)
def test_setup_attestation_rejects_self_pinned_control_scope_bypasses(
    block, prefix, suffix,
):
    checker, records, _registry, _discovered = current_contract()
    source = checker.attestation_source("setup-windows-skip-v1")
    mutated = records[source].replace(block, prefix + block + suffix, 1)
    assert mutated != records[source], block
    assert not _evaluate_self_pinned_setup(mutated)


WRAPPER_MUTATIONS = {
    b"scripts/cron/setup-cron.sh": (
        "setup-default-apply-v1",
        b'if [[ "$DRY_RUN" == false ]]',
        b'if [[ "$DRY_RUN" == true ]]',
    ),
    b"scripts/setup/new-machine-setup.sh": (
        "new-machine-default-v1",
        b'bash "${WORKSPACE_HUB}/scripts/cron/setup-cron.sh"\nfi',
        b'bash "${WORKSPACE_HUB}/scripts/cron/setup-cron.sh" || true\nfi',
    ),
    b"scripts/cron/harness-update.sh": (
        "harness-default-v1",
        b'out=$(bash "$installer" 2>&1) || true',
        b'out=$(bash "$installer" 2>&1)',
    ),
}


def _decoy(kind, original):
    if kind == "comment":
        return b"\n" + b"\n".join(b"# " + line for line in original.splitlines())
    if kind == "heredoc":
        return b"\n: <<'SCHEDULER_DECOY'\n" + original + b"\nSCHEDULER_DECOY\n"
    if kind == "dead-function":
        return b"\nscheduler_decoy() {\n: <<'BODY'\n" + original + b"\nBODY\n}\n"
    return b"\nif false; then\n: <<'BODY'\n" + original + b"\nBODY\nfi\n"


@pytest.mark.parametrize("source", sorted(WRAPPER_MUTATIONS))
@pytest.mark.parametrize("decoy", ["comment", "heredoc", "dead-function", "if-false"])
def test_wrapper_attestations_reject_dead_scope_and_fragment_decoys(source, decoy):
    checker, records, _registry, _discovered = current_contract()
    attestation, old, new = WRAPPER_MUTATIONS[source]
    original = records[source]
    mutated = original.replace(old, new, 1) + _decoy(decoy, original)
    assert mutated != original
    records[source] = mutated
    assert not checker.evaluate_attestation(attestation, records, source)


def test_wrapper_digest_pins_are_exact_complete_and_fail_closed():
    checker, records, _registry, _discovered = current_contract()
    wrapper_module = sys.modules["scheduler_mutation_wrapper_attestations"]
    assert set(wrapper_module.WRAPPER_SHA256) == set(WRAPPER_MUTATIONS)
    assert wrapper_module.WRAPPER_SHA256[wrapper_module.SETUP] == (
        "1a5e5573d00d17c4a820a831549fb92a2dad100b5fbab5572afcefadd57c84c1"
    )
    for source, (attestation, _old, _new) in WRAPPER_MUTATIONS.items():
        original = wrapper_module.WRAPPER_SHA256[source]
        try:
            assert original == hashlib.sha256(records[source]).hexdigest()
            wrapper_module.WRAPPER_SHA256[source] = "0" * 64
            assert not checker.evaluate_attestation(attestation, records, source)
            del wrapper_module.WRAPPER_SHA256[source]
            assert not checker.evaluate_attestation(attestation, records, source)
        finally:
            wrapper_module.WRAPPER_SHA256[source] = original


def test_setup_wrapper_pin_matches_exact_staged_blob():
    checker, records, _registry, _discovered = current_contract()
    wrapper_module = sys.modules["scheduler_mutation_wrapper_attestations"]
    source = wrapper_module.SETUP
    staged_body = records[source]
    working_body = (ROOT / source.decode()).read_bytes()
    assert staged_body == working_body
    assert wrapper_module.WRAPPER_SHA256[source] == hashlib.sha256(staged_body).hexdigest()


@pytest.mark.parametrize("source", sorted(WRAPPER_MUTATIONS))
@pytest.mark.parametrize("bypass", ["early-exit", "dead-script"])
def test_wrapper_attestations_reject_self_refreshed_reachability_bypass(source, bypass):
    checker, records, _registry, _discovered = current_contract()
    wrapper_module = sys.modules["scheduler_mutation_wrapper_attestations"]
    attestation = WRAPPER_MUTATIONS[source][0]
    original_body = records[source]
    original_pin = wrapper_module.WRAPPER_SHA256[source]
    if bypass == "early-exit":
        lines = original_body.splitlines(keepends=True)
        index = next(i for i, line in enumerate(lines) if line.strip().startswith(b"set -"))
        lines.insert(index + 1, b"exit 0\n")
        mutated = b"".join(lines)
    else:
        nested = b"\n".join(b"  " + line for line in original_body.splitlines())
        mutated = b"if false; then\n" + nested + b"\nfi\nexit 0\n"
    records[source] = mutated
    wrapper_module.WRAPPER_SHA256[source] = hashlib.sha256(mutated).hexdigest()
    try:
        assert not checker.evaluate_attestation(attestation, records, source)
    finally:
        wrapper_module.WRAPPER_SHA256[source] = original_pin


def _dead_transaction_source(records, mutation):
    tree = ast.parse(records[b"scripts/cron/cron_apply.py"])
    functions = {node.name: node for node in tree.body if isinstance(node, ast.FunctionDef)}
    if mutation in {"run-lock", "run-helper", "run-return"}:
        run = functions["run_cutover"]
        lock = next(node for node in run.body if isinstance(node, ast.With))
        index = run.body.index(lock)
        if mutation == "run-return":
            run.body.insert(index, ast.parse("return {'status': 'applied'}").body[0])
        elif mutation == "run-lock":
            run.body[index] = ast.If(test=ast.Constant(False), body=[lock], orelse=[])
        else:
            run.body[index] = ast.FunctionDef(
                name="never_called", args=ast.arguments(posonlyargs=[], args=[],
                kwonlyargs=[], kw_defaults=[], defaults=[]), body=[lock],
                decorator_list=[]
            )
        if mutation != "run-return":
            run.body.insert(index + 1, ast.parse(
                "observation = _write_observation(plan['new_text'], _read, _write)"
            ).body[0])
    elif mutation in {"finish-exact", "finish-return"}:
        finish = functions["_finish_exact"]
        guarded = next(node for node in finish.body if isinstance(node, ast.If)
                       and "observed == B" in ast.unparse(node.test))
        index = finish.body.index(guarded)
        if mutation == "finish-return":
            finish.body.insert(index, ast.parse(
                "return _transaction_result('applied', backup, expected=B)"
            ).body[0])
        else:
            finish.body[index] = ast.If(test=ast.Constant(False), body=[guarded], orelse=[])
            finish.body.insert(index + 1, ast.parse(
                "return _transaction_result('applied', backup, expected=B)"
            ).body[0])
    else:
        rollback = functions["_rollback"]
        lock = next(node for node in rollback.body if isinstance(node, ast.With))
        index = rollback.body.index(lock)
        if mutation == "rollback-raise":
            rollback.body.insert(index, ast.parse("raise RuntimeError('stop')").body[0])
        else:
            rollback.body[index] = ast.If(test=ast.Constant(False), body=[lock], orelse=[])
            rollback.body.insert(index + 1, ast.parse("_write(A)").body[0])
    ast.fix_missing_locations(tree)
    return ast.unparse(tree).encode()


def _split_transaction_source(records, mutation):
    tree = ast.parse(records[b"scripts/cron/cron_apply.py"])
    functions = {node.name: node for node in tree.body if isinstance(node, ast.FunctionDef)}
    if mutation == "run-graph-split":
        run = functions["run_cutover"]
        build = next(node for node in run.body if "_build_cutover(" in ast.unparse(node))
        lock = next(node for node in run.body if isinstance(node, ast.With))
        finish = next(node for node in run.body if "_finish_exact(" in ast.unparse(node))
        index = min(run.body.index(node) for node in (build, lock, finish))
        run.body.remove(build)
        run.body.remove(lock)
        run.body.remove(finish)
        run.body.insert(index, ast.If(test=ast.Name(id="split", ctx=ast.Load()),
                                     body=[build, lock], orelse=[finish]))
    elif mutation == "finish-exact-split":
        finish = functions["_finish_exact"]
        exact = next(node for node in finish.body if isinstance(node, ast.If)
                     and "observed == B" in ast.unparse(node.test))
        index = finish.body.index(exact)
        success = exact.body[0]
        exact.body = [ast.Pass()]
        finish.body[index] = ast.If(test=ast.Name(id="split", ctx=ast.Load()),
                                    body=[exact], orelse=[success])
    else:
        rollback = functions["_rollback"]
        lock = next(node for node in rollback.body if isinstance(node, ast.With))
        current, check, write, restored = lock.body
        if mutation == "rollback-cas-split":
            lock.body = [ast.If(test=ast.Name(id="split", ctx=ast.Load()),
                                body=[current, check], orelse=[write, restored])]
        elif mutation == "rollback-try-split":
            lock.body = [ast.Try(body=[current, check], handlers=[ast.ExceptHandler(
                type=ast.Name(id="Exception", ctx=ast.Load()), name=None,
                body=[write, restored])], orelse=[], finalbody=[])]
        else:
            index = rollback.body.index(lock)
            exact = rollback.body[index + 1:]
            rollback.body[index:] = [ast.If(
                test=ast.Name(id="split", ctx=ast.Load()),
                body=[lock, ast.Return(value=ast.Dict(keys=[], values=[]))],
                orelse=exact,
            )]
    ast.fix_missing_locations(tree)
    return ast.unparse(tree).encode()


@pytest.mark.parametrize(
    ("mutation", "attestations"),
    [
        ("run-graph-split", ["python-lock-scope-v1"]),
        ("finish-exact-split", ["python-postwrite-exact-state-v1"]),
        ("rollback-cas-split", ["python-rollback-after-cas-v1",
                                "python-rollback-exact-baseline-v1"]),
        ("rollback-try-split", ["python-rollback-after-cas-v1",
                                "python-rollback-exact-baseline-v1"]),
        ("rollback-outer-split", ["python-rollback-exact-baseline-v1"]),
    ],
)
def test_transaction_attestations_reject_mutually_exclusive_evidence(
    mutation, attestations
):
    checker, records, _registry, _discovered = current_contract()
    records[b"scripts/cron/cron_apply.py"] = _split_transaction_source(records, mutation)
    for attestation in attestations:
        assert not checker.evaluate_attestation(
            attestation, records, b"scripts/cron/cron_apply.py"
        )


@pytest.mark.parametrize(
    ("mutation", "attestations"),
    [
        ("run-lock", ["python-lock-scope-v1", "python-prewrite-cas-v1",
                      "python-backup-baseline-v1"]),
        ("run-helper", ["python-lock-scope-v1", "python-prewrite-cas-v1",
                        "python-backup-baseline-v1"]),
        ("run-return", ["python-lock-scope-v1", "python-prewrite-cas-v1",
                        "python-backup-baseline-v1"]),
        ("finish-exact", ["python-postwrite-exact-state-v1"]),
        ("finish-return", ["python-postwrite-exact-state-v1"]),
        ("rollback", ["python-rollback-after-cas-v1",
                      "python-rollback-exact-baseline-v1"]),
        ("rollback-raise", ["python-rollback-after-cas-v1",
                            "python-rollback-exact-baseline-v1"]),
    ],
)
def test_transaction_attestations_reject_dead_safe_path_with_unsafe_live_path(
    mutation, attestations
):
    checker, records, _registry, _discovered = current_contract()
    records[b"scripts/cron/cron_apply.py"] = _dead_transaction_source(records, mutation)
    for attestation in attestations:
        assert not checker.evaluate_attestation(
            attestation, records, b"scripts/cron/cron_apply.py"
        )
