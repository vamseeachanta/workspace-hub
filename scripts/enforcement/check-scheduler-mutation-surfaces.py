#!/usr/bin/env python3
"""Fail-closed, index-backed scheduler mutation inventory validator."""
from __future__ import annotations

import argparse
import ast
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

ROOT = Path(__file__).resolve().parents[2]
REGISTRY = b"config/scheduled-tasks/mutation-surfaces.yaml"
CHECKER = b"scripts/enforcement/check-scheduler-mutation-surfaces.py"
TEST = b"tests/enforcement/test_scheduler_mutation_surfaces.py"
FORENSIC = {CHECKER, TEST}
SENTINEL = b"scheduler-mutation-forensic"
PRIMITIVE_PATTERNS = {
    "crontab-replace": (
        rb"(?:^|[|;\(\s])(?:run_)?crontab[ \t]+-(?:[ \t]|$)",
        rb"\[[ \t]*['\"]crontab['\"][ \t]*,[ \t]*['\"]-['\"]",
    ),  # scheduler-mutation-forensic
    "systemd-user-unit-write": (
        rb"\b(?:write_unit|remove_unit)[ \t]+",
        rb"(?:cat|printf)[^\n]*(?:\.config/systemd/user|SYSTEMD_USER_DIR)",  # scheduler-mutation-forensic
    ),  # scheduler-mutation-forensic
    "systemd-user-enable-disable": (
        rb"\b(?:run_systemctl|systemctl[ \t]+--user)[ \t]+(?:enable|disable)\b",
    ),  # scheduler-mutation-forensic
    "windows-task-set": (rb"\bSet-ScheduledTask\b",),  # scheduler-mutation-forensic
    "windows-task-unregister-register": (
        rb"\b(?:Register|Unregister)-ScheduledTask\b",
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
        for line in body.splitlines():
            if line.lstrip().startswith(b"#") or (raw in FORENSIC and SENTINEL in line):
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
def _tree(records: dict[bytes, bytes], source: bytes) -> ast.Module | None:
    try:
        return ast.parse(records[source].decode())
    except (KeyError, UnicodeDecodeError, SyntaxError):
        return None
def _function(tree: ast.Module | None, name: str) -> ast.FunctionDef | None:
    if tree is None:
        return None
    return next((node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef) and node.name == name), None)


def _assignment_call(fn: ast.FunctionDef | None, variable: str, call: str) -> bool:
    if fn is None:
        return False
    return any(
        isinstance(node, ast.Assign)
        and any(isinstance(target, ast.Name) and target.id == variable for target in node.targets)
        and isinstance(node.value, ast.Call)
        and isinstance(node.value.func, ast.Name)
        and node.value.func.id == call
        for node in ast.walk(fn)
    )


def _call_args(fn: ast.FunctionDef | None, call: str, args: list[str]) -> bool:
    if fn is None:
        return False
    for node in ast.walk(fn):
        if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Name) or node.func.id != call:
            continue
        rendered = [ast.unparse(arg) for arg in node.args]
        if rendered == args:
            return True
    return False


def _eval_python(name: str, records: dict[bytes, bytes], source: bytes) -> bool:
    tree = _tree(records, source)
    run = _function(tree, "run_cutover")
    main = _function(tree, "main")
    run_text = ast.unparse(run) if run else ""
    main_text = ast.unparse(main) if main else ""
    if name == "python-physical-host-equality-guard-v1":
        return bool(re.search(r"if mid != physical_mid:[\s\S]+return 2[\s\S]+run_cutover", main_text))
    if name == "python-baseline-snapshot-v1":
        return _assignment_call(run, "A", "_read")
    if name == "python-lock-scope-v1":
        return bool(re.search(r"with _flock\(LOCKFILE\):[\s\S]+_write\(plan\['new_text'\]\)", run_text))
    if name == "python-backup-baseline-v1":
        return _call_args(run, "create_backup", ["canonical_id", "ts", "A"])
    if name == "python-prewrite-cas-v1":
        return bool(re.search(r"current = _read\(\)[\s\S]+if current != A:[\s\S]+return[\s\S]+_write", run_text))
    if name == "python-postwrite-preservation-multiset-v1":
        return "after_counts = Counter" in run_text and "after_counts[line] < n" in run_text
    if name == "python-postwrite-exact-state-v1":
        return False
    if name == "python-rollback-after-cas-v1":
        return bool(re.search(r"current = _read\(\)[\s\S]+if current != after:[\s\S]+return[\s\S]+_write\(A\)", run_text))
    if name == "cron-command-tokens-adjacent-v1":
        text = ast.unparse(_function(tree, "match_fingerprint")) if tree else ""
        return "shlex.split(line)" in text and "tokens[i:i + width] == wanted" in text
    if name == "cron-classifier-destructive-branches-v1":
        return derive_cron_classifier_branches(records) is not None
    if name == "crontab-current-user-target-v1":
        return _call_args(_function(tree, "write_crontab"), "_run", ["['crontab', '-']"])  # scheduler-mutation-forensic
    return False


def derive_cron_classifier_branches(records: dict[bytes, bytes]) -> set[str] | None:
    tree = _tree(records, b"scripts/cron/cron_transaction.py")
    fn = _function(tree, "classify_line_detail")
    if fn is None:
        return None
    returns: list[str] = []
    for node in ast.walk(fn):
        if not isinstance(node, ast.Return) or not isinstance(node.value, ast.Dict):
            continue
        values = {
            key.value: value.value
            for key, value in zip(node.value.keys, node.value.values)
            if isinstance(key, ast.Constant) and isinstance(value, ast.Constant)
        }
        if values.get("class") == "cataloged":
            returns.append(values.get("reason"))
    module_cataloged = 0
    for node in ast.walk(tree):
        if isinstance(node, ast.Dict):
            rendered = ast.unparse(node)
            if "'class': 'cataloged'" in rendered or '"class": "cataloged"' in rendered:
                module_cataloged += 1
    expected = ["catalog-owned-preserved-entry", "catalog-fingerprint", "catalog-command"]
    if sorted(returns) != sorted(expected) or module_cataloged != 3:
        return None
    return {"preserved-promotion", "installed-fingerprint", "catalog-key-fallback"}


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
        return _eval_python(name, records, source)
    code = _code(records.get(source, b""))
    if name == "shell-physical-host-equality-guard-v1":
        required = (
            b"CANONICAL_MACHINE=", b"PHYSICAL_MACHINE=",
            b'if [[ "$CANONICAL_MACHINE" != "$PHYSICAL_MACHINE" ]]', b"exit 2",
        )
        positions = [code.find(token) for token in required]
        guard = positions[2]
        return (
            all(position >= 0 for position in positions[:3])
            and positions[:3] == sorted(positions[:3])
            and code.find(b"exit 2", guard) > guard
        )
    if name == "shell-local-delegation-v1":
        return b"--machine" not in code and b"ssh " not in code
    if name == "kanban-backend-operation-set-v1":
        return len(derive_kanban_operations(records)) == 6
    patterns = {
        "shell-exact-sentinel-v1": rb"grep -vF \"\$CRON_SENTINEL\"[\s\S]+run_crontab -",
        "crontab-root-target-v1": rb"EUID -ne 0[\s\S]+crontab -",
        "systemd-user-unit-name-v1": rb"UNIT_NAME=\"kanban-loader-sync\"",
        "systemd-user-enable-disable-v1": rb"run_systemctl enable --now[\s\S]+run_systemctl disable --now",  # scheduler-mutation-forensic
        "windows-task-path-name-v1": rb"\$TaskPath = \"\\Claude\\\"[\s\S]+Register-ScheduledTask[\s\S]+-TaskPath \$TaskPath",  # scheduler-mutation-forensic
        "windows-current-user-principal-v1": rb"-UserId \$env:USERNAME[\s\S]+Register-ScheduledTask[\s\S]+-Principal \$principal",  # scheduler-mutation-forensic
        "context-windows-principal-v1": rb"-UserId \$env:USERNAME[\s\S]+Register-ScheduledTask[\s\S]+-Principal \$Principal",  # scheduler-mutation-forensic
        "context-windows-task-path-name-v1": rb"\$TaskPath = \"\\Claude\\\"[\s\S]+Register-ScheduledTask[\s\S]+-TaskPath \$TaskPath",  # scheduler-mutation-forensic
        "solver-windows-task-name-v1": rb"\$TaskName = \"SolverQueue\"[\s\S]+(?:Set|Register)-ScheduledTask -TaskName \$TaskName",
        "windows-task-set-operation-v1": rb"Get-ScheduledTask[\s\S]+Set-ScheduledTask[\s\S]+else \{[\s\S]+Register-ScheduledTask",  # scheduler-mutation-forensic
        "windows-task-unregister-register-v1": rb"if \(\$existing\)[\s\S]+Unregister-ScheduledTask[\s\S]+Register-ScheduledTask",  # scheduler-mutation-forensic
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
    kanban = rows.get("scripts/install/setup-kanban-loader-timer.sh", {})
    if derive_kanban_operations(records) != {operation["id"] for operation in kanban.get("operations", [])}:
        errors.append("kanban backend operation set mismatch")
    migration = {path for path, status in statuses.items() if status == "migration-required"}
    covered: set[str] = set()
    for group in registry.get("disposition_groups", []):
        members = set(group.get("members", []))
        if covered & members:
            errors.append(f"{group.get('group_id')}: duplicate disposition member")
        covered |= members
    if covered != migration:
        errors.append("dispositions must exactly cover migration-required surfaces")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
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
