#!/usr/bin/env python3
"""Fail-closed, index-backed scheduler mutation inventory validator."""
from __future__ import annotations

import argparse, ast, hashlib, json, re, struct, subprocess, sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any
import yaml

ROOT = Path(__file__).resolve().parents[2]
REGISTRY = b"config/scheduled-tasks/mutation-surfaces.yaml"
FORENSIC = {b"scripts/enforcement/check-scheduler-mutation-surfaces.py", b"tests/enforcement/test_scheduler_mutation_surfaces.py"}
SENTINEL = b"scheduler-mutation-forensic"
PRIMITIVE_PATTERNS = {
    "crontab-replace": (rb"(?:^|[|;(\s])(?:run_)?crontab[ \t]+-(?:[ \t]|$)", rb"\[['\"]crontab['\"],[ \t]*['\"]-['\"]\]"),  # scheduler-mutation-forensic
    "systemd-user-unit-write": (rb"\b(?:write_unit|remove_unit)[ \t]+",),  # scheduler-mutation-forensic
    "systemd-user-enable-disable": (rb"\b(?:run_systemctl|systemctl[ \t]+--user)[ \t]+(?:enable|disable)\b",),  # scheduler-mutation-forensic
    "windows-task-set": (rb"\bSet-ScheduledTask\b",),  # scheduler-mutation-forensic
    "windows-task-unregister-register": (rb"\b(?:Register|Unregister)-ScheduledTask\b",),  # scheduler-mutation-forensic
}
CALLEES = (b"scripts/cron/cron_apply.py", b"scripts/cron/setup-cron.sh")
TX_FIELDS = ("lock", "baseline_snapshot", "backup", "pre_write_cas", "post_write_preservation_verify", "post_write_exact_state_verify", "rollback_cas")
TX_ATTEST = {"lock": "python-prewrite-baseline-cas-v1", "baseline_snapshot": "python-prewrite-baseline-cas-v1", "backup": "python-prewrite-baseline-cas-v1", "pre_write_cas": "python-prewrite-baseline-cas-v1", "post_write_preservation_verify": "python-postwrite-preservation-multiset-v1", "post_write_exact_state_verify": "python-postwrite-exact-state-v1", "rollback_cas": "python-rollback-after-cas-v1"}
ATT_SOURCES = {
    "python-physical-host-equality-guard-v1": b"scripts/cron/cron_apply.py", "python-prewrite-baseline-cas-v1": b"scripts/cron/cron_apply.py",
    "python-postwrite-preservation-multiset-v1": b"scripts/cron/cron_apply.py", "python-postwrite-exact-state-v1": b"scripts/cron/cron_apply.py",
    "python-rollback-after-cas-v1": b"scripts/cron/cron_apply.py", "cron-command-tokens-adjacent-v1": b"scripts/cron/cron_transaction.py",
    "cron-classifier-destructive-branches-v1": b"scripts/cron/cron_transaction.py", "shell-exact-sentinel-v1": b"scripts/install/setup-kanban-loader-timer.sh",
    "kanban-backend-operation-set-v1": b"scripts/install/setup-kanban-loader-timer.sh", "crontab-current-user-target-v1": b"scripts/cron/cron_apply.py",
    "crontab-root-target-v1": b"scripts/setup/setup-engineering-update-cron.sh", "systemd-user-unit-name-v1": b"scripts/install/setup-kanban-loader-timer.sh",
    "systemd-user-enable-disable-v1": b"scripts/install/setup-kanban-loader-timer.sh", "windows-task-path-name-v1": b"scripts/windows/setup-scheduler-tasks.ps1",
    "windows-current-user-principal-v1": b"scripts/windows/setup-scheduler-tasks.ps1", "windows-task-set-operation-v1": b"scripts/solver/setup-scheduler.ps1",
    "windows-task-unregister-register-v1": b"scripts/windows/setup-scheduler-tasks.ps1", "context-windows-principal-v1": b"scripts/coordination/context/setup_scheduled_task.ps1",
}

class GitTransportError(RuntimeError): pass
@dataclass(frozen=True)
class Discovery:
    direct: set[str]; transitive: set[str]; edges: set[tuple[str, str]]; primitives: dict[str, set[str]]; unknown_edges: set[str]
@dataclass(frozen=True)
class ValidationResult:
    errors: list[str]; statuses: dict[str, str]

def _s(path: bytes) -> str: return path.decode("utf-8", "surrogateescape")
def _code(body: bytes) -> bytes: return b"\n".join(x for x in body.splitlines() if not x.lstrip().startswith(b"#"))
def attestation_source(name: str) -> bytes: return ATT_SOURCES.get(name, b"")

def read_index_records(repo: Path, git_command: str = "git") -> dict[bytes, bytes]:
    ls = subprocess.run([git_command, "ls-files", "-z"], cwd=repo, capture_output=True)
    if ls.returncode: raise GitTransportError("git ls-files -z failed")
    paths = [p for p in ls.stdout.split(b"\0") if p]
    cmd = b"".join(b"contents :" + p + b"\0" for p in paths)
    out = subprocess.run([git_command, "cat-file", "--batch-command", "-Z"], cwd=repo, input=cmd, capture_output=True)
    if out.returncode: raise GitTransportError("Git cat-file --batch-command -Z support is required")
    records, pos = {}, 0
    for path in paths:
        end = out.stdout.find(b"\0", pos)
        if end < 0: raise GitTransportError("truncated NUL header")
        header, pos = out.stdout[pos:end], end + 1
        parts = header.rsplit(b" ", 2)
        if len(parts) != 3 or parts[1] != b"blob": raise GitTransportError(f"missing index blob: {_s(path)}")
        size = int(parts[2]); blob = out.stdout[pos:pos + size]; pos += size
        if len(blob) != size or out.stdout[pos:pos + 1] != b"\0": raise GitTransportError("truncated NUL content")
        records[path], pos = blob, pos + 1
    return records

def discover_mutation_surfaces(records: dict[bytes, bytes]) -> Discovery:
    direct, transitive, edges, primitives, unknown = set(), set(), set(), {}, set()
    for raw, body in records.items():
        if not raw.startswith(b"scripts/") or not raw.endswith((b".sh", b".py", b".ps1")): continue
        path, code = _s(raw), _code(body)
        found = set()
        for line in body.splitlines():
            if line.lstrip().startswith(b"#") or (raw in FORENSIC and SENTINEL in line): continue
            for primitive, patterns in PRIMITIVE_PATTERNS.items():
                if any(re.search(p, line) for p in patterns): found.add(primitive)
        if found: direct.add(path); primitives[path] = found
        if raw not in FORENSIC:
            for callee in CALLEES:
                literal = re.search(rb"(?m)^[ \t]*(?:\w+=\$\()?[ \t]*bash[ \t]+[^\n]*" + re.escape(callee), code)
                constant = raw == b"scripts/cron/harness-update.sh" and callee.endswith(b"setup-cron.sh") and b'bash "$installer"' in code
                reviewed = raw == b"scripts/cron/setup-cron.sh" and callee.endswith(b"cron_apply.py") and callee in code
                if raw != callee and (literal or constant or reviewed): transitive.add(path); edges.add((path, _s(callee)))
            if re.search(rb"(?m)^\s*\$[A-Z_]*(?:SCHEDUL|CRON)[A-Z_]*\b", code): unknown.add(path)
    return Discovery(direct, transitive, edges, primitives, unknown)

def _python_tree(records, source):
    try: return ast.parse(records[source].decode())
    except (KeyError, UnicodeDecodeError, SyntaxError): return None
def _function(tree, name): return next((n for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name == name), None) if tree else None
def _calls(node, name): return [n for n in ast.walk(node) if isinstance(n, ast.Call) and ((isinstance(n.func, ast.Name) and n.func.id == name) or (isinstance(n.func, ast.Attribute) and n.func.attr == name))]

def _eval_python(name, records, source):
    tree = _python_tree(records, source)
    run, main = _function(tree, "run_cutover"), _function(tree, "main")
    text = ast.unparse(tree) if tree else ""
    if name == "python-physical-host-equality-guard-v1": return bool(main and re.search(r"if mid != physical_mid:[\s\S]+return 2[\s\S]+run_cutover", ast.unparse(main)))
    if name == "python-prewrite-baseline-cas-v1": return bool(run and re.search(r"with _flock\(LOCKFILE\):[\s\S]+if current != A:[\s\S]+return [\s\S]+create_backup[\s\S]+_write", ast.unparse(run)))
    if name == "python-postwrite-preservation-multiset-v1": return bool(run and "after_counts = Counter" in ast.unparse(run) and "after_counts[line] < n" in ast.unparse(run))
    if name == "python-postwrite-exact-state-v1": return False
    if name == "python-rollback-after-cas-v1": return bool(run and re.search(r"if current != after:[\s\S]+return [\s\S]+_write\(A\)", ast.unparse(run)))
    if name == "cron-command-tokens-adjacent-v1": return bool(_function(tree, "match_fingerprint") and "shlex.split(line)" in text and "tokens[i:i + width] == wanted" in text)
    if name == "cron-classifier-destructive-branches-v1": return derive_cron_classifier_branches(records) is not None
    if name == "crontab-current-user-target-v1": return bool(_function(tree, "write_crontab") and re.search(r"_run\(\['crontab', '-'\]", ast.unparse(_function(tree, "write_crontab"))))  # scheduler-mutation-forensic
    return False

def derive_cron_classifier_branches(records):
    tree = _python_tree(records, b"scripts/cron/cron_transaction.py"); fn = _function(tree, "classify_line_detail")
    if not fn: return None
    reasons, module_reasons = set(), set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Dict): continue
        values = {k.value: v.value for k, v in zip(node.keys, node.values) if isinstance(k, ast.Constant) and isinstance(k.value, str) and isinstance(v, ast.Constant)}
        if values.get("class") == "cataloged": module_reasons.add(values.get("reason"))
    for node in ast.walk(fn):
        if isinstance(node, ast.Dict):
            values = {k.value: v.value for k, v in zip(node.keys, node.values) if isinstance(k, ast.Constant) and isinstance(k.value, str) and isinstance(v, ast.Constant)}
            if values.get("class") == "cataloged": reasons.add(values.get("reason"))
    expected = {"catalog-owned-preserved-entry", "catalog-fingerprint", "catalog-command"}
    if reasons != expected or module_reasons != expected: return None
    return {"preserved-promotion", "installed-fingerprint", "catalog-key-fallback"}

def derive_kanban_operations(records):
    code = _code(records.get(b"scripts/install/setup-kanban-loader-timer.sh", b""))
    checks = {"install:systemd-unit-write": b'write_unit "$SERVICE_PATH"', "install:systemd-enable": b"run_systemctl enable --now", "install:crontab-replace": b"run_crontab -", "uninstall:systemd-unit-remove": b'remove_unit "$SERVICE_PATH"', "uninstall:systemd-disable": b"run_systemctl disable --now", "uninstall:crontab-replace": b"sed '/^$/d' | run_crontab -"}  # scheduler-mutation-forensic
    return {key for key, token in checks.items() if token in code}

def evaluate_attestation(name, records, operation_source=b""):
    source = attestation_source(name) or operation_source; code = _code(records.get(source, b""))
    if name.startswith("python-") or name.startswith("cron-") or name == "crontab-current-user-target-v1": return _eval_python(name, records, source)
    if name == "kanban-backend-operation-set-v1": return len(derive_kanban_operations(records)) == 6
    exact = {
        "shell-exact-sentinel-v1": rb"grep -vF [\"']\$CRON_SENTINEL[\"'][\s\S]+run_crontab -", "crontab-root-target-v1": rb"if \[\[ \$EUID -ne 0 \]\];[\s\S]+crontab -",  # scheduler-mutation-forensic
        "systemd-user-unit-name-v1": rb"UNIT_NAME=[\"']kanban-loader-sync[\"']", "systemd-user-enable-disable-v1": rb"run_systemctl enable --now[\s\S]+run_systemctl disable --now",  # scheduler-mutation-forensic
        "windows-task-path-name-v1": rb"\$TaskPath = [\"']\\Claude\\[\"'][\s\S]+Register-ScheduledTask[\s\S]+-TaskPath \$TaskPath",  # scheduler-mutation-forensic
        "windows-current-user-principal-v1": rb"\$principal = New-ScheduledTaskPrincipal -UserId \$env:USERNAME[\s\S]+Register-ScheduledTask[\s\S]+-Principal \$principal",  # scheduler-mutation-forensic
        "context-windows-principal-v1": rb"\$Principal = New-ScheduledTaskPrincipal -UserId \$env:USERNAME[\s\S]+Register-ScheduledTask[\s\S]+-Principal \$Principal",  # scheduler-mutation-forensic
        "windows-task-set-operation-v1": rb"if \(Get-ScheduledTask[\s\S]+Set-ScheduledTask[\s\S]+else \{[\s\S]+Register-ScheduledTask",  # scheduler-mutation-forensic
        "windows-task-unregister-register-v1": rb"if \(\$existing\)[\s\S]+Unregister-ScheduledTask[\s\S]+Register-ScheduledTask",  # scheduler-mutation-forensic
    }
    return bool(name in exact and re.search(exact[name], code))

def derive_status(branches, attestations, required_transactions):
    weak = any(b.get("destructive") and b.get("strength") in {"substring", "unknown"} for b in branches)
    return "migration-required" if weak or not all(attestations) or not all(required_transactions) else "compliant"
def input_digest(registry_bytes, records):
    data = bytearray(b"scheduler-mutation-input-v1\0" + struct.pack(">Q", len(registry_bytes)) + registry_bytes + struct.pack(">Q", len(records)))
    for path, blob in sorted(records.items()): data += struct.pack(">Q", len(path)) + path + struct.pack(">Q", len(blob)) + blob
    return hashlib.sha256(data).hexdigest()

def digest_record_union(registry, records):
    paths = {REGISTRY, b"scripts/enforcement/check-scheduler-mutation-surfaces.py", b"tests/enforcement/test_scheduler_mutation_surfaces.py", b".github/workflows/enforcement-gate.yml"}
    for row in registry.get("surfaces", []):
        paths.add(row["path"].encode())
        for op in row.get("operations", []):
            paths |= {b["config_source"].encode() for b in op.get("authority_branches", [])}
            paths |= {attestation_source(a) for a in op.get("attestations", [])}
        if row.get("edge", {}).get("target_guard_attestation"): paths.add(attestation_source(row["edge"]["target_guard_attestation"]))
    return {p: records[p] for p in paths if p}

def _validate_operation(path, op, records, errors):
    ids = [b.get("id") for b in op.get("authority_branches", [])]
    for branch in op.get("authority_branches", []):
        source = branch.get("config_source", "").encode()
        if source not in records: errors.append(f"{path}: config_source is not tracked: {_s(source)}")
        if branch.get("id") == "preserved-promotion" and source != b"config/workstations/harness-state-classes.yaml": errors.append(f"{path}: config_source not structurally connected")
    tx, attest = op.get("transaction", {}), op.get("attestations", [])
    if set(tx) != set(TX_FIELDS): errors.append(f"{path}: complete transaction contract required")
    for field, value in tx.items():
        needed = TX_ATTEST[field]
        if value and needed not in attest: errors.append(f"{path}: true {field} requires {needed}")
    for name in attest:
        if name not in ATT_SOURCES: errors.append(f"{path}: unknown attestation {name}")
        elif not evaluate_attestation(name, records, path.encode()) and any(tx.values()): errors.append(f"{path}: attestation failed: {name}")
    return ids, [b for b in op.get("authority_branches", [])], [evaluate_attestation(a, records, path.encode()) for a in attest], [bool(tx.get(f)) for f in TX_FIELDS]

def validate_registry(registry, discovery, records):
    errors, statuses, rows = [], {}, {}
    for row in registry.get("surfaces", []):
        path = row.get("path", ""); rows[path] = row; op_ids = [o.get("id") for o in row.get("operations", [])]
        if len(op_ids) != len(set(op_ids)): errors.append(f"{path}: duplicate operation id")
        branches, attest, txs = [], [], []
        for op in row.get("operations", []):
            _, bs, ats, ts = _validate_operation(path, op, records, errors); branches += bs; attest += ats; txs += ts
        statuses[path] = derive_status(branches, attest or [False], txs)
        if row.get("kind") == "transitive-entrypoint":
            edge = row.get("edge", {}); guard = edge.get("target_guard_attestation", "")
            if edge.get("call_form") not in {"literal-exec", "literal-bash", "constant-path-exec"} or (path, edge.get("callee", "")) not in discovery.edges: errors.append(f"{path}: unrecognized call grammar")
            if guard not in ATT_SOURCES or not evaluate_attestation(guard, records, path.encode()): errors.append(f"{path}: target_guard_attestation failed")
    registered_direct = {p for p, r in rows.items() if r.get("kind") == "direct-owner"}; registered_trans = set(rows) - registered_direct
    for p in sorted(discovery.direct ^ registered_direct): errors.append(f"direct inventory mismatch: {p}")
    for p in sorted(discovery.transitive ^ registered_trans): errors.append(f"transitive inventory mismatch: {p}")
    for p in discovery.unknown_edges: errors.append(f"unknown scheduler indirection: {p}")
    cron = rows.get("scripts/cron/cron_apply.py", {}); actual = {b["id"] for o in cron.get("operations", []) for b in o.get("authority_branches", [])}
    if derive_cron_classifier_branches(records) != actual: errors.append("cron destructive classifier branch set mismatch")
    kanban = rows.get("scripts/install/setup-kanban-loader-timer.sh", {}); declared = {o["id"] for o in kanban.get("operations", [])}
    if declared != derive_kanban_operations(records): errors.append("kanban backend operation set mismatch")
    migration = {p for p, s in statuses.items() if s == "migration-required"}; covered = {p for g in registry.get("disposition_groups", []) for p in g.get("members", [])}
    if migration != covered: errors.append("dispositions must exactly cover migration-required surfaces")
    return ValidationResult(errors, statuses)

def main(argv=None):
    parser = argparse.ArgumentParser(); parser.add_argument("--json", action="store_true"); args = parser.parse_args(argv)
    try:
        records = read_index_records(ROOT); raw = records[REGISTRY]; registry = yaml.safe_load(raw); found = discover_mutation_surfaces(records); result = validate_registry(registry, found, records)
        digest = input_digest(raw, digest_record_union(registry, records))
    except (GitTransportError, KeyError, yaml.YAMLError) as exc:
        found, result, digest = Discovery(set(), set(), set(), {}, set()), ValidationResult([str(exc)], {}), ""
    payload = {"direct": sorted(found.direct), "errors": result.errors, "input_digest": digest, "status": "ok" if not result.errors else "error", "transitive": sorted(found.transitive)}
    if args.json: print(json.dumps(payload, sort_keys=True))
    else:
        for error in result.errors: print(f"ERROR: {error}", file=sys.stderr)
    return bool(result.errors)
if __name__ == "__main__": raise SystemExit(main())
