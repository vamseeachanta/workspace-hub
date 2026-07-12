#!/usr/bin/env python3
"""Fail-closed, index-backed scheduler mutation inventory validator."""
from __future__ import annotations

import argparse
import html
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
from scheduler_mutation_attestations import (  # noqa: E402
    derive_cron_classifier_branches,
    derive_installed_fingerprint_branches,
    evaluate_python,
    evaluate_shell_guard,
    evaluate_windows,
    forensic_literal_lines,
)

ROOT = Path(__file__).resolve().parents[2]
REGISTRY = b"config/scheduled-tasks/mutation-surfaces.yaml"
CHECKER = b"scripts/enforcement/check-scheduler-mutation-surfaces.py"
TEST = b"tests/enforcement/test_scheduler_mutation_surfaces.py"
HARDENING_TEST = b"tests/enforcement/test_scheduler_mutation_hardening.py"
ATTESTATIONS = b"scripts/enforcement/scheduler_mutation_attestations.py"
FORENSIC = {CHECKER, TEST, HARDENING_TEST, ATTESTATIONS}
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
        # Variable calls are unknown only when that variable was assigned a
        # scheduler entrypoint. Ordinary shell scripts routinely execute other
        # variable-held tools and are outside this scanner's scope.
    return Discovery(direct, transitive, edges, primitives, unknown)


def derive_kanban_operations(records: dict[bytes, bytes]) -> set[str]:
    code = _code(records.get(b"scripts/install/setup-kanban-loader-timer.sh", b""))
    checks = {
        "install:systemd-unit-write": rb"do_install\(\)[\s\S]+service_body \| write_unit",
        "install:systemd-enable": rb"do_install\(\)[\s\S]+run_systemctl enable --now",  # scheduler-mutation-forensic
        "install:crontab-replace": rb"do_install\(\)[\s\S]+run_crontab -",
        "uninstall:systemd-unit-remove": rb"do_uninstall\(\)[\s\S]+remove_unit \"\$SERVICE_PATH\"",  # scheduler-mutation-forensic
        "uninstall:systemd-disable": rb"do_uninstall\(\)[\s\S]+run_systemctl disable --now",  # scheduler-mutation-forensic
        "uninstall:crontab-replace": rb"do_uninstall\(\)[\s\S]+run_crontab -",
    }
    return {name for name, pattern in checks.items() if re.search(pattern, code)}


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
        path = row.get("path", "")
        if path in rows:
            errors.append(f"duplicate surface: {path}")
        rows[path] = row
        operation_ids = [operation.get("id") for operation in row.get("operations", [])]
        if len(operation_ids) != len(set(operation_ids)):
            errors.append(f"{path}: duplicate operation id")
        branches: list[dict[str, Any]] = []
        attestations: list[bool] = []
        transactions: list[bool] = []
        for operation in row.get("operations", []):
            operation_errors, bs, ats, txs = validate_operation_contract(
                path, operation, records, evaluate_attestation
            )
            errors += operation_errors
            branches += bs
            attestations += ats
            transactions += txs
        statuses[path] = derive_status(branches, attestations or [False], transactions)
        declared_primitives = {operation.get("primitive") for operation in row.get("operations", [])}
        observed = set(discovery.primitives.get(path, set()))
        # windows-task-set is the closed update-or-register primitive.
        if "windows-task-set" in observed:
            observed.discard("windows-task-unregister-register")
        if row.get("kind") == "direct-owner" and observed != declared_primitives:
            errors.append(f"{path}: discovered/declared primitive mismatch")
        if row.get("kind") == "transitive-entrypoint":
            edge = row.get("edge", {})
            actual = discovery.edges.get(path)
            if actual != (edge.get("callee"), edge.get("call_form")):
                errors.append(f"{path}: call form/callee mismatch")
            guard = edge.get("target_guard_attestation", "")
            if guard not in ATT_SOURCES or not evaluate_attestation(guard, records, path.encode()):
                errors.append(f"{path}: wrapper-local target_guard attestation failed")
    _validate_global_sets(registry, rows, statuses, discovery, records, errors)
    return ValidationResult(errors, statuses)


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
    fingerprint_branches = {
        branch for branch in declared if branch.startswith("installed-fingerprint-")
    }
    if derive_installed_fingerprint_branches(records) != fingerprint_branches:
        errors.append("installed fingerprint mechanism set mismatch")
    kanban = rows.get("scripts/install/setup-kanban-loader-timer.sh", {})
    if derive_kanban_operations(records) != {operation["id"] for operation in kanban.get("operations", [])}:
        errors.append("kanban backend operation set mismatch")
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
    if covered != migration:
        errors.append("dispositions must exactly cover migration-required surfaces")


def _render_operation(path: str, operation: dict[str, Any]) -> str:
    key = html.escape(f'{path}::{operation["id"]}', quote=True)
    target = html.escape(operation["target_kind"], quote=True)
    identity = html.escape(operation["scheduler_identity"], quote=True)
    binding = html.escape(operation["execution_host_binding"], quote=True)
    authorities = []
    for branch in operation["authority_branches"]:
        branch_id = branch["id"]
        mechanism = html.escape(branch["mechanism"], quote=True)
        strength = html.escape(branch["strength"], quote=True)
        authority_key = html.escape(f"{key}::{branch_id}", quote=True)
        label = html.escape(f"{branch_id}:{branch['mechanism']}/{branch['strength']}")
        authorities.append(
            f'<li data-authority="{authority_key}" data-mechanism="{mechanism}" '
            f'data-strength="{strength}">{label}</li>'
        )
    gaps = [name for name, value in operation["transaction"].items() if not value]
    gap_text = ", ".join(f"{name}=false" for name in gaps) or "none"
    return (
        f'<section class="operation" data-operation="{key}" data-target-kind="{target}" '
        f'data-scheduler-identity="{identity}" data-execution-host-binding="{binding}">'
        f'<strong>{html.escape(operation["id"])}</strong><br>Target: {target}; '
        f'identity: {identity}; binding: {binding}<br>Authority:<ul>{"".join(authorities)}</ul>'
        f'Transaction gaps: <span class="transaction-gaps" '
        f'data-transaction-for="{key}">{gap_text}</span></section>'
    )


def render_html(registry, discovery, validation, digest: str) -> bytes:
    groups = {group["group_id"]: group for group in registry["disposition_groups"]}
    rows = []
    for surface in sorted(registry["surfaces"], key=lambda row: row["path"]):
        group = groups[surface["disposition_group"]]
        issue = group["issue"]["number"]
        operations = "".join(
            _render_operation(surface["path"], operation)
            for operation in surface["operations"]
        )
        path = html.escape(surface["path"], quote=True)
        rows.append(
            f'<tr data-surface="{path}"><td><code>{path}</code></td>'
            f'<td>{html.escape(surface["kind"])}</td>'
            f'<td>{html.escape(validation.statuses[surface["path"]])}</td>'
            f'<td>{operations}</td><td>'
            f'<a href="https://github.com/vamseeachanta/workspace-hub/issues/{issue}">#{issue}</a>'
            f'</td></tr>'
        )
    body = "\n".join(rows)
    document = f"""<!doctype html>
<html lang="en" data-input-digest="{digest}"><head><meta charset="utf-8">
<title>Scheduler Mutation Safety Audit</title>
<style>body{{font:16px system-ui;max-width:1200px;margin:2rem auto;padding:0 1rem}}table{{border-collapse:collapse;width:100%}}th,td{{border:1px solid #bbb;padding:.5rem;text-align:left}}code{{font-size:.9em}}.warning{{border-left:4px solid #b45309;padding:1rem;background:#fff7ed}}</style></head>
<body><h1>Scheduler Mutation Safety Audit</h1>
<p><strong>Input digest:</strong> <code>{digest}</code></p>
<p class="warning">Registry inclusion does not authorize live scheduler mutation.</p>
<table><thead><tr><th>Surface</th><th>Kind</th><th>Derived status</th><th>Operations</th><th>Disposition</th></tr></thead><tbody>
{body}
</tbody></table>
<h2>Limitations</h2><ul><li>Issue coordinates are validated offline; live issue state is non-authoritative.</li><li>Windows runtime behavior is source-audited on Linux and requires Windows-capable migration verification.</li><li>Branch-protection registration is outside this artifact.</li></ul>
<p>Discovered direct owners: {len(discovery.direct)}; transitive entrypoints: {len(discovery.transitive)}.</p>
</body></html>
"""
    return document.encode("utf-8")


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
