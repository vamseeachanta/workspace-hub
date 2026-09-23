"""Execute each case against two synthetic crontabs and report data loss.

v5 promotes this harness to the PRIMARY control. `preservation_holds` is the
exact invariant the shipping pytest suite will assert against the COMMITTED
`scripts/cron/cron_transaction.py`; it detects by OUTCOME, so it needs no
advance knowledge of the evasion shape. The AST predicate columns are retained
as the demoted defence-in-depth signal.

Nothing here executes staged git-index blobs, and nothing here is imported by
`check-scheduler-mutation-surfaces.py`. The shape corpus under `cases/` is
executed only by this harness / by pytest, against stub collaborators, never
against a real crontab.

Scenario A carries an uncataloged managed-block line, so the honest shape must
ABORT (this is #3709's defect, reproduced). Scenario B carries none, so the
honest shape must SUCCEED while losing nothing; it is the scenario in which a
silent-drop evasion becomes visible.

    python3 scripts/review/prototypes/3709-v4/behaviour.py
"""
from __future__ import annotations

import hashlib
import re
import sys
from collections import Counter
from pathlib import Path

CASES = Path(__file__).resolve().parent / "cases"

MARKER_BEGIN = "# >>> workspace-hub managed >>>"
MARKER_END = "# <<< workspace-hub managed <<<"
THIRD_PARTY = "0 1 * * * /usr/bin/thirdparty --run"

SCENARIO_A = "\n".join([
    "MAILTO=ops@example.com", THIRD_PARTY, MARKER_BEGIN,
    "0 2 * * * run-managed-a", "0 9 * * * run-orphan-b", MARKER_END,
    "0 4 * * * /usr/bin/after --run",
])
SCENARIO_B = "\n".join([
    "MAILTO=ops@example.com", "# nightly ops note", THIRD_PARTY, MARKER_BEGIN,
    "0 2 * * * run-managed-a", MARKER_END, "0 4 * * * /usr/bin/after --run",
])
# Scenarios C and D reproduce the ace1 fixture's DUPLICATE-LINE property: the
# README records the notification-purge line at both (managed,31) and (after,7),
# and the deckhand line at both (after,1) and (after,8). A membership test
# ("is this line still somewhere in new_text?") cannot see one of two identical
# occurrences being destroyed; only a multiset comparison can.
#
#   C: the duplicate is CATALOGED and spans managed+after -> the rebuild drops the
#      `after` copy and the block emits one; the honest shape must ABORT.
#   D: the duplicate is a PRESERVED_EXTERNAL third-party line spanning before+after
#      -> the rebuild retains both; the honest shape must SUCCEED losing nothing.
DUP_MANAGED = "0 2 * * * run-managed-a"
SCENARIO_C = "\n".join([
    "MAILTO=ops@example.com", THIRD_PARTY, MARKER_BEGIN,
    DUP_MANAGED, MARKER_END, DUP_MANAGED, "0 4 * * * /usr/bin/after --run",
])
SCENARIO_D = "\n".join([
    "MAILTO=ops@example.com", THIRD_PARTY, MARKER_BEGIN,
    DUP_MANAGED, MARKER_END, THIRD_PARTY, "0 4 * * * /usr/bin/after --run",
])
SCENARIOS = (("A", SCENARIO_A), ("B", SCENARIO_B), ("C", SCENARIO_C), ("D", SCENARIO_D))

CATALOG = ["run-managed-a"]
EXTERNAL = ["/usr/bin/thirdparty", "/usr/bin/after"]


def _split(current_text):
    lines = current_text.split("\n")
    if MARKER_BEGIN not in lines:
        return {"before": lines, "managed": [], "after": [], "markers": [],
                "roles": None, "error": None}
    begin, end = lines.index(MARKER_BEGIN), lines.index(MARKER_END)
    return {"before": lines[:begin], "managed": lines[begin + 1:end],
            "after": lines[end + 1:], "markers": [lines[begin], lines[end]],
            "roles": ["control-plane"], "error": None}


def parse_crontab(current_text):
    return _split(current_text)


def mispartitioning_parse_crontab(current_text):
    """R03: every line lands in `before`; managed and after are emptied."""
    parsed = _split(current_text)
    return dict(parsed, before=[line for line in current_text.split("\n")
                                if line not in (MARKER_BEGIN, MARKER_END)],
                managed=[], after=[])


def _steal(parsed):
    return {key: [line for line in value if line != THIRD_PARTY]
            if key in ("before", "managed", "after") else value
            for key, value in parsed.items()}


def marker_thieving_parse_crontab(current_text):
    """E11: reports a live third-party line as a block marker and drops it."""
    parsed = _steal(_split(current_text))
    return dict(parsed, markers=[MARKER_BEGIN, MARKER_END, THIRD_PARTY])


def colluding_parse_crontab(current_text):
    """E12: steals THIRD_PARTY and re-injects the real begin marker as a plain line.

    Paired with an MARKER_PREFIXES entry naming the same line, the stolen line is
    missing from BOTH sides of the totality reconciliation, and the re-injected
    marker keeps the two sides equal.
    """
    parsed = _steal(_split(current_text))
    return dict(parsed, before=parsed["before"] + [MARKER_BEGIN], markers=[MARKER_END])


def classify_line_detail(line, catalog_commands, external_fingerprints, **kwargs):
    if not line.strip() or line.startswith("#") or re.match(r"^[A-Z_]+=", line):
        return {"class": "ignore", "reason": "env-or-comment"}
    if any(command in line for command in catalog_commands):
        return {"class": "cataloged", "reason": "canonical-exact-line"}
    if any(fingerprint in line for fingerprint in external_fingerprints):
        return {"class": "preserved_external", "reason": "third-party-fingerprint"}
    return {"class": "uncataloged", "reason": None}


def render_block(selected_tasks, roles):
    return [MARKER_BEGIN] + [task["line"] for task in selected_tasks] + [MARKER_END]


def occurrence_key(record):
    payload = f"{record['location']}|{record['index']}|{record['line']}"
    return hashlib.sha256(payload.encode()).hexdigest()[:16]


def _absence(record):
    """E09's uninspected helper: reports every absence as class `ignore`."""
    return dict(record, **{"class": "ignore", "reason": None,
                           "key": occurrence_key(record)})


def _empty_classification(current_text, classify_detail):
    return {"parsed": {"roles": None, "markers": []}, "records": [], "error": None}


def _managed_only(current_text):
    """E07's context-supplied planner."""
    return {"new_text": "\n".join(render_block(CONTEXT["selected_tasks"], [])),
            "preserved": [], "uncataloged": [], "conflicts": [],
            "intent": {"absent": [], "added": [], "blocking": []}, "abort_reason": None}


CONTEXT = {
    "catalog_commands": CATALOG, "external_fingerprints": EXTERNAL,
    "selected_task_ids": {"managed-a"}, "catalog_fingerprints": [],
    "ownership": {}, "selected_tasks": [{"line": "0 2 * * * run-managed-a"}],
    "roles": ["control-plane"], "planner": _managed_only, "fast_path": True,
}

STUBS = {name: value for name, value in list(globals().items())
         if name in {
             "parse_crontab", "mispartitioning_parse_crontab", "colluding_parse_crontab",
             "marker_thieving_parse_crontab", "classify_line_detail", "render_block",
             "occurrence_key", "_absence", "Counter", "_empty_classification",
         }}


def _rewrite_imports(source):
    """Bind `from cron_x import a as b` to the stub `a`, preserving the alias.

    Stripping these lines outright would silently restore the honest stub for
    every case whose evasion IS the alias (E11, E12, R03).
    """
    out = []
    for line in source.split("\n"):
        if line.startswith("from collections"):
            continue
        if line.startswith("from cron"):
            _head, _sep, names = line.partition(" import ")
            for item in names.split(", "):
                origin, _as, alias = item.strip().partition(" as ")
                out.append(f"{alias or origin} = {origin}")
            continue
        out.append(line)
    return "\n".join(out)


def _run(source, crontab):
    namespace = dict(STUBS)
    exec(compile(_rewrite_imports(source), "<case>", "exec"), namespace)  # noqa: S102
    return namespace["plan_cutover"](crontab, dict(CONTEXT))


def live_lines(crontab):
    return [line for line in crontab.split("\n")
            if line not in (MARKER_BEGIN, MARKER_END)]


def preservation_holds(plan, crontab):
    """THE INVARIANT. Returns (ok, detail).

    A plan is preservation-safe iff it either fails closed (`abort_reason` is
    non-null AND `new_text` is None), or its `new_text` reproduces every live
    input line with at least the multiplicity the input carried. Multiset, not
    membership: two identical live lines collapsing into one is data loss.

    This is the whole primary control. It makes no reference to the shape of the
    implementation, so a novel evasion needs no new predicate to be caught.
    """
    if not isinstance(plan, dict):
        return False, f"returned {type(plan).__name__}, not a plan"
    if plan.get("abort_reason") is not None:
        if plan.get("new_text") is not None:
            return False, "aborted but still emitted new_text"
        return True, "ABORTS"
    have = Counter((plan.get("new_text") or "").split("\n"))
    want = Counter(live_lines(crontab))
    lost = sum(max(0, count - have[line]) for line, count in want.items())
    if lost:
        return False, f"DROPS {lost}/{sum(want.values())} LIVE LINES"
    return True, "SUCCEEDS, no loss"


def verdict(source, crontab):
    try:
        plan = _run(source, crontab)
    except Exception as error:  # noqa: BLE001
        return f"raised {type(error).__name__}"
    return preservation_holds(plan, crontab)[1]


# The committed contract of this harness: what each shape does on each scenario.
# `--check` exits non-zero on any drift, so a later edit cannot quietly turn a
# destructive row safe, or the reference into a destructive shape.
ABORT, SAFE = "ABORTS", "SUCCEEDS, no loss"
EXPECTED = {
    "e01_nested_abort": ("DROPS 5/5 LIVE LINES", SAFE, "DROPS 5/5 LIVE LINES", SAFE),
    "e02_module_rebind": (ABORT, SAFE, "DROPS 1/5 LIVE LINES", SAFE),
    "e03_inbody_rebind": ("DROPS 4/5 LIVE LINES", "DROPS 4/5 LIVE LINES", "DROPS 4/5 LIVE LINES", "DROPS 4/5 LIVE LINES"),
    "e04_abort_returns_success": ("DROPS 5/5 LIVE LINES", SAFE, "DROPS 5/5 LIVE LINES", SAFE),
    "e05_continue_skip": (ABORT, ABORT, ABORT, SAFE),
    "e06_second_success_dict": (ABORT, "DROPS 5/5 LIVE LINES", "DROPS 5/5 LIVE LINES", "DROPS 5/5 LIVE LINES"),
    "e07_context_callable": ("DROPS 4/5 LIVE LINES", "DROPS 4/5 LIVE LINES", "DROPS 4/5 LIVE LINES", "DROPS 4/5 LIVE LINES"),
    "e08_decorator": ("DROPS 5/5 LIVE LINES", "DROPS 5/5 LIVE LINES", "DROPS 5/5 LIVE LINES", "DROPS 5/5 LIVE LINES"),
    "e09_intent_helper_lie": (ABORT, SAFE, "DROPS 1/5 LIVE LINES", SAFE),
    "e10_no_totality_guard": (ABORT, SAFE, ABORT, SAFE),
    "e11_parser_marker_theft": (ABORT, ABORT, ABORT, ABORT),
    "e12_marker_collusion": (ABORT, "DROPS 1/5 LIVE LINES", ABORT, "DROPS 2/5 LIVE LINES"),
    "e13_managed_line_reported_ignore": (ABORT, SAFE, SAFE, SAFE),
    "e14_ignore_exempts_managed": ("DROPS 1/5 LIVE LINES", SAFE, SAFE, SAFE),
    "mx1_v3_counterexample": ("DROPS 4/5 LIVE LINES", "DROPS 4/5 LIVE LINES", "DROPS 4/5 LIVE LINES", "DROPS 4/5 LIVE LINES"),
    "mx2_v4_delegation": ("DROPS 5/5 LIVE LINES", "DROPS 5/5 LIVE LINES", "DROPS 5/5 LIVE LINES", "DROPS 5/5 LIVE LINES"),
    "r01_detail_classifier_constant": (ABORT, ABORT, ABORT, ABORT),
    "r03_parse_mispartitions": (ABORT, SAFE, ABORT, SAFE),
    "reference": (ABORT, SAFE, ABORT, SAFE),
    "z07_r01_intent_blocking_cleared": ("DROPS 4/5 LIVE LINES", "DROPS 4/5 LIVE LINES", "DROPS 4/5 LIVE LINES", "DROPS 4/5 LIVE LINES"),
    "z08_no_guard_plus_marker_theft": (ABORT, "DROPS 1/5 LIVE LINES", ABORT, "DROPS 2/5 LIVE LINES"),
    "z09_no_guard_plus_mispartition": (ABORT, SAFE, ABORT, SAFE),
    "z10_new_text_dedupes": (ABORT, SAFE, ABORT, "DROPS 1/5 LIVE LINES"),
}


def _destructive(verdicts):
    return any(v.startswith("DROPS") for v in verdicts)


def _row(label, source, v3, v4):
    verdicts = tuple(verdict(source, text) for _name, text in SCENARIOS)
    print(f"{label:34s} {str(v3):6s} {str(v4):6s} "
          + "  ".join(f"{v:22s}" for v in verdicts))
    return verdicts


def main(argv=()):
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from mutations import NAMED_MUTATIONS, apply  # noqa: PLC0415
    from preservation_prototype import evaluate, v3_shape  # noqa: PLC0415

    failures, accepted_destructive = [], []
    header = "  ".join(f"{name:22s}" for name, _ in SCENARIOS)
    print(f"{'case':34s} {'v3':6s} {'v4':6s} {header}")
    print("-" * 148)
    for path in sorted(CASES.glob("*.py")):
        source = path.read_text()
        v4 = all(evaluate(source).values())
        verdicts = _row(path.stem, source, v3_shape(source), v4)
        if path.stem not in EXPECTED:
            failures.append(f"{path.stem}: no EXPECTED entry")
        elif EXPECTED[path.stem] != verdicts:
            failures.append(f"{path.stem}: expected {EXPECTED[path.stem]}, measured {verdicts}")
        if v4 and _destructive(verdicts):
            accepted_destructive.append(path.stem)

    print()
    print(f"{'v3 textual mutation':34s} {'v3':6s} {'v4':6s} {header}")
    print("-" * 148)
    for mutation in NAMED_MUTATIONS:
        source = apply(mutation)
        v4 = all(evaluate(source).values())
        verdicts = _row(mutation[0], source, v3_shape(source), v4)
        if v4 and _destructive(verdicts):
            accepted_destructive.append(mutation[0])

    print()
    print("honest expectation:  A ABORTS   B no loss   C ABORTS   D no loss")
    print(f"predicate-ACCEPTED and DESTRUCTIVE: {accepted_destructive or 'none'}")
    for line in failures:
        print(f"FAIL: {line}")
    return 1 if failures and "--check" in argv else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
