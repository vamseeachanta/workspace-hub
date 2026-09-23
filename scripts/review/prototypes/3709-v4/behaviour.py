"""Execute each case against two synthetic crontabs and report data loss.

The attestation is a syntactic predicate; this harness measures the SEMANTIC
property that matters — "no live crontab line is dropped without an abort" — so a
shape the predicate set still ACCEPTS can be reported as destructive or not
destructive on evidence rather than on argument.

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


def verdict(source, crontab):
    live = [line for line in crontab.split("\n")
            if line not in (MARKER_BEGIN, MARKER_END)]
    try:
        plan = _run(source, crontab)
    except Exception as error:  # noqa: BLE001
        return f"raised {type(error).__name__}"
    if not isinstance(plan, dict):
        return f"returned {type(plan).__name__}, not a plan"
    if plan.get("abort_reason") is not None:
        return "ABORTS"
    lost = [line for line in live if line not in (plan.get("new_text") or "").split("\n")]
    return "SUCCEEDS, no loss" if not lost else f"DROPS {len(lost)}/{len(live)} LIVE LINES"


def main():
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from preservation_prototype import evaluate, v3_shape  # noqa: PLC0415

    print(f"{'case':36s} {'v3':6s} {'v4':6s} {'A (orphan present)':28s} B (clean crontab)")
    print("-" * 118)
    for path in sorted(CASES.glob("*.py")):
        source = path.read_text()
        print(f"{path.stem:36s} {str(v3_shape(source)):6s} "
              f"{str(all(evaluate(source).values())):6s} "
              f"{verdict(source, SCENARIO_A):28s} {verdict(source, SCENARIO_B)}")
    print()
    print("honest expectation:  A -> ABORTS (run-orphan-b is uncataloged)   "
          "B -> SUCCEEDS, no loss")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
