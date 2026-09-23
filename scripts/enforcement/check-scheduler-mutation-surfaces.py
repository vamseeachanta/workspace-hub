#!/usr/bin/env python3
"""Fail-closed, index-backed scheduler mutation inventory validator."""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

import yaml

MODULE_DIR = Path(__file__).resolve().parent
if str(MODULE_DIR) not in sys.path:
    sys.path.insert(0, str(MODULE_DIR))

from scheduler_mutation_contract import (  # noqa: E402
    ATT_SOURCES,
    Discovery,
    ValidationResult,
    attestation_source,
    derive_status,
    digest_record_union,
    input_digest,
    validate_closed_schema,
    validate_operation_contract,
)
from scheduler_mutation_discovery import (  # noqa: E402
    derive_kanban_operations,
    derive_windows_task_operations,
    has_primitive_alias_call,
)
from scheduler_mutation_attestations import (  # noqa: E402
    derive_cron_classifier_branches,
    evaluate_python,
    evaluate_shell_guard,
    evaluate_windows,
    forensic_literal_lines,
)
from scheduler_mutation_delegation import (  # noqa: E402
    validate_delegation_graph,
    validate_identity_inputs,
)
from scheduler_mutation_report import render_html  # noqa: E402
from scheduler_mutation_wrapper_attestations import (  # noqa: E402
    evaluate_wrapper_attestation,
)

ROOT = Path(__file__).resolve().parents[2]
REGISTRY = b"config/scheduled-tasks/mutation-surfaces.yaml"
CHECKER = b"scripts/enforcement/check-scheduler-mutation-surfaces.py"
TEST = b"tests/enforcement/test_scheduler_mutation_surfaces.py"
HARDENING_TEST = b"tests/enforcement/test_scheduler_mutation_hardening.py"
ATTESTATIONS = b"scripts/enforcement/scheduler_mutation_attestations.py"
DISCOVERY_HELPER = b"scripts/enforcement/scheduler_mutation_discovery.py"
WRAPPER_ATTESTATIONS = b"scripts/enforcement/scheduler_mutation_wrapper_attestations.py"
FORENSIC = {CHECKER, TEST, HARDENING_TEST, ATTESTATIONS, DISCOVERY_HELPER, WRAPPER_ATTESTATIONS}
SENTINEL = b"scheduler-mutation-forensic"
PRIMITIVE_PATTERNS = {
    "crontab-replace": (
        rb"(?:^|[|;\(\s])(?:run_)?crontab[ \t]+-(?:[ \t]|$)",  # scheduler-mutation-forensic
        rb"\[[ \t]*['\"]crontab['\"][ \t]*,[ \t]*['\"]-['\"]",  # scheduler-mutation-forensic
        rb"['\"]crontab[ \t]+-['\"]",  # scheduler-mutation-forensic
    ),  # scheduler-mutation-forensic
    "systemd-user-unit-write": (
        rb"\b(?:write_unit|remove_unit)[ \t]+",  # scheduler-mutation-forensic
        rb"(?:cat|printf)[^\n]*(?:\.config/systemd/user|SYSTEMD_USER_DIR)",  # scheduler-mutation-forensic
    ),  # scheduler-mutation-forensic
    "systemd-user-enable-disable": (
        rb"\b(?:run_systemctl|systemctl[ \t]+--user)[ \t]+(?:enable|disable)\b",  # scheduler-mutation-forensic
    ),  # scheduler-mutation-forensic
    "windows-task-set": (rb"\bSet-ScheduledTask\b",),  # scheduler-mutation-forensic
    "windows-task-unregister-register": (
        rb"\b(?:Register|Unregister)-ScheduledTask\b",  # scheduler-mutation-forensic
    ),  # scheduler-mutation-forensic
}
PRIMITIVES = set(PRIMITIVE_PATTERNS)
class GitTransportError(RuntimeError):
    pass
def _s(path: bytes) -> str:
    return path.decode("utf-8", "surrogateescape")
def _code(body: bytes) -> bytes:
    return b"\n".join(line for line in body.splitlines() if not line.lstrip().startswith(b"#"))


def read_index_records(repo: Path, git_command: str = "git") -> dict[bytes, bytes]:
    listed = subprocess.run([git_command, "ls-files", "-z"], cwd=repo, capture_output=True)
    if listed.returncode:
        raise GitTransportError("git ls-files -z failed")
    paths = [path for path in listed.stdout.split(b"\0") if path]
    commands = b"".join(b"contents :" + path + b"\0" for path in paths)
    read = subprocess.run(
        [git_command, "cat-file", "--batch-command", "-Z"],
        cwd=repo, input=commands, capture_output=True,
    )
    if read.returncode:
        raise GitTransportError("Git cat-file --batch-command -Z support is required")
    records: dict[bytes, bytes] = {}
    offset = 0
    for path in paths:
        end = read.stdout.find(b"\0", offset)
        if end < 0:
            raise GitTransportError("truncated NUL header")
        parts = read.stdout[offset:end].rsplit(b" ", 2)
        offset = end + 1
        if len(parts) != 3 or parts[1] != b"blob":
            raise GitTransportError(f"missing index blob: {_s(path)}")
        size = int(parts[2])
        blob = read.stdout[offset:offset + size]
        offset += size
        if len(blob) != size or read.stdout[offset:offset + 1] != b"\0":
            raise GitTransportError("truncated NUL content")
        records[path] = blob
        offset += 1
    return records


def _known_call(raw: bytes, code: bytes) -> tuple[str, str] | None:
    if raw == b"scripts/cron/setup-cron.sh":
        shape = rb"CRON_APPLY=.*scripts/cron/cron_apply\.py[\s\S]+exec uv run --script \"\$CRON_APPLY\""
        return ("scripts/cron/cron_apply.py", "constant-path-exec") if re.search(shape, code) else None
    if raw == b"scripts/setup/new-machine-setup.sh":
        shape = rb"bash \"\$\{WORKSPACE_HUB\}/scripts/cron/setup-cron\.sh\""
        return ("scripts/cron/setup-cron.sh", "literal-bash") if re.search(shape, code) else None
    if raw == b"scripts/cron/harness-update.sh":
        shape = rb"installer=.*scripts/cron/setup-cron\.sh[\s\S]+bash \"\$installer\""
        return ("scripts/cron/setup-cron.sh", "constant-path-exec") if re.search(shape, code) else None
    literal = re.search(rb"(?m)^\s*bash\s+[^\n]*(scripts/cron/(?:setup-cron\.sh|cron_apply\.py))", code)
    if literal:
        return (_s(literal.group(1)), "literal-bash")
    return None


def discover_mutation_surfaces(records: dict[bytes, bytes]) -> Discovery:
    direct: set[str] = set()
    transitive: set[str] = set()
    primitives: dict[str, set[str]] = {}
    edges: dict[str, tuple[str, str]] = {}
    unknown: set[str] = set()
    for raw, body in records.items():
        if not raw.startswith(b"scripts/") or not raw.endswith((b".sh", b".py", b".ps1")):
            continue
        path = _s(raw)
        found: set[str] = set()
        literal_lines = forensic_literal_lines(body) if raw in FORENSIC else set()
        for line_number, line in enumerate(body.splitlines(), 1):
            forensic_literal = (
                raw in FORENSIC
                and SENTINEL in line
                and line_number in literal_lines
            )
            if line.lstrip().startswith(b"#") or forensic_literal:
                continue
            for primitive, patterns in PRIMITIVE_PATTERNS.items():
                if any(re.search(pattern, line) for pattern in patterns):
                    found.add(primitive)
        if found:
            direct.add(path)
            primitives[path] = found
        code = _code(body)
        call = _known_call(raw, code) if raw not in FORENSIC else None
        if call:
            transitive.add(path)
            edges[path] = call
        assignments = re.findall(rb"(?m)^\s*([A-Za-z_]\w*)=([^\n]*(?:setup-cron|cron_apply)[^\n]*)", code)
        for variable, _value in assignments:
            if call is None and re.search(rb"(?:bash|exec|--script)\s+\"?\$\{?" + variable + rb"\}?", code):
                unknown.add(path)
        if call is None and re.search(
            rb"(?m)^\s*\$[A-Za-z_]*(?:SCHEDUL|CRON)[A-Za-z_]*\b", code
        ):
            unknown.add(path)
        if raw not in FORENSIC and has_primitive_alias_call(code):
            unknown.add(path)
        # Variable calls are unknown only when that variable was assigned a
        # scheduler entrypoint. Ordinary shell scripts routinely execute other
        # variable-held tools and are outside this scanner's scope.
    return Discovery(direct, transitive, edges, primitives, unknown)


def evaluate_attestation(name: str, records: dict[bytes, bytes], operation_source: bytes = b"") -> bool:
    source = attestation_source(name) or operation_source
    if name.startswith("python-") or name.startswith("cron-") or name == "crontab-current-user-target-v1":
        return evaluate_python(name, records, source)
    shell_guard = evaluate_shell_guard(name, records, source)
    if shell_guard is not None:
        return shell_guard
    windows = evaluate_windows(name, records, source)
    if windows is not None:
        return windows
    wrapper = evaluate_wrapper_attestation(name, records)
    if wrapper is not None:
        return wrapper
    code = _code(records.get(source, b""))
    if name == "kanban-backend-operation-set-v1":
        return len(derive_kanban_operations(records)) == 6
    patterns = {
        "shell-exact-sentinel-v1": rb"grep -vF \"\$CRON_SENTINEL\"[\s\S]+run_crontab -",
        "crontab-root-target-v1": rb"EUID -ne 0[\s\S]+crontab -",
        "systemd-user-unit-name-v1": rb"UNIT_NAME=\"kanban-loader-sync\"",
        "systemd-user-enable-disable-v1": rb"run_systemctl enable --now[\s\S]+run_systemctl disable --now",  # scheduler-mutation-forensic
    }
    return bool(name in patterns and re.search(patterns[name], code))


def validate_registry(registry: dict[str, Any], discovery: Discovery, records: dict[bytes, bytes]) -> ValidationResult:
    errors = validate_closed_schema(registry, set(records), PRIMITIVES)
    if errors and ("surfaces" not in registry or not isinstance(registry.get("surfaces"), list)):
        return ValidationResult(errors, {})
    rows: dict[str, dict[str, Any]] = {}
    statuses: dict[str, str] = {}
    for row in registry["surfaces"]:
        _validate_surface(row, rows, statuses, discovery, records, errors)
    validate_delegation_graph(rows, statuses, errors)
    validate_identity_inputs(ROOT, registry, records, errors)
    _validate_global_sets(registry, rows, statuses, discovery, records, errors)
    return ValidationResult(errors, statuses)


def _validate_surface(row, rows, statuses, discovery, records, errors):
    path = row.get("path", "")
    if path in rows:
        errors.append(f"duplicate surface: {path}")
    rows[path] = row
    operation_ids = [operation.get("id") for operation in row.get("operations", [])]
    if len(operation_ids) != len(set(operation_ids)):
        errors.append(f"{path}: duplicate operation id")
    branches, attestations, transactions = [], [], []
    for operation in row.get("operations", []):
        operation_errors, bs, ats, txs = validate_operation_contract(
            path, operation, records, evaluate_attestation
        )
        errors.extend(operation_errors)
        branches.extend(bs)
        attestations.extend(ats)
        transactions.extend(txs)
    if row.get("kind") == "direct-owner":
        statuses[path] = derive_status(branches, attestations or [False], transactions)
        _validate_direct_primitives(path, row, discovery, errors)
    else:
        _validate_transitive(path, row, statuses, discovery, records, errors)


def _validate_direct_primitives(path, row, discovery, errors):
    declared = {operation.get("primitive") for operation in row.get("operations", [])}
    observed = set(discovery.primitives.get(path, set()))
    if "windows-task-set" in observed:
        observed.discard("windows-task-unregister-register")
    if observed != declared:
        errors.append(f"{path}: discovered/declared primitive mismatch")


def _validate_transitive(path, row, statuses, discovery, records, errors):
    edge = row.get("delegation", {})
    actual = discovery.edges.get(path)
    if actual is None or actual[0] != edge.get("immediate_callee"):
        errors.append(f"{path}: immediate callee mismatch")
    if discovery.primitives.get(path):
        errors.append(f"{path}: direct primitive wrapper cannot inherit compliance")
    results = []
    for mode in edge.get("modes", []):
        attestation = mode.get("source_attestation", "")
        passed = attestation in ATT_SOURCES and evaluate_attestation(attestation, records, path.encode())
        results.append(passed)
        if not passed:
            errors.append(f"{path}: delegation attestation failed: {attestation}")
    statuses[path] = "compliant" if results and all(results) else "migration-required"
    if row.get("disposition_group"):
        statuses[path] = "migration-required"




def _validate_global_sets(registry, rows, statuses, discovery, records, errors):
    direct = {path for path, row in rows.items() if row.get("kind") == "direct-owner"}
    transitive = {path for path, row in rows.items() if row.get("kind") == "transitive-entrypoint"}
    for path in sorted(discovery.direct ^ direct):
        errors.append(f"direct inventory mismatch: {path}")
    for path in sorted(discovery.transitive ^ transitive):
        errors.append(f"transitive inventory mismatch: {path}")
    for path in sorted(discovery.unknown_edges):
        errors.append(f"unknown scheduler indirection: {path}")
    cron = rows.get("scripts/cron/cron_apply.py", {})
    declared = {branch["id"] for operation in cron.get("operations", []) for branch in operation.get("authority_branches", [])}
    if derive_cron_classifier_branches(records) != declared:
        errors.append("cron destructive classifier branch set mismatch")
    kanban = rows.get("scripts/install/setup-kanban-loader-timer.sh", {})
    if derive_kanban_operations(records) != {operation["id"] for operation in kanban.get("operations", [])}:
        errors.append("kanban backend operation set mismatch")
    windows = rows.get("scripts/windows/setup-scheduler-tasks.ps1", {})
    declared_windows = {operation["id"] for operation in windows.get("operations", [])}
    if derive_windows_task_operations(records) != declared_windows:
        errors.append("Windows operation set mismatch")
    migration = {path for path, status in statuses.items() if status == "migration-required"}
    covered: set[str] = set()
    group_ids: set[str] = set()
    for group in registry.get("disposition_groups", []):
        group_id = group.get("group_id")
        if group_id in group_ids:
            errors.append(f"{group_id}: duplicate disposition group")
        group_ids.add(group_id)
        members = set(group.get("members", []))
        if covered & members:
            errors.append(f"{group.get('group_id')}: duplicate disposition member")
        covered |= members
        for member in members:
            if rows.get(member, {}).get("disposition_group") != group_id:
                errors.append(f"{member}: disposition row/group mismatch")
            if statuses.get(member) == "compliant":
                errors.append(f"{member}: compliant surface cannot have active disposition")
    for path, row in rows.items():
        if row.get("disposition_group") and statuses.get(path) == "compliant":
            errors.append(f"{path}: compliant surface cannot have active disposition")
    if covered != migration:
        errors.append("dispositions must exactly cover migration-required surfaces")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("--render-html", type=Path)
    modes.add_argument("--check-html", type=Path)
    args = parser.parse_args(argv)
    try:
        records = read_index_records(ROOT)
        raw = records[REGISTRY]
        registry = yaml.safe_load(raw)
        if not isinstance(registry, dict):
            raise ValueError("registry root must be a mapping")
        discovery = discover_mutation_surfaces(records)
        result = validate_registry(registry, discovery, records)
        digest = input_digest(raw, digest_record_union(registry, records))
    except (GitTransportError, KeyError, ValueError, yaml.YAMLError) as exc:
        discovery = Discovery(set(), set(), {}, {}, set())
        result = ValidationResult([str(exc)], {})
        digest = ""
    rendered = b""
    if not result.errors and (args.render_html or args.check_html):
        rendered = render_html(registry, discovery, result, digest)
    if args.render_html and not result.errors:
        args.render_html.parent.mkdir(parents=True, exist_ok=True)
        args.render_html.write_bytes(rendered)
    if args.check_html and not result.errors:
        if not args.check_html.is_file() or args.check_html.read_bytes() != rendered:
            result.errors.append(f"HTML audit is stale: {args.check_html}")
    payload = {
        "direct": sorted(discovery.direct),
        "errors": result.errors,
        "input_digest": digest,
        "status": "ok" if not result.errors else "error",
        "transitive": sorted(discovery.transitive),
    }
    if args.json:
        print(json.dumps(payload, sort_keys=True))
    else:
        for error in result.errors:
            print(f"ERROR: {error}", file=sys.stderr)
    return 1 if result.errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
