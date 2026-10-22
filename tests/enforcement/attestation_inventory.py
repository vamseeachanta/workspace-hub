"""Conservative AST inventory of enforcement attestation test entrypoints.

All direct attestation evaluators and source-pin references are included, plus
their local callers. Unpinned structural cases remain explicit audit rows.
"""
from __future__ import annotations

import ast

ENTRYPOINTS = {
    "evaluate_attestation", "evaluate_wrapper_attestation", "wrapper_attestation_reason",
    "_pinned", "assert_semantic_rejection", "_run_gate",
}
PIN_TABLES = {"WRAPPER_SHA256"}


def discover_attestation_tests(directory):
    found = set()
    for path in sorted(directory.rglob("test_*.py")):
        tree = ast.parse(path.read_text())
        functions = {node.name: node for node in ast.walk(tree)
                     if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))}
        dependencies = {}
        relevant = set()
        for name, node in functions.items():
            names = {part.id if isinstance(part, ast.Name) else part.attr
                     for part in ast.walk(node) if isinstance(part, (ast.Name, ast.Attribute))}
            dependencies[name] = names & functions.keys()
            if names & (ENTRYPOINTS | PIN_TABLES):
                relevant.add(name)
        while True:
            expanded = relevant | {name for name, deps in dependencies.items() if deps & relevant}
            if expanded == relevant:
                break
            relevant = expanded
        relative = "tests/enforcement/" + path.relative_to(directory).as_posix()
        found.update(f"{relative}::{name}" for name in relevant if name.startswith("test_"))
    return found
