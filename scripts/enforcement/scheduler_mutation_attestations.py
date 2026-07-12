"""Structural source attestations for scheduler mutation surfaces."""
from __future__ import annotations

import ast
import io
import re
import tokenize
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
        and any(isinstance(node, ast.Return) for node in ast.walk(stmt))
    )


def _ordered_indices(body: list[ast.stmt], predicates: list[Callable[[ast.stmt], bool]]) -> bool:
    positions = []
    for predicate in predicates:
        found = next((i for i, stmt in enumerate(body) if predicate(stmt)), None)
        if found is None:
            return False
        positions.append(found)
    return positions == sorted(positions) and len(set(positions)) == len(positions)


def _prewrite_shape(records: dict[bytes, bytes]) -> bool:
    run = _function(_tree(records, CRON_APPLY), "run_cutover")
    if run is None:
        return False
    baseline = next((s for s in run.body if _assign_call(s, "A", "_read", [])), None)
    locks = [node for node in ast.walk(run) if isinstance(node, ast.With)]
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
    for lock in (node for node in ast.walk(run) if isinstance(node, ast.With)):
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
        tokens = tokenize.tokenize(io.BytesIO(body).readline)
    except (SyntaxError, tokenize.TokenError):
        return set()
    lines = set()
    try:
        for token in tokens:
            if token.type != tokenize.STRING:
                continue
            text = token.string
            scheduler_literal = any(
                word in text
                for word in ("ScheduledTask", "write_unit", "remove_unit", "run_systemctl")
            ) or ("crontab" in text and "-" in text)
            if scheduler_literal:
                lines.update(range(token.start[0], token.end[0] + 1))
    except (SyntaxError, tokenize.TokenError):
        return set()
    return lines


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
        text = ast.unparse(main) if main else ""
        return bool(re.search(r"if mid != physical_mid:[\s\S]+return 2[\s\S]+run_cutover", text))
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
        return bool(fn and "_run(['crontab', '-']" in ast.unparse(fn))  # scheduler-mutation-forensic
    return False


def evaluate_shell_guard(name: str, records: dict[bytes, bytes], source: bytes) -> bool | None:
    if name == "shell-physical-host-equality-guard-v1":
        return _shell_host_guard(records, source)
    if name == "shell-local-delegation-v1":
        code = records.get(source, b"")
        return b"--machine" not in code and b"ssh " not in code
    return None
