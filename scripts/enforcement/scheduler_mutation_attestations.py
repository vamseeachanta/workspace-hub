"""Structural source attestations for scheduler mutation surfaces."""
from __future__ import annotations

import ast
import re
from typing import Callable

import yaml

CRON_APPLY = b"scripts/cron/cron_apply.py"
CRON_TRANSACTION = b"scripts/cron/cron_transaction.py"
SCHEDULE = b"config/scheduled-tasks/schedule-tasks.yaml"


def _tree(records: dict[bytes, bytes], source: bytes) -> ast.Module | None:
    try:
        return ast.parse(records[source].decode())
    except (KeyError, UnicodeDecodeError, SyntaxError):
        return None


def _function(tree: ast.Module | None, name: str) -> ast.FunctionDef | None:
    if tree is None:
        return None
    return next(
        (node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef) and node.name == name),
        None,
    )


def _is_call(node: ast.AST, name: str, args: list[str] | None = None) -> bool:
    if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Name):
        return False
    if node.func.id != name:
        return False
    return args is None or [ast.unparse(arg) for arg in node.args] == args


def _assign_call(stmt: ast.stmt, variable: str, call: str, args=None) -> bool:
    return (
        isinstance(stmt, ast.Assign)
        and any(isinstance(target, ast.Name) and target.id == variable for target in stmt.targets)
        and _is_call(stmt.value, call, args)
    )


def _expr_call(stmt: ast.stmt, call: str, args: list[str]) -> bool:
    return isinstance(stmt, ast.Expr) and _is_call(stmt.value, call, args)


def _abort_if(stmt: ast.stmt, left: str, right: str) -> bool:
    if not isinstance(stmt, ast.If) or not isinstance(stmt.test, ast.Compare):
        return False
    test = stmt.test
    names = ast.unparse(test.left), ast.unparse(test.comparators[0])
    return (
        names == (left, right)
        and len(test.ops) == 1
        and isinstance(test.ops[0], ast.NotEq)
        and bool(stmt.body)
        and isinstance(stmt.body[-1], ast.Return)
    )


def _ordered_indices(body: list[ast.stmt], predicates: list[Callable[[ast.stmt], bool]]) -> bool:
    positions = []
    for predicate in predicates:
        found = next((i for i, stmt in enumerate(body) if predicate(stmt)), None)
        if found is None:
            return False
        positions.append(found)
    return positions == sorted(positions) and len(set(positions)) == len(positions)


def _live_withs(body: list[ast.stmt]) -> list[ast.With]:
    locks = []
    for stmt in body:
        if isinstance(stmt, ast.With):
            locks.append(stmt)
        elif isinstance(stmt, (ast.For, ast.AsyncFor)):
            locks.extend(_live_withs(stmt.body))
            locks.extend(_live_withs(stmt.orelse))
        elif isinstance(stmt, ast.If):
            if not (isinstance(stmt.test, ast.Constant) and stmt.test.value is False):
                locks.extend(_live_withs(stmt.body))
            if not (isinstance(stmt.test, ast.Constant) and stmt.test.value is True):
                locks.extend(_live_withs(stmt.orelse))
    return locks


def _prewrite_shape(records: dict[bytes, bytes]) -> bool:
    run = _function(_tree(records, CRON_APPLY), "run_cutover")
    if run is None:
        return False
    baseline = next((s for s in run.body if _assign_call(s, "A", "_read", [])), None)
    locks = [stmt for stmt in run.body if isinstance(stmt, ast.With)]
    for lock in locks:
        if "_flock(LOCKFILE)" not in ast.unparse(lock.items[0].context_expr):
            continue
        predicates = [
            lambda s: _assign_call(s, "current", "_read", []),
            lambda s: _abort_if(s, "current", "A"),
            lambda s: _assign_call(s, "backup", "create_backup", ["canonical_id", "ts", "A"]),
            lambda s: _expr_call(s, "_write", ["plan['new_text']"]),
            lambda s: _assign_call(s, "after", "_read", []),
        ]
        if baseline and baseline.lineno < lock.lineno and _ordered_indices(lock.body, predicates):
            return True
    return False


def _rollback_shape(records: dict[bytes, bytes]) -> bool:
    run = _function(_tree(records, CRON_APPLY), "run_cutover")
    if run is None:
        return False
    for lock in _live_withs(run.body):
        if "_flock(LOCKFILE)" not in ast.unparse(lock.items[0].context_expr):
            continue
        predicates = [
            lambda s: _assign_call(s, "current", "_read", []),
            lambda s: _abort_if(s, "current", "after"),
            lambda s: _expr_call(s, "_write", ["A"]),
        ]
        if _ordered_indices(lock.body, predicates):
            return True
    return False


def derive_cron_classifier_branches(records: dict[bytes, bytes]) -> set[str] | None:
    tree = _tree(records, CRON_TRANSACTION)
    fn = _function(tree, "classify_line_detail")
    if fn is None:
        return None
    reasons = []
    for node in ast.walk(fn):
        if not isinstance(node, ast.Return) or not isinstance(node.value, ast.Dict):
            continue
        values = {
            key.value: value.value
            for key, value in zip(node.value.keys, node.value.values)
            if isinstance(key, ast.Constant) and isinstance(value, ast.Constant)
        }
        if values.get("class") == "cataloged":
            reasons.append(values.get("reason"))
    expected = ["catalog-owned-preserved-entry", "catalog-fingerprint", "catalog-command"]
    module_count = sum(
        "'class': 'cataloged'" in ast.unparse(node)
        for node in ast.walk(tree)
        if isinstance(node, ast.Dict)
    )
    if sorted(reasons) != sorted(expected) or module_count != 3:
        return None
    return {
        "preserved-promotion", "installed-fingerprint-token",
        "installed-fingerprint-substring", "catalog-key-fallback",
    }


def derive_installed_fingerprint_branches(records: dict[bytes, bytes]) -> set[str]:
    try:
        tasks = (yaml.safe_load(records[SCHEDULE]) or {}).get("tasks", [])
    except (KeyError, yaml.YAMLError):
        return set()
    result = set()
    for task in tasks:
        fingerprint = task.get("installed_fingerprint") or {}
        if "command_tokens" in fingerprint:
            result.add("installed-fingerprint-token")
        if fingerprint and "command_tokens" not in fingerprint:
            result.add("installed-fingerprint-substring")
    return result


def forensic_literal_lines(body: bytes) -> set[int]:
    try:
        tree = ast.parse(body.decode())
    except (SyntaxError, UnicodeDecodeError):
        return set()
    lines = set()
    for node in ast.walk(tree):
        if not isinstance(node, (ast.Assign, ast.AnnAssign)):
            continue
        value = node.value
        if value is None or any(isinstance(child, ast.Call) for child in ast.walk(value)):
            continue
        for literal in (child for child in ast.walk(value) if isinstance(child, ast.Constant)):
            raw = literal.value
            text = raw.decode("utf-8", "ignore") if isinstance(raw, bytes) else raw
            if not isinstance(text, str):
                continue
            words = ("Scheduled" + "Task", "write" + "_unit", "remove" + "_unit", "run" + "_systemctl")
            systemd = ".config/systemd/user" in text or "SYSTEMD_USER_DIR" in text
            scheduler = systemd or any(word in text for word in words) or ("cron" + "tab" in text and "-" in text)
            if scheduler:
                lines.update(range(literal.lineno, getattr(literal, "end_lineno", literal.lineno) + 1))
    return lines


def _ps_extract_block(code: str, pattern: str) -> tuple[str, int, int] | None:
    match = re.search(pattern, code, re.IGNORECASE)
    if not match:
        return None
    start = code.find("{", match.start())
    if start < 0:
        return None
    depth = 0
    for index in range(start, len(code)):
        if code[index] == "{":
            depth += 1
        elif code[index] == "}":
            depth -= 1
            if depth == 0:
                return code[start + 1:index], match.start(), index + 1
    return None


def _ps_live_code(body: bytes, include_function: str | None = None) -> str:
    code = body.decode("utf-8", "ignore")
    code = re.sub(r"<#[\s\S]*?#>", "", code)
    code = "\n".join(line for line in code.splitlines() if not line.lstrip().startswith("#"))
    selected = ""
    if include_function:
        block = _ps_extract_block(code, rf"function\s+{re.escape(include_function)}\s*\{{")
        if block:
            selected = block[0]
    while True:
        dead = _ps_extract_block(code, r"if\s*\(\s*\$false\s*\)\s*\{")
        if not dead:
            break
        code = code[:dead[1]] + code[dead[2]:]
    while True:
        function = _ps_extract_block(code, r"function\s+[A-Za-z_][\w-]*\s*\{")
        if not function:
            break
        code = code[:function[1]] + code[function[2]:]
    if include_function and not re.search(rf"(?m)^\s*{re.escape(include_function)}\s+`?\s*$", code):
        selected = ""
    return code + "\n" + selected


def evaluate_windows(name: str, records: dict[bytes, bytes], source: bytes) -> bool | None:
    if not (name.startswith("windows-") or name.startswith("context-windows") or name.startswith("solver-windows")):
        return None
    function = "Register-ClaudeTask" if source.endswith(b"setup-scheduler-tasks.ps1") else None
    code = _ps_live_code(records.get(source, b""), function)
    patterns = {
        "windows-task-path-name-v1": r"\$TaskPath\s*=\s*['\"]\\Claude\\['\"][\s\S]+Register-ScheduledTask[\s\S]+-TaskPath\s+\$TaskPath",  # scheduler-mutation-forensic
        "windows-current-user-principal-v1": r"\$principal\s*=\s*New-ScheduledTaskPrincipal\s+-UserId\s+\$env:USERNAME[\s\S]+Register-ScheduledTask[\s\S]+-Principal\s+\$principal",  # scheduler-mutation-forensic
        "context-windows-principal-v1": r"\$Principal\s*=\s*New-ScheduledTaskPrincipal\s+-UserId\s+\$env:USERNAME[\s\S]+Register-ScheduledTask[\s\S]+-Principal\s+\$Principal",  # scheduler-mutation-forensic
        "context-windows-task-path-name-v1": r"\$TaskPath\s*=\s*['\"]\\Claude\\['\"][\s\S]+Register-ScheduledTask[\s\S]+-TaskPath\s+\$TaskPath",  # scheduler-mutation-forensic
        "solver-windows-task-name-v1": r"\$TaskName\s*=\s*['\"]SolverQueue['\"][\s\S]+(?:Set|Register)-ScheduledTask\s+-TaskName\s+\$TaskName",  # scheduler-mutation-forensic
        "windows-task-set-operation-v1": r"if\s*\(Get-ScheduledTask[\s\S]+Set-ScheduledTask[\s\S]+else\s*\{[\s\S]+Register-ScheduledTask",  # scheduler-mutation-forensic
        "windows-task-unregister-register-v1": r"if\s*\(\$existing\)[\s\S]+Unregister-ScheduledTask[\s\S]+Register-ScheduledTask",  # scheduler-mutation-forensic
    }
    return bool(name in patterns and re.search(patterns[name], code, re.IGNORECASE))


def _shell_host_guard(records: dict[bytes, bytes], source: bytes) -> bool:
    code = records.get(source, b"")
    canonical = code.find(b"CANONICAL_MACHINE=")
    physical = code.find(b"PHYSICAL_MACHINE=")
    guard = code.find(b'if [[ "$CANONICAL_MACHINE" != "$PHYSICAL_MACHINE" ]]')
    guard_end = code.find(b"\nfi", guard)
    abort = code.find(b"\n  exit 2", guard, guard_end)
    execute = code.find(b'exec uv run --script "$CRON_APPLY"')
    positions = (canonical, physical, guard, abort, guard_end, execute)
    return all(pos >= 0 for pos in positions) and list(positions) == sorted(positions)


def evaluate_python(name: str, records: dict[bytes, bytes], source: bytes) -> bool:
    tree = _tree(records, source)
    run = _function(tree, "run_cutover")
    main = _function(tree, "main")
    if name == "python-physical-host-equality-guard-v1":
        if main is None:
            return False
        guard = next((stmt for stmt in main.body if _abort_if(stmt, "mid", "physical_mid")), None)
        call = next((stmt for stmt in main.body if "run_cutover(" in ast.unparse(stmt)), None)
        return bool(guard and call and guard.lineno < call.lineno)
    if name in {"python-lock-scope-v1", "python-baseline-snapshot-v1", "python-backup-baseline-v1", "python-prewrite-cas-v1"}:
        return _prewrite_shape(records)
    if name == "python-postwrite-preservation-multiset-v1":
        text = ast.unparse(run) if run else ""
        return "after_counts = Counter" in text and "after_counts[line] < n" in text
    if name == "python-postwrite-exact-state-v1":
        return False
    if name == "python-rollback-after-cas-v1":
        return _rollback_shape(records)
    if name == "cron-command-tokens-adjacent-v1":
        text = ast.unparse(_function(tree, "match_fingerprint")) if tree else ""
        return "shlex.split(line)" in text and "tokens[i:i + width] == wanted" in text
    if name == "cron-classifier-destructive-branches-v1":
        return derive_cron_classifier_branches(records) is not None
    if name == "crontab-current-user-target-v1":
        fn = _function(tree, "write_crontab")
        needle = "_run([" + repr("crontab") + ", " + repr("-") + "]"
        return bool(fn and needle in ast.unparse(fn))
    return False


def evaluate_shell_guard(name: str, records: dict[bytes, bytes], source: bytes) -> bool | None:
    if name == "shell-physical-host-equality-guard-v1":
        return _shell_host_guard(records, source)
    if name == "shell-local-delegation-v1":
        code = records.get(source, b"")
        return b"--machine" not in code and b"ssh " not in code
    return None
