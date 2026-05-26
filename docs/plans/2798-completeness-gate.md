# Plan for #2798: test-based completeness score (0–100%) as pre-closure hard-stop gate + HTML artifact

> **Status:** plan-review
> **Complexity:** T3 (systemic — harness/governance, cross-cutting close flow, multi-file)
> **Date:** 2026-05-25
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2798
> **Client:** N/A
> **Project:** (none)
> **Review artifacts:** scripts/review/results/2026-05-25-plan-2798-claude.md | ...-codex.md | ...-gemini.md (pending dispatch)

---

## Resource Intelligence Summary

Sources consulted (≥3, with concrete findings):

1. **Issue #2798 body** — the requirement: test-based completeness % (0–100), owner-reviewed, gating `gh issue close`; HTML documentation. (source 1)
2. **#1839 (workflow hard-stops & enforced gates)** — Found: the enforced-gate framework already exists as an open epic; "TDD mandatory" and review-gate are documented as *aspirational/warning-mode, not enforced* (`SKIP_REVIEW_GATE=1` bypass trivial). **This gate is a child of #1839** and must reuse its hard-stop mechanism, not invent a parallel one.
3. **#1663 + #1629 (module status matrix)** — Found: the matrix already emits `quality_score`, `test_source_ratio`, `loc` per package as JSON snapshots. **The code-side completeness score MUST reuse `quality_score`/`test_source_ratio`** rather than compute a new metric. Gap: it is per-*package*, not per-*issue* — needs an issue→package(s) mapping.
4. **#2110 (session-close structured report)** — Found: a Stop/SessionEnd hook + `scripts/workflow/` report generator emitting gate pass/fail summary is in scope/landing. **Reuse its hook infra**; the completeness report is the issue-scoped analogue (per-issue, not per-session).
5. **#2236 (post-closure promotion)** — Found: closure-flow modification point in `issue-planning-mode`. This gate fires *before* close; #2236 fires *after*. Sequence them, don't collide.
6. **`.claude/rules/patterns.md`** — Found: enforcement gradient (prose → script → hook) with prior art `scripts/enforcement/check-no-abs-paths.sh` (exit 0/1, `*_ALLOW=1` bypass, stderr-only, git-root anchored). The pre-close check must follow this shape.
7. **`hermes kanban complete --help`** — Found: `--metadata` accepts structured JSON → natural store for `completeness_pct` + evidence.
8. **Prototype** `docs/reports/2026-05-25-session-completeness-scorecard.html` (commit `f262d38b0`) — rubric + owner-override layout + worked example; the artifact template.

**Gaps (build from scratch):** issue→package mapping for the code score; the ops/infra rubric formalization; the `completeness_pct` persistence + issue stamp; the pre-close enforcement check; wiring into the `issue-planning-mode` close flow; the per-issue HTML generator.

## Approach

Layer onto existing infrastructure; build nothing that #1629/#1839/#2110 already provide.

1. **Score computation (`scripts/workflow/completeness_score.py`)**
   - *Code issues:* resolve affected package(s), pull `quality_score` + `test_source_ratio` from the latest module-status-matrix snapshot (#1629), combine with an acceptance-criteria checklist completion ratio → weighted 0–100.
   - *Ops/infra issues:* rubric-based (live-probe evidence bands per the prototype) — explicit evidence list, each item scored.
   - Output a `CompletenessResult{pct, band, evidence[], source}` dict.
2. **Persistence** — write `completeness_pct` + evidence via `hermes kanban complete --metadata` and stamp a one-line summary as an issue comment.
3. **HTML artifact** — `scripts/workflow/render_completeness_html.py` → `docs/reports/<date>-<issue>-completeness.html` reusing the prototype's CSS/rubric/owner-override layout.
4. **Pre-close gate** — `scripts/enforcement/check-completeness-before-close.sh` (exit 0/1, `COMPLETENESS_ALLOW=1` bypass, stderr-only): verifies an owner-confirmed `completeness_pct >= ${COMPLETENESS_THRESHOLD:-90}` is recorded for the issue. Owner override is **down-only** (recorded confirmed value may be ≤ computed, never silently >).
5. **Workflow wiring** — add the gate step to `issue-planning-mode` between Cross-review and Close; document in the flow.
6. **Enforcement gradient** — land prose-rule + script first (Level 2); promote to a pre-close hook (Level 3) after burn-in, consistent with `patterns.md`.

## Implementation steps (TDD — tests first per hard gate)

1. Write tests: `tests/workflow/test_completeness_score.py` (code path reuses a fixture matrix snapshot; ops path scores a fixture evidence list; boundary bands 89/90).
2. Write tests: `tests/enforcement/test_check_completeness_before_close.py` (≥threshold passes; <threshold fails exit 1; missing record fails; `COMPLETENESS_ALLOW=1` bypasses; override-up rejected).
3. Implement `completeness_score.py` to green.
4. Implement `check-completeness-before-close.sh` to green.
5. Implement `render_completeness_html.py` (golden-file test against prototype layout).
6. Wire into `issue-planning-mode` SKILL + add the prose rule under `.claude/rules/`.
7. Adversarial review (plan already in review; implementation review T3 after code lands).

## Test plan
- Unit: score computation (both paths), boundary bands, gate check exit codes, override-direction enforcement.
- Integration: end-to-end on a sample closed-eligible vs blocked issue; HTML renders + opens.
- Regression: scope a glob so sibling enforcement scripts aren't broken (`feedback_regression_test_broader_than_issue_scope`).

## Risks
- **Score gaming** — % derived from tests can be inflated by trivial tests; mitigate with `test_source_ratio` floor + acceptance-criteria checklist, and adversarial review.
- **Issue→package mapping ambiguity** for cross-cutting issues — fall back to the ops/rubric path when no clean package mapping exists.
- **Hook over-blocking** — keep at Level-2 script (warn/exit-1 with bypass) until burn-in; don't jump to a blocking hook (`patterns.md`).
- **Overlap with #2110/#1839** — coordinate; reuse their hook/score infra, don't fork it.

## Out of scope
- Implementing #2236 promotion targets; the #1663 trend dashboard; per-package PRODUCTION promotion (#1662).

---
_Not self-approved. Awaiting USER APPROVAL to move status:plan-review → status:plan-approved per the load-bearing user-in-loop gate (`feedback_never_offer_to_self_label_plan_approved`)._
