# Adversarial Review — Plan for Issue #510

**Plan:** `docs/plans/2026-04-24-issue-510-fix-20-test-failures.md`
**Reviewer stance:** ADVERSARIAL / defect-hunter
**Date:** 2026-04-24

---

## Verdict

**MINOR** — Plan is directionally correct, correctly scoped to test-only changes, correctly categorizes the three root-cause classes, and includes the Category-4 traceback-read gate. Several defects are real but none block approval; they should be patched into the plan before implementation starts.

---

## Defect Checklist (adversarial sweep)

| # | Check | Status | Note |
|---|---|---|---|
| 1 | Scope limited to test-only edits | PASS | Hard constraint at L142 explicitly forbids `digitalmodel/src/` edits |
| 2 | 20 failures enumerated | PARTIAL | Categories enumerated, but exact 20-test ID list not pinned (defers to `--collect-only`) |
| 3 | Root-cause categorization (3 classes) | PASS | Matches intel (rename-1, rename-2, path-rename) plus Category-4 errors |
| 4 | Category-4 traceback-read gate | PASS | L177 acceptance criterion + L201 risk mitigation + L142 escalation clause |
| 5 | Follow-up audit recommendation (other suites) | PARTIAL | Listed as a Risk (L200) but not as a discrete follow-up issue/action — weak |
| 6 | No invented fixture data | PASS | L138 and L203 explicitly require `pytest.skip` over fabrication |
| 7 | Preserves alias-round-trip tests | PASS | Explicit carve-out at L137 and TDD row at L162 |
| 8 | Shapes/ramps scope discrepancy addressed | FAIL | Intel L78 flags "shapes_builder ramp/ramps" failures not covered in the failing-file list. Plan ignores this entirely. |
| 9 | "20 failures" vs "5 errors" scope | PASS | L204 Risk + issue-body wording interpreted inclusively |
| 10 | No past-tense artifact drift | PASS | All edits are framed as future ("must", "will") |
| 11 | Verification block has 3+ sources | PASS | HTML comment at L74 claims 6 sources |
| 12 | Hard-coded absolute paths in scripts | PASS | Plan only shows code snippets; no scripts land under this plan |
| 13 | Review artifact paths populated | PASS | L7 + Artifact Map rows |
| 14 | Complexity label defended | PASS | Explicit justification at L209-211 |
| 15 | Regression guard for extractor | PASS | Last row of TDD Test List |
| 16 | `parents[N]` placeholder | FAIL | L122/L139 leaves `parents[N]` unresolved. N is determinable from static file location; plan should pin the integer. |
| 17 | `--collect-only` baseline timing | PASS | Pseudocode step 2 captures snapshot before patching |
| 18 | Grep guard for legacy names is too lenient | MINOR | Acceptance gate at L172 allows any match "only in extractor alias-round-trip test cases" — no count specified; drive-by stale reference could slip through unnoticed |
| 19 | Test file count mismatch | FAIL | Intel L82 says "20 test files touched (minimum)" but plan Files-to-Change lists only 5 test files. Either intel overcounts or plan undercounts; not reconciled. |

---

## Specific Defects

### D1 (FAIL → should-fix): shapes_builder ramp/ramps failures silently dropped

**Where:** plan does not mention `shapes_builder` or ramps anywhere.
**Source:** issue body says "`shapes_builder` ramp/ramps related failures"; intel L78 explicitly flags: *"Shapes/ramps assertions flagged in issue body not found in grep of `test_generic_builder.py`. The issue mentions 'shapes_builder ramp/ramps related failures' — these likely live in a file like `test_shapes_builder.py` not in the failing-file list."*
**Defect:** the plan's Files-to-Change list touches 5 files, none named `shapes_builder*`. If the shapes failures are a 6th root-cause class (or a different file entirely), the deliverable "0 failures" will not be met after the planned edits complete.
**Fix:** before implementation, the pseudocode's step-2 `--collect-only` must also be used to confirm whether shapes_builder tests exist in the failing set; if yes, add them as a 6th root-cause class or explicitly defer to a follow-up issue. Do not discover this mid-implementation.

### D2 (FAIL → should-fix): `parents[N]` is an unresolved placeholder

**Where:** Pseudocode L122 and Files-to-Change L139.
**Defect:** `Path(__file__).resolve().parents[N]` leaves `N` as a literal letter. This pushes a decision onto the implementer that is statically resolvable right now (count the path segments from the test file to the repo root). An implementer under time pressure may guess `parents[3]` and produce silent cwd-independent path drift, since `Path.exists()` returns `False` quietly. The plan should resolve `N` by inspection.
**Fix:** count segments: `digitalmodel/tests/solvers/orcaflex/test_orcaflex_converter_enhanced.py` → `parents[0]=orcaflex`, `parents[1]=solvers`, `parents[2]=tests`, `parents[3]=digitalmodel`, `parents[4]=workspace-hub-root`. If the anchor is workspace-hub root (where `docs/domains/...` lives), N=4. Pin this in the plan.

### D3 (MINOR): Grep acceptance gate has no hit-count

**Where:** Acceptance Criteria L172.
**Defect:** "returns only the extractor alias-round-trip test cases" — the criterion depends on the reviewer recognizing which hits are legitimate. A stale hit in, say, a docstring or a negative-assertion block could pass visually. A stronger gate names the expected line count (e.g., "exactly N hits, all in `test_extractor.py::TestAliasRoundTrip`").
**Fix:** after the first clean run, record the exact matching-line count; codify it.

### D4 (MINOR): File-count reconciliation with intel

**Where:** intel L82 ("20 test files touched (minimum)") vs plan's 5-file Files-to-Change.
**Defect:** intel likely confused "20 failures" with "20 files." Plan should note the reconciliation (5 files, ~20 test methods across them) to prevent a reviewer from thinking scope shrank silently.
**Fix:** add a one-line note in Files-to-Change: *"Intel-estimated '20 files' is actually 20 test methods across the 5 files listed above."*

### D5 (MINOR): Follow-up audit recommendation is under-specified

**Where:** L200 Risks.
**Requirement:** the prompt asks that the plan "add a follow-up recommendation for auditing OTHER test suites for the docs path-rename drift (NOT expanding scope, just recommending)."
**Defect:** the recommendation exists but is buried in the Risks list. A Risk is passive; a follow-up recommendation should be actionable (e.g., "file follow-up issue after implementation" with a concrete grep command that scopes the audit).
**Fix:** add a Follow-ups section (or one line in Acceptance Criteria) stating: *"Post-implementation: file a follow-up issue to run `grep -rn 'docs/modules' digitalmodel/tests/ -- :!*.md` across the rest of the digitalmodel test tree and triage any remaining hits. Do not expand #510 scope."*

### D6 (INFO): Hard constraint wording conflicts with Category-4 escalation

**Where:** L142 ("no edits to `digitalmodel/src/` are permitted under this plan") vs L211 ("Escalate to T2 only if the Category-4 traceback reveals a real source regression").
**Observation:** these are actually consistent — escalation means re-opening approval, not silent src/ edits. But the phrasing is ambiguous. Consider rewording L211 to "Escalate to a *separate* T2 plan" to eliminate any reading that src/ edits can happen under #510.

---

## Justification for MINOR verdict (not MAJOR)

The plan satisfies every prompt-mandated check in substance: test-only scope (PASS), root-cause categorization (PASS), Category-4 gate (PASS), follow-up recommendation (PARTIAL-PASS). The defects above are all patchable in <30 minutes and do not threaten correctness of the core approach. The one real risk (D1: shapes_builder failures) is flagged in the intel that the planner did consult, so it's a review-miss rather than a fundamental design flaw — but it must be resolved before implementation to avoid "0 failures" being unmet.

None of the defects reach MAJOR severity (which would require scope drift, safety issues, or a broken core approach).

---

## Summary line

**MINOR — 6 defects (2 fail / 3 minor / 1 info). Critical finding: shapes_builder ramp/ramps failures listed in the issue body + intel are not covered by the plan's 5-file Files-to-Change list; the deliverable "0 failures" cannot be met until this is reconciled via `--collect-only` before implementation begins.**
