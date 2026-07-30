"""Run the v4 predicate prototype over every committed case.

    python3 scripts/review/prototypes/3709-v4/run.py [case-name ...]

Exit 0 when the reference is accepted and every non-reference case is rejected
by at least one named predicate, EXCEPT the cases listed in ADMITTED_RESIDUE,
which the plan admits the attestation still accepts.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from mutations import NAMED_MUTATIONS, apply  # noqa: E402
from preservation_prototype import NAMED_PREDICATES, evaluate, v3_shape  # noqa: E402

HERE = Path(__file__).resolve().parent
CASES = HERE / "cases"

# Shapes the v4 predicate set still ACCEPTS. Each must name a covering test.
ADMITTED_RESIDUE = {
    "r01_detail_classifier_constant": "row 1 test_ace1_fixture_aborts_with_47_managed_uncataloged",
    "r03_parse_mispartitions": "row 20 test_ace2_fixture_classifies_as_captured",
    "e11_parser_marker_theft": "row 20 test_ace2_fixture_classifies_as_captured",
    "e13_managed_line_reported_ignore": "row 2 test_managed_block_unknown_line_blocks_before_rebuild",
    # v5: accepted by the DEMOTED predicate set, caught by the PRIMARY control.
    "z07_r01_intent_blocking_cleared": "row P1 test_plan_cutover_never_loses_a_live_line_without_aborting",
    "z10_new_text_dedupes": "row P1 test_plan_cutover_never_loses_a_live_line_without_aborting",
}


def _load(name):
    return (CASES / f"{name}.py").read_text()


def main(argv):
    names = argv or sorted(p.stem for p in CASES.glob("*.py"))
    reference = evaluate(_load("reference"))
    failures = []
    print(f"{'case':44s} v4     v3     first failing predicate")
    print("-" * 108)
    for name in names:
        results = evaluate(_load(name))
        accepted = all(results.values())
        failed = [k for k, v in results.items() if not v]
        note = "-" if accepted else failed[0]
        if len(failed) > 1:
            note = f"{note}  (+{len(failed) - 1} more)"
        print(f"{name:44s} {str(accepted):6s} {str(v3_shape(_load(name))):6s} {note}")
        if name == "reference":
            if not accepted:
                failures.append(f"reference REJECTED on {failed}")
        elif accepted and name not in ADMITTED_RESIDUE:
            failures.append(f"{name} ACCEPTED (undeclared evasion)")
        elif not accepted and name in ADMITTED_RESIDUE:
            failures.append(f"{name} declared residue but is now rejected — update the plan")
    print()
    print(f"{'v3 textual mutation':44s} v4     v3     first failing predicate")
    print("-" * 108)
    for mutation in NAMED_MUTATIONS:
        source = apply(mutation)
        results = evaluate(source)
        failed = [k for k, v in results.items() if not v]
        note = "-" if not failed else failed[0]
        if len(failed) > 1:
            note = f"{note}  (+{len(failed) - 1} more)"
        label = f"{mutation[0]} {mutation[1]}"
        print(f"{label:44s} {str(not failed):6s} {str(v3_shape(source)):6s} {note}")
        if not failed:
            failures.append(f"{mutation[0]} ACCEPTED")
    print()
    print(f"predicates: {len(NAMED_PREDICATES)}   file cases: {len(names)}   "
          f"textual mutations: {len(NAMED_MUTATIONS)}")
    print(f"reference per-predicate: {'all True' if all(reference.values()) else reference}")
    for line in failures:
        print(f"FAIL: {line}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
