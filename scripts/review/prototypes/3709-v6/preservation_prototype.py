"""v4 prototype of `python-postwrite-preservation-multiset-v1`.

PROTOTYPE ONLY. This file is committed so that an independent reviewer executes
the SAME artifact the plan claims results for (v3 published a predicate contract
but committed no prototype, so the r2 reviewer had to reimplement it and tested
its own reading instead of the design). It lives under `scripts/review/` and is
NOT imported by any enforcement module; the shipping module named by the plan is
`scripts/enforcement/scheduler_mutation_preservation.py`, which does not exist
yet and must not be created before #3709 is approved and #3711 has landed.

Predicates 1-7 are v3's, re-implemented from the published contract.
Predicates 8-19 are the v4 delta.

Run: python3 scripts/review/prototypes/3709-v4/run.py
"""
from __future__ import annotations

import ast
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "enforcement"))

from scheduler_mutation_python_flow import _statement_text, _walk_block  # noqa: E402

INSPECTED = (
    "plan_cutover", "classify_crontab_lines", "_fallback_records",
    "_rebuild_from_records", "build_cutover_intent", "_abort",
    "_missing_occurrences", "_detail_classifier",
)

PLAN_ASSIGNED = frozenset({
    "classify_detail", "selected_tasks", "roles", "classified",
    "uncataloged", "block", "new_lines", "new_text", "intent",
})

CALLEE_ALLOWLIST = {
    "plan_cutover": frozenset({
        "_detail_classifier", "classify_crontab_lines", "_abort",
        "render_block", "_rebuild_from_records", "build_cutover_intent",
    }),
    "classify_crontab_lines": frozenset({
        "parse_crontab", "_fallback_records", "classify_detail",
    }),
    "_fallback_records": frozenset({"enumerate", "classify_detail"}),
    "_rebuild_from_records": frozenset(),
    "build_cutover_intent": frozenset({"_missing_occurrences", "occurrence_key"}),
    "_abort": frozenset(),
    "_missing_occurrences": frozenset({"Counter"}),
}

GUARDED_NAMES = frozenset(set(INSPECTED) | set().union(*CALLEE_ALLOWLIST.values()))


# --- generic helpers -------------------------------------------------------


def _functions(tree):
    return {n.name: n for n in tree.body if isinstance(n, ast.FunctionDef)}


def _paths(fn):
    return [] if fn is None else _walk_block(fn.body)


def _terminals(fn):
    """[(path_stmts, Return)] or None when some live path does not return."""
    if fn is None:
        return None
    out = []
    for stmts, falls, _locks in _paths(fn):
        if falls or not stmts or not isinstance(stmts[-1], ast.Return):
            return None
        out.append((stmts, stmts[-1]))
    return out


def _texts(stmts):
    return [_statement_text(n) for n in stmts]


def _ordered(texts, steps):
    i = 0
    for step in steps:
        while i < len(texts) and not step(texts[i]):
            i += 1
        if i == len(texts):
            return False
        i += 1
    return True


def _live_nodes(fn):
    seen, out = set(), []
    for stmts, _f, _l in _paths(fn):
        for node in stmts:
            if id(node) not in seen:
                seen.add(id(node))
                out.append(node)
    return out


def _dict_items(node):
    if not isinstance(node, ast.Dict):
        return {}
    return {k.value: v for k, v in zip(node.keys, node.values)
            if isinstance(k, ast.Constant)}


def _call_names(node):
    return {n.func.id for n in ast.walk(node)
            if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)}


def _assigned_names(fn):
    names = set()
    for node in ast.walk(fn):
        targets = []
        if isinstance(node, ast.Assign):
            targets = node.targets
        elif isinstance(node, (ast.AnnAssign, ast.AugAssign)):
            targets = [node.target]
        elif isinstance(node, (ast.For, ast.AsyncFor)):
            targets = [node.target]
        elif isinstance(node, ast.withitem) and node.optional_vars:
            targets = [node.optional_vars]
        for target in targets:
            names |= {t.id for t in ast.walk(target) if isinstance(t, ast.Name)}
    return names


def _comprehension(node, name):
    for stmt in ast.walk(node):
        if (isinstance(stmt, ast.Assign) and len(stmt.targets) == 1
                and isinstance(stmt.targets[0], ast.Name)
                and stmt.targets[0].id == name
                and isinstance(stmt.value, ast.ListComp)):
            return stmt.value
    return None


# --- predicates 1-7 (v3, re-implemented from the published contract) -------


def _p1_plan_cutover_order(fns):
    plan = fns.get("plan_cutover")
    if plan is None:
        return False
    return _ordered(_texts(plan.body), _PLAN_STEPS)


_PLAN_STEPS = (
    lambda t: t == "classify_detail = _detail_classifier(classification_context)",
    lambda t: t == "classified = classify_crontab_lines(current_text, classify_detail)",
    lambda t: (t.startswith("uncataloged = [") and "for r in classified['records']" in t
               and "r['detail']['class'] == 'uncataloged'" in t),
    lambda t: t == "if uncataloged:",
    lambda t: t == "block = render_block(selected_tasks, roles)",
    lambda t: t == ("new_lines = _rebuild_from_records(classified['parsed'], "
                    "classified['records'], block)"),
    lambda t: t == ("intent = build_cutover_intent(classified['records'], "
                    "new_lines, acknowledged)"),
    lambda t: t == "if intent['blocking']:",
)


def _p2_plan_cutover_result_flow(fns):
    plan = fns.get("plan_cutover")
    terminals = _terminals(plan)
    if terminals is None:
        return False
    dicts = [r.value for _s, r in terminals if isinstance(r.value, ast.Dict)]
    if len({ast.unparse(d) for d in dicts}) != 1:
        return False
    items = _dict_items(dicts[0])
    ok = (isinstance(items.get("new_text"), ast.Name) and items["new_text"].id == "new_text"
          and isinstance(items.get("intent"), ast.Name) and items["intent"].id == "intent"
          and isinstance(items.get("abort_reason"), ast.Constant)
          and items["abort_reason"].value is None)
    flows = any(isinstance(n, ast.Assign) and ast.unparse(n.targets[0]) == "new_text"
                and "new_lines" in ast.unparse(n.value) for n in _live_nodes(plan))
    return ok and flows


def _p3_render_block_called_once(fns):
    plan = fns.get("plan_cutover")
    if plan is None:
        return False
    calls = [n for node in _live_nodes(plan) for n in ast.walk(node)
             if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)
             and n.func.id == "render_block"]
    return len({id(c) for c in calls}) == 1


def _inner_append(outer):
    if len(outer.body) != 1 or not isinstance(outer.body[0], ast.For):
        return None
    inner = outer.body[0]
    if "enumerate(parsed[location])" != ast.unparse(inner.iter):
        return None
    appends = [n for n in inner.body if isinstance(n, ast.Expr)
               and isinstance(n.value, ast.Call)
               and ast.unparse(n.value.func).endswith(".append")]
    return (inner, appends[0]) if len(appends) == 1 else None


def _outer_loop(fn):
    for node in ast.walk(fn):
        if (isinstance(node, ast.For)
                and ast.unparse(node.iter) == "('before', 'managed', 'after')"):
            return node
    return None


def _p4_classify_populates_records(fns):
    fn = fns.get("classify_crontab_lines")
    terminals = _terminals(fn)
    if terminals is None:
        return False
    outer = _outer_loop(fn)
    if outer is None or not all(any(n is outer for n in stmts) for stmts, _r in terminals):
        return False
    pair = _inner_append(outer)
    if pair is None:
        return False
    _inner, append = pair
    payload = _dict_items(append.value.args[0]) if append.value.args else {}
    if not {"location", "index", "line", "detail"} <= set(payload):
        return False
    if "classify_detail" not in _call_names(append):
        return False
    appended = ast.unparse(append.value.func).split(".")[0]
    for _stmts, ret in terminals:
        records = _dict_items(ret.value).get("records")
        if not isinstance(records, ast.Name) or records.id not in (appended, "fallback_records"):
            return False
    return True


def _p5_fallback_records_populated(fns):
    fn = fns.get("_fallback_records")
    terminals = _terminals(fn)
    if terminals is None:
        return False
    for _stmts, ret in terminals:
        if isinstance(ret.value, (ast.List, ast.Tuple)) and not ret.value.elts:
            return False
        if isinstance(ret.value, ast.Constant):
            return False
    text = ast.unparse(fn)
    return "classify_detail(" in text and "'unparsed'" in text


def _p6_rebuild_retention(fns):
    fn = fns.get("_rebuild_from_records")
    terminals = _terminals(fn)
    if terminals is None:
        return False
    for name, location in (("before", "before"), ("after", "after")):
        comp = _comprehension(fn, name)
        if comp is None:
            return False
        text = ast.unparse(comp)
        if ("for r in records" not in text or f"r['location'] == '{location}'" not in text
                or "r['detail']['class'] != 'cataloged'" not in text):
            return False
    returns = {ast.unparse(r.value) for _s, r in terminals}
    if returns != {"before + block", "before + block + after"}:
        return False
    for stmts, ret in terminals:
        if ast.unparse(ret.value) != "before + block":
            continue
        if not any(_statement_text(n) == "if parsed['roles'] is None:" for n in stmts):
            return False
    return True


def _p7_intent_derives_blocking(fns):
    fn = fns.get("build_cutover_intent")
    terminals = _terminals(fn)
    if terminals is None:
        return False
    absent, blocking = _comprehension(fn, "absent"), _comprehension(fn, "blocking")
    if absent is None or blocking is None:
        return False
    if "records" not in ast.unparse(absent.generators[0].iter):
        return False
    if ast.unparse(blocking.generators[0].iter) != "absent":
        return False
    conditions = " ".join(ast.unparse(c) for c in blocking.generators[0].ifs)
    if "!= 'ignore'" not in conditions or "not in acknowledged" not in conditions:
        return False
    for _stmts, ret in terminals:
        items = _dict_items(ret.value)
        for key in ("absent", "blocking"):
            if not isinstance(items.get(key), ast.Name) or items[key].id != key:
                return False
    return True


# --- predicates 8-17 (v4 delta) -------------------------------------------


def _p8_terminal_return_closure(fns):
    """Every live terminal return of plan_cutover is `_abort(...)` or THE dict."""
    plan = fns.get("plan_cutover")
    terminals = _terminals(plan)
    if terminals is None:
        return False
    dicts = set()
    for _stmts, ret in terminals:
        value = ret.value
        if isinstance(value, ast.Dict):
            dicts.add(ast.unparse(value))
            continue
        if (isinstance(value, ast.Call) and isinstance(value.func, ast.Name)
                and value.func.id == "_abort"):
            continue
        return False
    return len(dicts) == 1


def _p9_success_path_chain(fns):
    """Every live path returning the success dict traverses the whole chain."""
    plan = fns.get("plan_cutover")
    terminals = _terminals(plan)
    if terminals is None:
        return False
    success = [(s, r) for s, r in terminals if isinstance(r.value, ast.Dict)]
    if not success:
        return False
    for stmts, _ret in success:
        if not _ordered(_texts(stmts), _SUCCESS_STEPS):
            return False
    return True


_SUCCESS_STEPS = (
    _PLAN_STEPS[1],
    lambda t: t == "if classified['error']:",
    _PLAN_STEPS[2],
    _PLAN_STEPS[3],
    _PLAN_STEPS[4],
    _PLAN_STEPS[5],
    lambda t: t.startswith("new_text = ") and "new_lines" in t,
    _PLAN_STEPS[6],
    _PLAN_STEPS[7],
)


def _p10_plan_cutover_binding_closure(fns):
    plan = fns.get("plan_cutover")
    if plan is None or plan.decorator_list:
        return False
    if _assigned_names(plan) != PLAN_ASSIGNED:
        return False
    nested = (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Lambda)
    if any(isinstance(n, nested) for n in ast.walk(plan) if n is not plan):
        return False
    args = plan.args
    return (not args.posonlyargs and [a.arg for a in args.args] ==
            ["current_text", "classification_context"]
            and [a.arg for a in args.kwonlyargs] == ["acknowledged"]
            and args.vararg is None and args.kwarg is None and not args.defaults
            and len(args.kw_defaults) == 1
            and ast.unparse(args.kw_defaults[0]) == "()")


def _module_bound_names(stmt):
    names = set()
    if isinstance(stmt, ast.Assign):
        for target in stmt.targets:
            names |= {n.id for n in ast.walk(target) if isinstance(n, ast.Name)}
    elif isinstance(stmt, (ast.AnnAssign, ast.AugAssign)):
        names |= {n.id for n in ast.walk(stmt.target) if isinstance(n, ast.Name)}
    elif isinstance(stmt, (ast.Import, ast.ImportFrom)):
        names |= {(a.asname or a.name).split(".")[0] for a in stmt.names}
    elif isinstance(stmt, (ast.For, ast.AsyncFor)):
        names |= {n.id for n in ast.walk(stmt.target) if isinstance(n, ast.Name)}
    elif isinstance(stmt, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
        names.add(stmt.name)
    return names


def _p11_module_binding_integrity(tree, fns):
    """No module-level statement may rebind a name defined by a def in this module.

    Imports MAY bind a guarded name (that is how `render_block`, `parse_crontab`
    and `Counter` legitimately arrive) — unless the same name is also defined as a
    top-level function here, which would be a shadowing pair.
    """
    counts, defined = {}, set(fns)
    module_statements = [s for top in tree.body for s in ast.walk(top)
                         if isinstance(s, ast.stmt)
                         and not _inside_function(tree, s)]
    for stmt in module_statements:
        if isinstance(stmt, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            counts[stmt.name] = counts.get(stmt.name, 0) + 1
            if stmt.name in INSPECTED and getattr(stmt, "decorator_list", None):
                return False
            continue
        bound = _module_bound_names(stmt)
        if isinstance(stmt, (ast.Import, ast.ImportFrom)):
            if bound & defined:
                return False
            continue
        if bound & (GUARDED_NAMES | defined):
            return False
    return all(counts.get(name, 0) <= 1 for name in INSPECTED)


def _inside_function(tree, target):
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            continue
        if any(inner is target for inner in ast.walk(node) if inner is not node):
            return True
    return False


def _p12_abort_fails_closed(fns):
    fn = fns.get("_abort")
    terminals = _terminals(fn)
    if terminals is None or not fn.args.args:
        return False
    reason = fn.args.args[0].arg
    for _stmts, ret in terminals:
        if not isinstance(ret.value, ast.Dict):
            return False
        items = _dict_items(ret.value)
        new_text, abort_reason = items.get("new_text"), items.get("abort_reason")
        if not (isinstance(new_text, ast.Constant) and new_text.value is None):
            return False
        if not (isinstance(abort_reason, ast.Name) and abort_reason.id == reason):
            return False
    return True


def _p13_callee_allowlist_closure(fns):
    for name, allowed in CALLEE_ALLOWLIST.items():
        fn = fns.get(name)
        if fn is None:
            return False
        if _call_names(fn) - {"len", "enumerate", "sorted", "list", "set", "str"} - allowed:
            return False
    return True


def _p14_record_loop_bodies_exact(fns):
    outer = _outer_loop(fns.get("classify_crontab_lines")) if fns.get(
        "classify_crontab_lines") else None
    if outer is None or _inner_append(outer) is None:
        return False
    inner, append = _inner_append(outer)
    if len(inner.body) != 1 or inner.body[0] is not append:
        return False
    if any(isinstance(n, (ast.Continue, ast.Break, ast.If, ast.Try, ast.While))
           for n in ast.walk(inner) if n is not inner):
        return False
    fallback = fns.get("_fallback_records")
    loops = [n for n in ast.walk(fallback) if isinstance(n, ast.For)] if fallback else []
    if len(loops) != 1 or len(loops[0].body) != 1:
        return False
    return not any(isinstance(n, (ast.Continue, ast.Break, ast.If))
                   for n in ast.walk(loops[0]) if n is not loops[0])


def _p15_absent_record_is_literal(fns):
    fn = fns.get("build_cutover_intent")
    absent = _comprehension(fn, "absent") if fn else None
    if absent is None or not isinstance(absent.elt, ast.Dict):
        return False
    items = _dict_items(absent.elt)
    variable = absent.generators[0].target
    if not isinstance(variable, ast.Name):
        return False
    expected = {"class": f"{variable.id}['detail']['class']",
                "line": f"{variable.id}['line']",
                "location": f"{variable.id}['location']",
                "index": f"{variable.id}['index']"}
    for key, unparsed in expected.items():
        if key not in items or ast.unparse(items[key]) != unparsed:
            return False
    return not absent.generators[0].ifs


def _p16_missing_occurrences_shape(fns):
    fn = fns.get("_missing_occurrences")
    terminals = _terminals(fn)
    if terminals is None:
        return False
    loops = [n for n in ast.walk(fn) if isinstance(n, ast.For)]
    if len(loops) != 1:
        return False
    loop = loops[0]
    if ast.unparse(loop.iter) != "records" or len(loop.body) != 1:
        return False
    guard = loop.body[0]
    if not isinstance(guard, ast.If) or not guard.orelse:
        return False
    variable = ast.unparse(loop.target)
    if ast.unparse(guard.test) != f"remaining[{variable}['line']] > 0":
        return False
    if len(guard.orelse) != 1 or ast.unparse(guard.orelse[0]) != f"missing.append({variable})":
        return False
    text = ast.unparse(fn)
    if "remaining = Counter(new_lines)" not in text:
        return False
    return all(ast.unparse(r.value) == "missing" for _s, r in terminals)


def _p17_classification_covers_every_line(fns):
    """A totality guard, computed from `current_text` and MODULE marker constants.

    The expected line set must NOT be supplied by the parser: a parser that
    reports live lines as block markers would otherwise pass a self-referential
    reconstruction check while silently dropping them.
    """
    fn = fns.get("classify_crontab_lines")
    terminals = _terminals(fn)
    if terminals is None:
        return False
    guard = "if sorted((r['line'] for r in records)) != sorted(expected):"
    expected = _comprehension(fn, "expected")
    if expected is None or ast.unparse(expected.generators[0].iter) != (
            "current_text.splitlines()"):
        return False
    conditions = " ".join(ast.unparse(c) for c in expected.generators[0].ifs)
    if conditions != "not line.startswith(MARKER_PREFIXES)":
        return False
    clean = [(s, r) for s, r in terminals
             if isinstance(_dict_items(r.value).get("error"), ast.Constant)
             and _dict_items(r.value)["error"].value is None]
    if not clean:
        return False
    for stmts, _ret in clean:
        if not any(_statement_text(n) == guard for n in stmts):
            return False
    for node in ast.walk(fn):
        if isinstance(node, ast.If) and _statement_text(node) == guard:
            if len(node.body) != 1 or not isinstance(node.body[0], ast.Return):
                return False
            error = _dict_items(node.body[0].value).get("error")
            return isinstance(error, ast.Constant) and isinstance(error.value, str)
    return False


def _p18_marker_prefixes_are_literal(tree, fns):
    """The exclusion set of predicate 17 must be a pinned module-level literal.

    Without this, the guard is still bypassable: name a live cron line in
    MARKER_PREFIXES and it disappears from the expected set, which is exactly how
    case E12 defeated the parser-supplied form of the same guard.
    """
    for stmt in tree.body:
        if not isinstance(stmt, ast.Assign) or len(stmt.targets) != 1:
            continue
        if getattr(stmt.targets[0], "id", None) != "MARKER_PREFIXES":
            continue
        return ast.unparse(stmt.value) == MARKER_PREFIXES_LITERAL
    return False


def _p19_managed_absence_always_blocks(fns):
    """A managed-block line that the new block does not reproduce must ALWAYS block.

    Managed records are unconditionally dropped by the rebuild, so the intent report
    is their only protection - and exempting class `ignore` hands an evader a silent
    delete (case E13). The `ignore` exemption stays for `before`/`after`, where the
    rebuild retains the line anyway.
    """
    fn = fns.get("build_cutover_intent")
    blocking = _comprehension(fn, "blocking") if fn else None
    if blocking is None:
        return False
    variable = blocking.generators[0].target
    if not isinstance(variable, ast.Name):
        return False
    conditions = [ast.unparse(c) for c in blocking.generators[0].ifs]
    exemption = (f"{variable.id}['class'] != 'ignore' or "
                 f"{variable.id}['location'] == 'managed'")
    return any(exemption in condition for condition in conditions)


MARKER_PREFIXES_LITERAL = (
    "('# >>> workspace-hub managed', '# <<< workspace-hub managed')"
)

NAMED_PREDICATES = (
    ("plan-cutover-order", _p1_plan_cutover_order),
    ("plan-cutover-result-flow", _p2_plan_cutover_result_flow),
    ("render-block-called-once", _p3_render_block_called_once),
    ("classify-populates-records", _p4_classify_populates_records),
    ("fallback-records-populated", _p5_fallback_records_populated),
    ("rebuild-retention", _p6_rebuild_retention),
    ("intent-derives-blocking", _p7_intent_derives_blocking),
    ("plan-cutover-terminal-return-closure", _p8_terminal_return_closure),
    ("plan-cutover-success-path-chain", _p9_success_path_chain),
    ("plan-cutover-binding-closure", _p10_plan_cutover_binding_closure),
    ("module-binding-integrity", None),
    ("abort-fails-closed", _p12_abort_fails_closed),
    ("callee-allowlist-closure", _p13_callee_allowlist_closure),
    ("record-loop-bodies-exact", _p14_record_loop_bodies_exact),
    ("absent-record-is-literal", _p15_absent_record_is_literal),
    ("missing-occurrences-shape", _p16_missing_occurrences_shape),
    ("classification-covers-every-line", _p17_classification_covers_every_line),
    ("marker-prefixes-are-literal", None),
    ("managed-absence-always-blocks", _p19_managed_absence_always_blocks),
)

V3_PREDICATES = frozenset(name for name, _p in NAMED_PREDICATES[:7])


def evaluate(source: str) -> dict[str, bool]:
    """Return {predicate name: bool}. Any exception is a False, fail-closed."""
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return {name: False for name, _p in NAMED_PREDICATES}
    fns = _functions(tree)
    results = {}
    for name, predicate in NAMED_PREDICATES:
        try:
            if name == "module-binding-integrity":
                results[name] = bool(_p11_module_binding_integrity(tree, fns))
            elif name == "marker-prefixes-are-literal":
                results[name] = bool(_p18_marker_prefixes_are_literal(tree, fns))
            else:
                results[name] = bool(predicate(fns))
        except Exception:
            results[name] = False
    return results


def preservation_shape(source: str) -> bool:
    return all(evaluate(source).values())


def v3_shape(source: str) -> bool:
    return all(v for k, v in evaluate(source).items() if k in V3_PREDICATES)
