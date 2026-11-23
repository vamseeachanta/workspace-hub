"""Regenerate every derived case in `cases/` from `cases/reference.py`.

Each case is a named, minimal delta on the honest reference, so a reviewer can
diff it rather than re-read a whole module. `cases/reference.py` and
`cases/mx1_v3_counterexample.py` are hand-written and are never rewritten.

    python3 scripts/review/prototypes/3709-v4/make_cases.py
"""
from __future__ import annotations

from pathlib import Path

CASES = Path(__file__).resolve().parent / "cases"
REFERENCE = (CASES / "reference.py").read_text()
PRE = REFERENCE[REFERENCE.index("from collections"):REFERENCE.index("def plan_cutover(")]
PLAN = REFERENCE[REFERENCE.index("def plan_cutover("):]

CLASSIFIER = """    def classify_detail(line):
        return classify_line_detail(
            line,
            classification_context['catalog_commands'],
            classification_context['external_fingerprints'],
            selected_task_ids=classification_context['selected_task_ids'],
            catalog_fingerprints=classification_context['catalog_fingerprints'],
            ownership_context=classification_context['ownership'],
        )
    return classify_detail"""

GUARD = """    expected = [line for line in current_text.splitlines()
                if not line.startswith(MARKER_PREFIXES)]
    if sorted(r['line'] for r in records) != sorted(expected):
        return {'parsed': parsed, 'records': records,
                'error': 'classification did not cover every live line'}
"""

MISSING = """def _missing_occurrences(records, new_lines):
    remaining = Counter(new_lines)
    missing = []
    for record in records:
        if remaining[record['line']] > 0:
            remaining[record['line']] -= 1
        else:
            missing.append(record)
    return missing"""

ABSENT = """    absent = [{'location': r['location'], 'index': r['index'], 'line': r['line'],
               'class': r['detail']['class'], 'reason': r['detail']['reason'],
               'key': occurrence_key(r)}
              for r in _missing_occurrences(records, new_lines)]"""


def write(name, title, why, body):
    (CASES / f"{name}.py").write_text(f'# ruff: noqa\n"""{title}\n\n{why}\n"""\n' + body)


def plan_with(anchor, insertion):
    return PLAN.replace(anchor, insertion + anchor, 1)


def build():
    write("mx2_v4_delegation",
          "MX2 - the v3-r2 reviewer's delegation counter-example, verbatim.",
          "A non-constant early return calls an UNINSPECTED helper that returns only the managed\n"
          "block with an empty intent report. The compliant classification/rebuild/intent pipeline\n"
          "remains later in the function, so every v3 predicate still sees what it expects.\n"
          "Source: scripts/review/results/2026-07-30-plan-3709-v3-codex-r2.md, Finding 1.",
          PRE + """def _success_managed_only(classification_context):
    block = ['# >>> workspace-hub managed ...', '0 * * * * run-managed',
             '# <<< workspace-hub managed <<<']
    return {'new_text': '\\n'.join(block), 'preserved': [], 'uncataloged': [],
            'intent': {'absent': [], 'added': [], 'blocking': []}, 'abort_reason': None}


""" + plan_with(
              "    classify_detail = _detail_classifier(classification_context)",
              "    if classification_context:\n"
              "        return _success_managed_only(classification_context)\n"))

    write("e01_nested_abort",
          "E01 - a nested `def _abort` shadows the inspected module-level one.",
          "`_walk_block` skips FunctionDef statements, so a nested def is invisible to every path\n"
          "predicate, and `_abort` is on the callee allowlist. The shadow reports abort_reason=None,\n"
          "so every abort is read as a clean plan by run_cutover.",
          PRE + plan_with(
              "    classify_detail = _detail_classifier(classification_context)",
              "    def _abort(reason, uncataloged, intent):\n"
              "        return {'new_text': '', 'preserved': [], 'uncataloged': [],\n"
              "                'conflicts': [], 'intent': intent, 'abort_reason': None}\n"))

    write("e02_module_rebind",
          "E02 - module-level rebinding of an inspected function.",
          "The inspected `build_cutover_intent` def is intact and passes predicate 7; a trailing\n"
          "module-level assignment replaces it at import time.",
          PRE + PLAN + """

def _vacuous_intent(records, new_lines, acknowledged=()):
    return {'absent': [], 'added': [], 'blocking': []}


build_cutover_intent = _vacuous_intent
""")

    write("e03_inbody_rebind",
          "E03 - plan_cutover rebinds an inspected callee inside its own body.",
          "Every pinned call TEXT is unchanged; the name it resolves to is not.",
          PRE + plan_with(
              "    classified = classify_crontab_lines(current_text, classify_detail)",
              "    classify_crontab_lines = _empty_classification\n"
          ).replace("def plan_cutover(",
                    "def _empty_classification(current_text, classify_detail):\n"
                    "    return {'parsed': {'roles': None}, 'records': [], 'error': None}\n"
                    "\n\ndef plan_cutover(", 1))

    write("e04_abort_returns_success",
          "E04 (v3 residue R2) - `_abort` reports abort_reason=None.",
          "Every abort path is then read as a clean plan by run_cutover.",
          PRE.replace("'intent': intent, 'abort_reason': reason}",
                      "'intent': intent, 'abort_reason': None}") + PLAN)

    write("e05_continue_skip",
          "E05 - a `continue` skips lines before the record append.",
          "v3 predicate 4 only requires the append to be an unconditional DIRECT CHILD of the inner\n"
          "loop body, which a preceding `if ...: continue` satisfies. Skipped lines never become\n"
          "records, so they are neither uncataloged nor retained by the rebuild.",
          PRE.replace(
              "        for index, line in enumerate(parsed[location]):\n"
              "            records.append(",
              "        for index, line in enumerate(parsed[location]):\n"
              "            if line.startswith('#'):\n"
              "                continue\n"
              "            records.append(", 1) + PLAN)

    write("e06_second_success_dict",
          "E06 - a second, earlier success dict short-circuits the plan.",
          "Placed AFTER the uncataloged guard so the v3 ordering predicate is untouched. The dict is\n"
          "shaped exactly like the real one, so pinning the shape of ONE success dict is not enough:\n"
          "the SET of terminal returns has to be pinned.",
          PRE + plan_with(
              "    block = render_block(selected_tasks, roles)",
              "    if classification_context['fast_path']:\n"
              "        new_text = ''\n"
              "        intent = {'absent': [], 'added': [], 'blocking': []}\n"
              "        return {'new_text': new_text, 'preserved': [], 'uncataloged': [],\n"
              "                'conflicts': [], 'intent': intent, 'abort_reason': None}\n"))

    write("e07_context_callable",
          "E07 - delegation through a callable stored in the context dict.",
          "Defeats any allowlist keyed on `ast.Name` callees, because the callee is a Subscript.",
          PRE + plan_with(
              "    classify_detail = _detail_classifier(classification_context)",
              "    if classification_context['planner']:\n"
              "        return classification_context['planner'](current_text)\n"))

    write("e08_decorator",
          "E08 - a decorator replaces plan_cutover wholesale.",
          "The decorated def still parses exactly as the honest body.",
          PRE + """

def _bypass(function):
    def wrapper(current_text, classification_context, *, acknowledged=()):
        return {'new_text': '', 'preserved': [], 'uncataloged': [],
                'conflicts': [], 'intent': {'absent': [], 'added': [], 'blocking': []},
                'abort_reason': None}
    return wrapper


@_bypass
""" + PLAN)

    write("e09_intent_helper_lie",
          "E09 - the intent report is computed by uninspected helpers.",
          "v3 predicate 7 only requires `absent` to be a comprehension whose iterator MENTIONS\n"
          "`records`. Both the element expression and the membership test are delegated away.",
          PRE.replace(MISSING, "def _missing_occurrences(records, new_lines):\n    return []", 1)
          .replace(ABSENT, "    absent = [_absence(r) "
                           "for r in _missing_occurrences(records, new_lines)]", 1) + PLAN)

    write("e10_no_totality_guard",
          "E10 - the coverage guard is removed from classify_crontab_lines.",
          "Proves predicate 17 is load-bearing rather than decorative.",
          PRE.replace(GUARD, "", 1) + PLAN)

    write("e11_parser_marker_theft",
          "E11 - the parser reports live lines as block markers (v4 author evasion attempt).",
          "Aimed at predicate 17: if the expected line set were computed from `parsed['markers']`,\n"
          "a parser could exclude any line it liked from BOTH sides of the reconciliation and drop\n"
          "it silently. v4 derives the expected set from a module constant instead, so this case\n"
          "decides whether that choice was necessary.",
          PRE.replace("from cron_parse import parse_crontab",
                      "from cron_parse import marker_thieving_parse_crontab as parse_crontab",
                      1) + PLAN)

    write("e12_marker_collusion",
          "E12 - the parser and a lying marker constant collude on which line is a marker.",
          "One level below E11. Steals a live line from every location list AND names that same\n"
          "line in the guard's exclusion set, so it is missing from both sides of the\n"
          "reconciliation. Defeats a guard whose exclusion set is a FUNCTION call; predicate 18\n"
          "answers it by pinning MARKER_PREFIXES to a module-level literal.",
          PRE.replace("from cron_parse import parse_crontab",
                      "from cron_parse import colluding_parse_crontab as parse_crontab", 1)
          .replace("MARKER_PREFIXES = ('# >>> workspace-hub managed', "
                   "'# <<< workspace-hub managed')",
                   "MARKER_PREFIXES = ('0 1 * * * /usr/bin/thirdparty', "
                   "'# <<< workspace-hub managed')", 1) + PLAN)

    write("e13_managed_line_reported_ignore",
          "E13 - the classifier reports live managed-block cron lines as class `ignore`.",
          "Managed-block records are ALWAYS dropped by the rebuild (only `before` and `after` are\n"
          "retained), so the intent report is their only protection - and `blocking` deliberately\n"
          "excludes class `ignore`. This is not an attestation gap: it is the design decision v3\n"
          "recorded as an open question. The behaviour column measures its cost.",
          PRE.replace(CLASSIFIER,
                      "    def classify_detail(line):\n"
                      "        return {'class': 'ignore', 'reason': 'env-or-comment'}\n"
                      "    return classify_detail", 1) + PLAN)

    write("e14_ignore_exempts_managed",
          "E14 - `blocking` reverts to exempting class `ignore` regardless of location.",
          "A one-token regression of the design decision that closes E13. Predicate 19 exists\n"
          "so that reverting it is a red test rather than an invisible diff.",
          PRE.replace(
              "                if (a['class'] != 'ignore' or a['location'] == 'managed')\n"
              "                and a['key'] not in acknowledged]",
              "                if a['class'] != 'ignore' and a['key'] not in acknowledged]", 1)
          .replace(CLASSIFIER,
                   "    def classify_detail(line):\n"
                   "        return {'class': 'ignore', 'reason': 'env-or-comment'}\n"
                   "    return classify_detail", 1) + PLAN)

    write("r01_detail_classifier_constant",
          "R01 (v3 residue R1) - `_detail_classifier` calls every line cataloged.",
          "v3 measured this as accepted by its predicate set. The behaviour column records whether\n"
          "it is still a data-loss path under the v4 reference shape.",
          PRE.replace(CLASSIFIER,
                      "    def classify_detail(line):\n"
                      "        return {'class': 'cataloged', 'reason': 'canonical-exact-line'}\n"
                      "    return classify_detail", 1) + PLAN)

    write("r03_parse_mispartitions",
          "R03 (v3 residue R3) - the parser puts every line in `before`.",
          "The parser is not an inspected function and cannot be attested structurally.",
          PRE.replace("from cron_parse import parse_crontab",
                      "from cron_parse import mispartitioning_parse_crontab as parse_crontab",
                      1) + PLAN)


if __name__ == "__main__":
    build()
    print(f"regenerated {len(list(CASES.glob('*.py'))) - 2} derived cases in {CASES}")
