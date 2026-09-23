"""Prototype for v6 Layer 3: behavioural-test-present-and-pinned.

This is a parse-only model of the future enforcement conjunct. It proves the
specific v5 bypass is closed without executing the indexed test blob.

Run:
    python3 scripts/review/prototypes/3709-v6/s1_integrity.py --check
"""
from __future__ import annotations

import ast
import sys

PINNED_SCENARIOS = ("A", "B", "C", "D", "ace1", "ace2")
PINNED_EXPECTED = {
    "reference": ("ABORTS", "SUCCEEDS, no loss", "ABORTS", "SUCCEEDS, no loss"),
    "z07_r01_intent_blocking_cleared": (
        "DROPS 4/5 LIVE LINES", "DROPS 4/5 LIVE LINES",
        "DROPS 4/5 LIVE LINES", "DROPS 4/5 LIVE LINES",
    ),
    "z10_new_text_dedupes": ("ABORTS", "SUCCEEDS, no loss", "ABORTS", "DROPS 1/5 LIVE LINES"),
}

REFERENCE = '''
from collections import Counter
import pytest

SCENARIOS = ("A", "B", "C", "D", "ace1", "ace2")
EXPECTED_SHAPE_VERDICTS = {
    "reference": ("ABORTS", "SUCCEEDS, no loss", "ABORTS", "SUCCEEDS, no loss"),
    "z07_r01_intent_blocking_cleared": (
        "DROPS 4/5 LIVE LINES", "DROPS 4/5 LIVE LINES",
        "DROPS 4/5 LIVE LINES", "DROPS 4/5 LIVE LINES",
    ),
    "z10_new_text_dedupes": ("ABORTS", "SUCCEEDS, no loss", "ABORTS", "DROPS 1/5 LIVE LINES"),
}


def preservation_holds(plan, crontab):
    if not isinstance(plan, dict):
        return False
    if plan.get("abort_reason") is not None:
        return plan.get("new_text") is None
    have = Counter((plan.get("new_text") or "").split("\\n"))
    want = Counter(live_lines(crontab))
    return all(have[line] >= count for line, count in want.items())


@pytest.mark.parametrize("scenario", SCENARIOS)
def test_plan_cutover_never_loses_a_live_line_without_aborting(scenario):
    plan, crontab = run_plan_cutover(scenario)
    assert preservation_holds(plan, crontab)


def test_preservation_invariant_discriminates_over_the_shape_corpus():
    assert measured_shape_verdicts() == EXPECTED_SHAPE_VERDICTS


def test_preservation_shape_fixtures_are_inert():
    assert shape_fixtures_are_inert()
'''

TEST_NAMES = {
    "test_plan_cutover_never_loses_a_live_line_without_aborting",
    "test_preservation_invariant_discriminates_over_the_shape_corpus",
    "test_preservation_shape_fixtures_are_inert",
}
DISABLING_MARKS = {"skip", "skipif", "xfail"}
DISABLING_CALLS = {
    "pytest.skip", "pytest.xfail", "pytest.importorskip",
    "unittest.skip", "unittest.skipIf", "unittest.skipUnless",
}


def dotted(node: ast.AST) -> str | None:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        base = dotted(node.value)
        return f"{base}.{node.attr}" if base else node.attr
    return None


def mark_name(node: ast.AST) -> str | None:
    if isinstance(node, ast.Call):
        node = node.func
    name = dotted(node)
    if not name:
        return None
    parts = name.split(".")
    if len(parts) >= 3 and parts[-3:-1] == ["pytest", "mark"]:
        return parts[-1]
    if len(parts) >= 2 and parts[-2:] == ["mark", "parametrize"]:
        return "parametrize"
    return parts[-1]


def literal(node: ast.AST):
    try:
        return ast.literal_eval(node)
    except Exception:  # noqa: BLE001 - parse-only prototype
        return None


def assigned_literal(module: ast.Module, name: str):
    for stmt in module.body:
        if isinstance(stmt, ast.Assign):
            if any(isinstance(t, ast.Name) and t.id == name for t in stmt.targets):
                return literal(stmt.value)
    return None


def module_has_disabling_pytestmark(module: ast.Module) -> bool:
    for stmt in module.body:
        if not isinstance(stmt, ast.Assign):
            continue
        if not any(isinstance(t, ast.Name) and t.id == "pytestmark" for t in stmt.targets):
            continue
        values = stmt.value.elts if isinstance(stmt.value, (ast.List, ast.Tuple)) else [stmt.value]
        if any((mark_name(value) or "") in DISABLING_MARKS for value in values):
            return True
    return False


def function_has_required_parametrize(fn: ast.FunctionDef) -> bool:
    if fn.name != "test_plan_cutover_never_loses_a_live_line_without_aborting":
        return True
    for dec in fn.decorator_list:
        if mark_name(dec) == "parametrize" and isinstance(dec, ast.Call) and len(dec.args) >= 2:
            arg0 = literal(dec.args[0])
            arg1 = assigned_literal(ast.Module(body=[], type_ignores=[]), "unused")
            if isinstance(dec.args[1], ast.Name) and dec.args[1].id == "SCENARIOS":
                arg1 = PINNED_SCENARIOS
            else:
                arg1 = literal(dec.args[1])
            if arg0 == "scenario" and tuple(arg1 or ()) == PINNED_SCENARIOS:
                return True
    return False


def integrity_ok(source: str) -> tuple[bool, str]:
    try:
        module = ast.parse(source)
    except SyntaxError as error:
        return False, f"syntax error: {error}"
    if module_has_disabling_pytestmark(module):
        return False, "module-level disabling pytestmark"
    scenarios = assigned_literal(module, "SCENARIOS")
    if tuple(scenarios or ()) != PINNED_SCENARIOS:
        return False, "scenario list changed"
    expected = assigned_literal(module, "EXPECTED_SHAPE_VERDICTS")
    if expected != PINNED_EXPECTED:
        return False, "shape expectation values changed"
    functions = {n.name: n for n in module.body if isinstance(n, ast.FunctionDef)}
    if set(functions) & TEST_NAMES != TEST_NAMES:
        return False, "missing pinned test function"
    helper = functions.get("preservation_holds")
    if helper is None:
        return False, "missing preservation_holds"
    helper_text = ast.unparse(helper)
    for token in ("Counter", "abort_reason", "new_text", "live_lines", ">= count"):
        if token not in helper_text:
            return False, f"preservation_holds missing {token}"
    for fn in functions.values():
        if fn.name not in TEST_NAMES:
            continue
        for dec in fn.decorator_list:
            name = mark_name(dec)
            if name in DISABLING_MARKS:
                return False, f"{fn.name} has disabling decorator {name}"
            if name != "parametrize" and fn.name in TEST_NAMES:
                return False, f"{fn.name} has unapproved decorator {name}"
        if not function_has_required_parametrize(fn):
            return False, "P1 parametrize is not pinned"
        for node in ast.walk(fn):
            if isinstance(node, ast.Return):
                return False, f"{fn.name} has early return"
            if isinstance(node, ast.Call) and dotted(node.func) in DISABLING_CALLS:
                return False, f"{fn.name} calls {dotted(node.func)}"
    return True, "accepted"


MUTANTS = {
    "s1_module_pytestmark_skip": REFERENCE.replace(
        "import pytest\n", "import pytest\npytestmark = pytest.mark.skip('disabled')\n", 1),
    "s1_module_pytestmark_skipif": REFERENCE.replace(
        "import pytest\n", "import pytest\npytestmark = pytest.mark.skipif(True, reason='disabled')\n", 1),
    "s1_module_pytestmark_xfail": REFERENCE.replace(
        "import pytest\n", "import pytest\npytestmark = pytest.mark.xfail(reason='disabled')\n", 1),
    "s1_per_test_skip_decorator": REFERENCE.replace(
        '@pytest.mark.parametrize("scenario", SCENARIOS)\n',
        '@pytest.mark.skip(reason="disabled")\n@pytest.mark.parametrize("scenario", SCENARIOS)\n', 1),
    "s1_per_test_skipif_decorator": REFERENCE.replace(
        '@pytest.mark.parametrize("scenario", SCENARIOS)\n',
        '@pytest.mark.skipif(True, reason="disabled")\n@pytest.mark.parametrize("scenario", SCENARIOS)\n', 1),
    "s1_per_test_xfail_decorator": REFERENCE.replace(
        '@pytest.mark.parametrize("scenario", SCENARIOS)\n',
        '@pytest.mark.xfail(reason="disabled")\n@pytest.mark.parametrize("scenario", SCENARIOS)\n', 1),
    "s1_body_pytest_skip": REFERENCE.replace(
        'def test_plan_cutover_never_loses_a_live_line_without_aborting(scenario):\n',
        'def test_plan_cutover_never_loses_a_live_line_without_aborting(scenario):\n    pytest.skip("disabled")\n', 1),
    "s1_body_pytest_xfail": REFERENCE.replace(
        'def test_plan_cutover_never_loses_a_live_line_without_aborting(scenario):\n',
        'def test_plan_cutover_never_loses_a_live_line_without_aborting(scenario):\n    pytest.xfail("disabled")\n', 1),
    "s1_body_early_return": REFERENCE.replace(
        'def test_plan_cutover_never_loses_a_live_line_without_aborting(scenario):\n',
        'def test_plan_cutover_never_loses_a_live_line_without_aborting(scenario):\n    return\n', 1),
    "s1_expectation_table_value_tamper": REFERENCE.replace(
        '"z10_new_text_dedupes": ("ABORTS", "SUCCEEDS, no loss", "ABORTS", "DROPS 1/5 LIVE LINES")',
        '"z10_new_text_dedupes": ("ABORTS", "SUCCEEDS, no loss", "ABORTS", "SUCCEEDS, no loss")', 1),
}


def main(argv: list[str]) -> int:
    failures = []
    ok, reason = integrity_ok(REFERENCE)
    print(f"reference {'ACCEPT' if ok else 'REJECT'}: {reason}")
    if not ok:
        failures.append("reference rejected")
    for name, source in MUTANTS.items():
        ok, reason = integrity_ok(source)
        verdict = "ACCEPT" if ok else "REJECT"
        print(f"{name:36s} {verdict:6s} {reason}")
        if ok:
            failures.append(f"{name} accepted")
    print(f"mutants: {len(MUTANTS)}")
    for failure in failures:
        print(f"FAIL: {failure}")
    return 1 if failures and "--check" in argv else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
