# Plan for #2798: test-based completeness score (0–100%) as pre-closure hard-stop gate + HTML artifact

> **Status:** plan-approved (user, 2026-05-25) → implemented on `feat/2798-completeness-gate` (PR #2800)
> **Complexity:** T3 (systemic — harness/governance, cross-cutting close flow, multi-file)
> **Date:** 2026-05-25
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2798
> **Client:** N/A
> **Project:** (none)
> **Review artifacts:** scripts/review/results/2026-05-25-plan-2798-{claude,codex,gemini}.md (plan) + 2026-05-25-impl-2798-{claude,codex}.md (code)
> **Review outcome:** Plan stage — Claude r1 MAJOR + Codex r2 MAJOR → revised inline (r-inline). Code stage — Claude + Codex MAJOR → hardened inline (forgeable-record, stale-label, over-scope). Gemini UNAVAILABLE (env) → T2.

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

## Review-driven corrections (plan stage, v1→v2)

| # | Finding (reviewer) | Correction |
|---|---|---|
| MAJOR-1 | Pre-close "git hook" can't intercept `gh issue close` (Claude#1, Codex#15) | Enforcement is a **GitHub Action on the `issues.closed` webhook**: if a closed issue lacks a valid completeness record + owner-verify label, the Action **re-opens it and comments**. Local `check-completeness-before-close.sh` is demoted to an advisory pre-flight (not the gate). |
| MAJOR-2 | Owner-confirmed % is agent-spoofable in metadata/comments (Claude#2, Codex#20) | Owner confirmation = an **owner-only `status:completeness-verified` label** (label events are attributable in the GH audit log; a repo ruleset restricts who may apply it). Agent writes only the *computed* score. The Action cross-checks the label actor ≠ the closing bot. |
| MINOR | "Based on tests" undefined for test-less issues (Claude#3, Codex#13) | Completeness **class taxonomy**: `code` (test-derived) vs `evidence` (ops/docs/governance rubric). Class is auto-derived from changed files — **not selectable** (closes Codex#10 dodge). |
| MINOR | Single global threshold 90 arbitrary (Claude#4, Codex#13) | **Per-class thresholds** (`code:90`, `evidence:80`). |
| MINOR | #2110 hook collision (Claude#5, Codex#7/#17) | Shared schema; consume #2110's single hook; dedup by issue id; ordering (completeness before promotion #2236). |
| MINOR | issue→package mapping undesigned (Codex#9) | Map changed files → package via a `path→package` table; multi-package = **min(scores)**; no mapping ⇒ `evidence` class. |
| MINOR | snapshot freshness (Codex#8) | Score binds the matrix snapshot **commit SHA**; stale/missing ⇒ fail-closed. |
| MINOR | gaming via low-value tests (Codex#11/#12) | `test_source_ratio` floor + **changed-code coverage**; checklist items must carry an evidence link or don't count. |
| MINOR | missing legal/security scan (Codex#18) | `legal-sanity-scan.sh` in verification. |

## Code-stage review corrections (as-built hardening)

| # | Finding (reviewer) | Correction |
|---|---|---|
| MAJOR-A | Body record forgeable; gate trusted record's own `threshold` (Codex#2) | Threshold from **server-side class config**, never the record; record **bound to `issue_number`**. |
| MAJOR-B | Stale-label bypass — label could pre-date a forged body edit (Codex#1/#3, Claude#2) | Gate requires `body_verified_fresh`: the verified label must be applied **at/after** the issue body's last edit. |
| MAJOR-C | Action reopened **every** completed/uncompleted close (Claude#1) | Action gated to `state_reason == 'completed'`; runner skips issues lacking `status:plan-approved`. |
| MINOR | weight/coverage validation, empty-checklist free pass, prefix-boundary, empty-owners opaque | Fail-closed input validation; empty checklist penalised; path-boundary prefix match; explicit empty-owners config error. |

## Approach (as-built)
1. `scripts/workflow/completeness_score.py` — classify (`code`|`evidence`); `code` reuses #1629 snapshot (SHA-bound, fail-closed) + changed-code coverage + evidence-linked checklist; `evidence` weighted ratio. Emits `CompletenessResult` (incl. `issue_number`, `generated_at`).
2. Persistence — computed result via `hermes kanban complete --metadata` + issue-body ```completeness {json}``` stamp.
3. HTML — `render_completeness_html.py` → `docs/reports/<date>-<issue>-completeness.html`; data-contract tested (not CSS); html-escaped.
4. Server-side gate — `.github/workflows/completeness-gate.yml` on `issues.closed` (scoped `completed`); `completeness_gate_check.py` (pure decision) + `completeness_gate_runner.py` (gh I/O); reopen+comment on deny.
5. Advisory pre-flight — `scripts/enforcement/check-completeness-before-close.sh` (`COMPLETENESS_ALLOW=1`).
6. Wiring — issue-planning-mode close step + `.claude/rules/completeness-before-close.md` + rules README.

## Test plan (as-built: 34 tests green)
- Unit: classifier + prefix-boundary, both scoring paths, thresholds, snapshot SHA/staleness fail-closed, coverage/weight validation, empty-checklist penalty.
- Gate decision: record-missing/label-missing/unauthorized-actor/self-verify/body-stale/forged-threshold/issue-mismatch/unknown-class all DENY; valid ALLOW; per-class thresholds.
- HTML: data-contract round-trip + injection-escape.
- Security: `legal-sanity-scan.sh --diff-only` PASS.

## Risks
- **GH Action latency** — close-revert isn't instantaneous; a closed issue is briefly visible closed. Acceptable; comment explains.
- **Label ruleset / `COMPLETENESS_OWNERS`** — repo-admin must configure the authorized-applier ruleset + the owners variable; documented as a prerequisite (unset ⇒ fail-closed on completed closes).
- **#1629 dependency** — if the matrix snapshot pipeline is down, `code` issues fail-closed; manual `evidence`-class override (owner-verified).

## Out of scope
- #2236 promotion targets; #1663 trend dashboard; #1662 PRODUCTION promotion.
