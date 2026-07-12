"""Reachable Python control-flow evidence for scheduler transactions."""
from __future__ import annotations

import ast


def _functions(tree: ast.AST) -> dict[str, ast.FunctionDef]:
    return {node.name: node for node in getattr(tree, "body", [])
            if isinstance(node, ast.FunctionDef)}


Path = tuple[list[ast.stmt], bool, list[str]]


def _walk_block(statements: list[ast.stmt]) -> list[Path]:
    paths: list[Path] = [([], True, [])]
    for statement in statements:
        if isinstance(statement, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            continue
        paths = _extend_paths(paths, _walk_statement(statement))
    return paths


def _extend_paths(prefixes: list[Path], suffixes: list[Path]) -> list[Path]:
    result: list[Path] = []
    for prefix, prefix_falls, prefix_locks in prefixes:
        if not prefix_falls:
            result.append((prefix, False, prefix_locks))
            continue
        for suffix, suffix_falls, suffix_locks in suffixes:
            result.append((prefix + suffix, suffix_falls,
                           prefix_locks + suffix_locks))
    return result


def _walk_statement(statement: ast.stmt) -> list[Path]:
    if isinstance(statement, (ast.Return, ast.Raise, ast.Break, ast.Continue)):
        return [([statement], False, [])]
    if isinstance(statement, ast.If):
        if isinstance(statement.test, ast.Constant):
            branch = statement.body if statement.test.value else statement.orelse
            return _walk_block(branch)
        branches = _walk_block(statement.body) + _walk_block(statement.orelse)
        return [([statement, *nodes], falls, locks)
                for nodes, falls, locks in branches]
    if isinstance(statement, ast.With):
        flock = "_flock(LOCKFILE)" in ast.unparse(statement.items[0].context_expr)
        return [([statement, *nodes], falls,
                 locks + ([_path_text(nodes)] if flock else []))
                for nodes, falls, locks in _walk_block(statement.body)]
    if isinstance(statement, ast.Try):
        normal = _extend_paths(_walk_block(statement.body), _walk_block(statement.orelse))
        handlers = [path for handler in statement.handlers
                    for path in _walk_block(handler.body)]
        alternatives = normal + handlers
        return _append_finally(statement, alternatives)
    if isinstance(statement, (ast.For, ast.While)):
        # Loop execution/fallthrough is path-dependent. Retain no body evidence;
        # transaction guarantees must be established outside ambiguous loops.
        return [([statement], True, [])]
    return [([statement], True, [])]


def _append_finally(statement: ast.Try, paths: list[Path]) -> list[Path]:
    if not statement.finalbody:
        return [([statement, *nodes], falls, locks)
                for nodes, falls, locks in paths]
    final_paths = _walk_block(statement.finalbody)
    result: list[Path] = []
    for nodes, falls, locks in paths:
        for final, final_falls, final_locks in final_paths:
            result.append(([statement, *nodes, *final], falls and final_falls,
                           locks + final_locks))
    return result


def _live_texts(function: ast.FunctionDef | None) -> list[str]:
    return [text for text, _locks in _live_paths(function)]


def _live_paths(function: ast.FunctionDef | None) -> list[tuple[str, list[str]]]:
    if function is None:
        return []
    return [(_path_text(path), locks)
            for path, _falls, locks in _walk_block(function.body)]


def _path_text(path: list[ast.stmt]) -> str:
    return "\n".join(_statement_text(node) for node in path)


def _statement_text(node: ast.stmt) -> str:
    if isinstance(node, ast.If):
        return f"if {ast.unparse(node.test)}:"
    if isinstance(node, ast.With):
        items = ", ".join(ast.unparse(item.context_expr) for item in node.items)
        return f"with {items}:"
    if isinstance(node, ast.For):
        return f"for {ast.unparse(node.target)} in {ast.unparse(node.iter)}:"
    if isinstance(node, ast.While):
        return f"while {ast.unparse(node.test)}:"
    if isinstance(node, ast.Try):
        return "try:"
    return ast.unparse(node)


def _has_tokens(texts: list[str], tokens: tuple[str, ...]) -> bool:
    return any(all(token in text for token in tokens) for text in texts)


def _has_ordered(texts: list[str], tokens: tuple[str, ...]) -> bool:
    for text in texts:
        positions = [text.find(token) for token in tokens]
        if all(position >= 0 for position in positions) and positions == sorted(positions):
            return True
    return False


def _path_has_lock_sequence(path: tuple[str, list[str]], tokens: tuple[str, ...]) -> bool:
    _text, locks = path
    return _has_ordered(locks, tokens)


def _transaction_graph(functions: dict[str, ast.FunctionDef]) -> bool:
    run = _live_texts(functions.get("run_cutover"))
    build = _live_texts(functions.get("_build_cutover"))
    finish = _live_texts(functions.get("_finish_exact"))
    return _has_ordered(run, (
        "_build_cutover(selection, classes, ownership, _read)",
        "_write_observation(plan['new_text'], _read, _write)",
        "_finish_exact(A, plan['new_text'], backup, observation, _read, _write)",
    )) and _has_tokens(build, ("ct.plan_cutover(",)) and _has_tokens(
        finish, ("_rollback(",))


def evaluate_transaction(name: str, tree: ast.AST) -> bool | None:
    supported = {
        "python-lock-scope-v1", "python-baseline-snapshot-v1",
        "python-prewrite-cas-v1", "python-backup-baseline-v1",
        "python-postwrite-exact-state-v1", "python-rollback-after-cas-v1",
        "python-rollback-exact-baseline-v1",
    }
    if name not in supported:
        return None
    functions = _functions(tree)
    if not _transaction_graph(functions):
        return False
    run = functions.get("run_cutover")
    sequence = (
        "current = _read()", "current != A",
        "backup = create_backup(canonical_id, ts, A)",
        "observation = _write_observation(plan['new_text'], _read, _write)",
    )
    common = any(_path_has_lock_sequence(path, sequence)
                 for path in _live_paths(run))
    if name in {"python-lock-scope-v1", "python-baseline-snapshot-v1",
                "python-prewrite-cas-v1", "python-backup-baseline-v1"}:
        return common
    if name == "python-postwrite-exact-state-v1":
        observe = _live_texts(functions.get("_write_observation"))
        finish = _live_texts(functions.get("_finish_exact"))
        return _has_ordered(observe, ("_write(B)", "observed = _read()")) and _has_ordered(
            finish, (
                "if not write_failed and observed == B:",
                "_transaction_result('applied', backup, expected=B, observed=observed)",
            )
        )
    if name in {"python-rollback-after-cas-v1", "python-rollback-exact-baseline-v1"}:
        rollback = functions.get("_rollback")
        paths = _live_paths(rollback)
        sequence = (
            "current = _read()", "if current != C:", "_write(A)", "restored = _read()",
        )
        cas = any(_path_has_lock_sequence(path, sequence) for path in paths)
        if name == "python-rollback-after-cas-v1":
            return cas
        exact = "'rolled-back' if restored == A else 'rollback-failed'"
        return any(exact in text and _path_has_lock_sequence(path, sequence)
                   for path in paths for text, _locks in [path])
    return None
