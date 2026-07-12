"""Reachable Python control-flow evidence for scheduler transactions."""
from __future__ import annotations

import ast


def _functions(tree: ast.AST) -> dict[str, ast.FunctionDef]:
    return {node.name: node for node in getattr(tree, "body", [])
            if isinstance(node, ast.FunctionDef)}


def _live_nodes(statements: list[ast.stmt]):
    nodes, _falls_through = _walk_block(statements)
    yield from nodes


def _walk_block(statements: list[ast.stmt]) -> tuple[list[ast.stmt], bool]:
    nodes: list[ast.stmt] = []
    for statement in statements:
        if isinstance(statement, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            continue
        statement_nodes, falls_through = _walk_statement(statement)
        nodes.extend(statement_nodes)
        if not falls_through:
            return nodes, False
    return nodes, True


def _walk_statement(statement: ast.stmt) -> tuple[list[ast.stmt], bool]:
    if isinstance(statement, (ast.Return, ast.Raise, ast.Break, ast.Continue)):
        return [statement], False
    if isinstance(statement, ast.If):
        if isinstance(statement.test, ast.Constant):
            branch = statement.body if statement.test.value else statement.orelse
            return _walk_block(branch)
        body, body_falls = _walk_block(statement.body)
        other, other_falls = _walk_block(statement.orelse)
        return [statement, *body, *other], body_falls or other_falls
    if isinstance(statement, ast.With):
        body, falls = _walk_block(statement.body)
        return [statement, *body], falls
    if isinstance(statement, ast.Try):
        body, body_falls = _walk_block(statement.body)
        handlers = [_walk_block(handler.body) for handler in statement.handlers]
        final, final_falls = _walk_block(statement.finalbody)
        nodes = [statement, *body]
        for handler_nodes, _handler_falls in handlers:
            nodes.extend(handler_nodes)
        nodes.extend(final)
        handler_falls = any(falls for _nodes, falls in handlers) if handlers else True
        return nodes, final_falls and (body_falls or handler_falls)
    if isinstance(statement, (ast.For, ast.While)):
        # Loop execution/fallthrough is path-dependent. Retain no body evidence;
        # transaction guarantees must be established outside ambiguous loops.
        return [statement], True
    return [statement], True


def _live_text(function: ast.FunctionDef | None) -> str:
    if function is None:
        return ""
    return "\n".join(_statement_text(node) for node in _live_nodes(function.body))


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


def _live_locks(function: ast.FunctionDef | None) -> list[ast.With]:
    if function is None:
        return []
    return [node for node in _live_nodes(function.body) if isinstance(node, ast.With)
            and "_flock(LOCKFILE)" in ast.unparse(node.items[0].context_expr)]


def _transaction_graph(functions: dict[str, ast.FunctionDef]) -> bool:
    run = _live_text(functions.get("run_cutover"))
    build = _live_text(functions.get("_build_cutover"))
    finish = _live_text(functions.get("_finish_exact"))
    return all(token in run for token in (
        "_build_cutover(selection, classes, ownership, _read)",
        "_write_observation(plan['new_text'], _read, _write)",
        "_finish_exact(A, plan['new_text'], backup, observation, _read, _write)",
    )) and "ct.plan_cutover(" in build and "_rollback(" in finish


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
    locks = _live_locks(run)
    lock_text = "\n".join(_live_text_from_block(lock.body) for lock in locks)
    sequence = (
        "current = _read()", "current != A",
        "backup = create_backup(canonical_id, ts, A)",
        "observation = _write_observation(plan['new_text'], _read, _write)",
    )
    positions = [lock_text.find(token) for token in sequence]
    common = all(position >= 0 for position in positions) and positions == sorted(positions)
    if name in {"python-lock-scope-v1", "python-baseline-snapshot-v1",
                "python-prewrite-cas-v1", "python-backup-baseline-v1"}:
        return common
    if name == "python-postwrite-exact-state-v1":
        observe = _live_text(functions.get("_write_observation"))
        finish = _live_text(functions.get("_finish_exact"))
        return all(token in observe for token in ("_write(B)", "observed = _read()")) and all(
            token in finish for token in (
                "if not write_failed and observed == B:",
                "_transaction_result('applied', backup, expected=B, observed=observed)",
            )
        )
    if name in {"python-rollback-after-cas-v1", "python-rollback-exact-baseline-v1"}:
        rollback = functions.get("_rollback")
        text = "\n".join(_live_text_from_block(lock.body) for lock in _live_locks(rollback))
        exact = _live_text(rollback)
        cas = all(token in text for token in (
            "current = _read()", "if current != C:", "_write(A)", "restored = _read()",
        ))
        if name == "python-rollback-after-cas-v1":
            return cas
        return cas and "'rolled-back' if restored == A else 'rollback-failed'" in exact
    return None


def _live_text_from_block(statements: list[ast.stmt]) -> str:
    return "\n".join(_statement_text(node) for node in _live_nodes(statements))
