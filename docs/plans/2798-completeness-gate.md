# Plan for #2798: test-based completeness score (0–100%) as pre-closure hard-stop gate + HTML artifact

> **Status:** plan-review (revised post-review v2)
> **Complexity:** T3 (systemic — harness/governance, cross-cutting close flow, multi-file)
> **Date:** 2026-05-25
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2798
> **Client:** N/A
> **Project:** (none)
> **Review artifacts:** scripts/review/results/2026-05-25-plan-2798-{claude,codex,gemini}.md
> **Review outcome:** Claude r1 MAJOR + Codex r2 MAJOR (corroborating) → revised inline (r-inline). Gemini UNAVAILABLE (env issue → T3 degraded to T2). v1→v2 diff addresses both consensus MAJORs + key MINORs below.

---

## Resource Intelligence Summary

1. **Issue #2798 body** — requirement: test-based completeness % (0–100), owner-reviewed, gating `gh issue close`; HTML documentation.
2. **#1839 (workflow hard-stops & enforced gates)** — enforced-gate epic; TDD/review gates documented as warning-mode/bypassable. This is a child; reuse its hard-stop mechanism. **Gap (Codex#6): #1839 exposes no concrete shared gate API/schema yet — this plan must define the schema it contributes, not assume one.**
3. **#1663 + #1629 (module status matrix)** — emits `quality_score`, `test_source_ratio`, `loc` per package as JSON snapshots. Reuse for the code score. Gap: per-*package*, not per-*issue*.
4. **#2110 (session-close structured report)** — Stop/SessionEnd hook + `scripts/workflow/` report generator emitting gate pass/fail. Reuse its hook; this is the issue-scoped analogue.
5. **#2236 (post-closure promotion)** — closure-flow point in `issue-planning-mode`; fires *after* close. Sequence, don't collide.
6. **`.claude/rules/patterns.md`** — enforcement gradient (prose→script→hook), prior art `check-no-abs-paths.sh` (exit 0/1, `*_ALLOW=1`, stderr-only).
7. **`hermes kanban complete --metadata`** — JSON store for the *computed* score.
8. **Prototype** `docs/reports/2026-05-25-session-completeness-scorecard.html` (`f262d38b0`) — artifact template.

**Gaps to build:** issue→package mapping; completeness-class taxonomy; computed-score persistence; **server-side** close enforcement; owner-verify signal; issue-planning-mode wiring; per-issue HTML generator.

## Review-driven corrections (v1→v2)

| # | Finding (reviewer) | Correction in v2 |
|---|---|---|
| MAJOR-1 | Pre-close "git hook" can't intercept `gh issue close` (Claude#1, Codex#15) | Enforcement is a **GitHub Action on the `issues.closed` webhook**: if a closed issue lacks a valid completeness record + owner-verify label, the Action **re-opens it and comments**. Local `check-completeness-before-close.sh` is demoted to an advisory pre-flight (not the gate). |
| MAJOR-2 | Owner-confirmed % is agent-spoofable in metadata/comments (Claude#2, Codex#20) | Owner confirmation = an **owner-only `status:completeness-verified` label** (label events are attributable in the GH audit log; a repo ruleset restricts who may apply it). Agent writes only the *computed* score; it cannot self-verify. The Action cross-checks the label actor ≠ the closing bot. |
| MINOR | "Based on tests" undefined for test-less issues (Claude#3, Codex#13) | Completeness **class taxonomy**: `code` (test-derived: pass-rate + changed-code coverage + `test_source_ratio` floor) vs `evidence` (ops/docs/governance: explicit evidence rubric, labeled "evidence-based, no test surface"). Class is auto-derived from changed files — **not selectable** (closes Codex#10 dodge). |
| MINOR | Single global threshold 90 arbitrary (Claude#4, Codex#13) | **Per-class thresholds** in config (`code:90`, `evidence:80`) + a per-issue declared-exception that itself requires the owner-verify label. |
| MINOR | #2110 hook collision (Claude#5, Codex#7/#17) | Shared `completeness/v1` report schema; this gate **consumes #2110's single hook** (no second hook); dedup by issue id; defined ordering (completeness before promotion #2236). |
| MINOR | issue→package mapping undesigned (Codex#9) | Map from the issue's merged-PR **changed files → package** via a `path→package` table (CODEOWNERS-style); multi-package = **min(scores)** (conservative); no mapping ⇒ `evidence` class. |
| MINOR | snapshot freshness (Codex#8) | Score binds the matrix snapshot **commit SHA**; stale (>1 snapshot behind HEAD) or missing ⇒ fail-closed with a clear message. |
| MINOR | gaming via low-value tests (Codex#11/#12) | `test_source_ratio` floor + **changed-code coverage** (not whole-package); checklist items must carry an evidence link or don't count. |
| MINOR | missing legal/security scan (Codex#18) | Add `scripts/legal/legal-sanity-scan.sh` to the verification gate. |

## Approach (v2)

1. **`scripts/workflow/completeness_score.py`** — classify issue (`code`|`evidence`) from changed files; `code` reuses #1629 snapshot (SHA-bound) + changed-code coverage + checklist-with-evidence ratio; `evidence` uses the rubric. Emits `CompletenessResult{pct, class, threshold, snapshot_sha, evidence[]}`.
2. **Persistence** — write the **computed** result via `hermes kanban complete --metadata` + stamp on the issue. (Computed only; never the verified value.)
3. **HTML** — `render_completeness_html.py` → `docs/reports/<date>-<issue>-completeness.html`; test the score/evidence **data contract**, not the CSS (closes Claude#6).
4. **Server-side gate** — `.github/workflows/completeness-gate.yml` on `issues.closed`: require (a) a computed record for the issue and (b) `status:completeness-verified` applied by an authorized owner; else re-open + comment. Repo ruleset restricts the label.
5. **Advisory pre-flight** — `scripts/enforcement/check-completeness-before-close.sh` (exit 0/1, `COMPLETENESS_ALLOW=1`) for local feedback before pushing a close; explicitly NOT the authoritative gate.
6. **Wiring** — issue-planning-mode close step + prose rule in `.claude/rules/`; consume #2110's hook.

## Implementation steps (TDD)
1. Tests: `test_completeness_score.py` — class auto-derivation, code vs evidence scoring, boundary 89/90, multi-package min, stale/missing snapshot fail-closed, malformed inputs.
2. Tests: gate workflow — record-missing ⇒ reopen; label-missing ⇒ reopen; label-by-unauthorized-actor ⇒ reopen; valid ⇒ stays closed. (Exercised via `act` or a workflow unit harness; **plus** an integration test that proves a close is reverted before standing — closes Codex#15.)
3. Tests: #2110 co-fire (both gates in one path; dedup; ordering); invalid threshold config.
4. Implement to green, in order: score → persistence → html → workflow → advisory script → wiring.
5. Verification gate: tests green + `legal-sanity-scan.sh` + adversarial **implementation** review (T3) before merge.

## Test plan
- Unit: classifier, both scoring paths, thresholds, snapshot SHA/staleness, malformed metadata, duplicate/stale records, wrong-issue.
- Integration: close-revert proof; label-actor authorization; #2110 co-fire; HTML data-contract golden (data, not markup).
- Security: `legal-sanity-scan.sh`; verify label cannot be self-applied by the automation token.
- Regression: scope glob to the enforcement/workflow dir (`feedback_regression_test_broader_than_issue_scope`).

## Risks
- **GH Action latency** — close-revert isn't instantaneous; a closed issue is briefly visible closed. Acceptable; comment explains.
- **Label ruleset** — requires repo-admin to configure the authorized-applier ruleset; document as a prerequisite.
- **Over-blocking** — keep advisory script non-blocking; the Action is the gate, with a documented admin bypass.
- **#1629 dependency** — if the matrix snapshot pipeline is down, `code` issues fail-closed; document the manual `evidence`-class override (owner-verified).

## Out of scope
- #2236 promotion targets; #1663 trend dashboard; #1662 PRODUCTION promotion.

---
_Not self-approved. Carries Claude r1 + Codex r2 review evidence (both MAJOR, addressed above); Gemini UNAVAILABLE. Awaiting USER APPROVAL to move status:plan-review → status:plan-approved (`feedback_never_offer_to_self_label_plan_approved`)._
