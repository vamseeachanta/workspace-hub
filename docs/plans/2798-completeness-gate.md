# Plan for #2798: test-based completeness score (0–100%) as pre-closure hard-stop gate + HTML artifact

> **Status:** plan-approved (user, 2026-05-25) → implemented on `feat/2798-completeness-gate`
> **Complexity:** T3 · **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2798 · **Client:** N/A
> **Review artifacts:** scripts/review/results/2026-05-25-plan-2798-{claude,codex,gemini}.md
> **Review outcome:** Claude r1 MAJOR + Codex r2 MAJOR (corroborating) → fixed v2 (table below). Gemini UNAVAILABLE → T2.

## Requirement
For all completed work, a test-/evidence-based completeness score (0–100%) the user reviews before issue closure; progress documented in HTML.

## Position (discovery-first; not a duplicate)
Child of #1839 (enforced gates); reuses #1629/#1663 `quality_score`+`test_source_ratio`; complements #2110 (session-close report); sequences before #2236 (post-closure promotion).

## Review-driven design (v2)
| Defect (reviewer) | Fix |
|---|---|
| git hook can't intercept `gh issue close` (Claude#1, Codex#15) | **GitHub Action on `issues.closed`** reopens+comments; local `.sh` is advisory only |
| owner-% agent-spoofable (Claude#2, Codex#20) | **owner-only `status:completeness-verified` label**, applied by an authorized actor ≠ closer; agent writes only the computed score |
| "tests" undefined for test-less issues (Claude#3) | **class taxonomy** code (test-derived, thr 90) vs evidence (rubric, thr 80), auto-derived from changed files, non-selectable |
| arbitrary threshold (Claude#4, Codex#13) | per-class thresholds |
| #2110 collision (Claude#5, Codex#7/#17) | shared record schema; consume #2110 hook; dedup |
| issue→package undesigned (Codex#9) | changed-files→package map; multi-package = min |
| snapshot freshness (Codex#8) | bind matrix snapshot SHA; stale/missing ⇒ fail-closed |
| gaming via low-value tests (Codex#11/#12) | tsr floor + changed-code coverage + evidence-linked checklist |
| missing legal scan (Codex#18) | `legal-sanity-scan.sh` in verification |

## Components (implemented)
1. `scripts/workflow/completeness_score.py` — classify + score (code/evidence); fail-closed on stale snapshot/missing package; min over packages; tsr floor; evidence-linked checklist. (tests: `tests/workflow/test_completeness_score.py`, 12)
2. `scripts/workflow/completeness_gate_check.py` — pure close-gate decision (record present, owner label, authorized ≠ closer, pct≥threshold). (tests: `tests/workflow/test_completeness_gate_check.py`, 7)
3. `scripts/workflow/completeness_gate_runner.py` — gh I/O wrapper around the decision (CI-validated).
4. `.github/workflows/completeness-gate.yml` — authoritative server-side gate (reopen+comment on deny).
5. `scripts/enforcement/check-completeness-before-close.sh` — advisory local pre-flight (`COMPLETENESS_ALLOW=1` bypass).
6. `scripts/workflow/render_completeness_html.py` — HTML artifact embedding the exact record; html-escaped. (tests: `tests/workflow/test_render_completeness_html.py`, 5)
7. `.claude/rules/completeness-before-close.md` + issue-planning-mode wiring + rules README.

## Close flow
Issue → Plan → Approve → Implement → Cross-review → **completeness gate** → Close → (promotion #2236).

## Out of scope
#2236 targets; #1663 trend dashboard; #1662 PRODUCTION promotion.
