# Plan-Review Queue Health Audit — 2026-05-02

**Trigger:** /whats-next dispatch added 5 plans to a queue that already held 16 from concurrent sessions; total reached 21. User asked to "continue work" — audit chosen over more dispatch since queue depth, not plan supply, is the bottleneck.

## Method

5-signal audit per `.claude/skills/coordination/issue-planning-mode/SKILL.md` "Pending cross-review audit routine":

1. `gh issue list --label status:plan-review` — live label state
2. `docs/plans/` — canonical plan file presence
3. `scripts/review/results/` — per-provider review artifacts
4. Other status-label drift (`status:pending`, etc.)
5. Latest-review verdict spot-check (regex over first 2.5KB of each review file)

## Headline numbers

- **21 issues** at `status:plan-review`
- **0 missing-plan drift** — every issue has a canonical plan file
- **0 label drift** — no `+status:*` co-labels
- **~7 of 21 actually approval-ready** — the other 14 either have unaddressed MAJOR findings or only single-provider coverage from a planning-only session

## Tier classification

### Tier A — Likely approval-ready (verify before approving)

| # | Latest verdicts | Confidence | Notes |
|---|---|---|---|
| #2588 | claude-internal MINOR | high | Single-author but with extensive evidence-verification table; 6/6 file claims and 5/5 issue states verified live. Codex/Gemini blocked from planning-only session per `feedback_permission_gate_blocks_cross_review`. |
| #2532 | claude MINOR + gemini FAILED-stream | high | Today's batch. Claude r1 MINOR + r3 fallback concurs. Gemini stream silent (CLI accepted prompt but no stdout). |

### Tier B — Revision likely complete, needs **fresh review wave** to confirm

These plans had MAJOR findings, were revised in-session, but the original review files still contain the MAJOR text. Per skill section "Governance cleanup after fresh MAJOR re-review", a fresh review confirming the patch is needed before user approval.

| # | Latest verdicts | Status | Recommended action |
|---|---|---|---|
| #2563 | claude MAJOR + gemini MAJOR | r2 revision in plan | Re-run Gemini against r2 plan |
| #2533 | codex MAJOR + gemini MAJOR | rev-3 in plan | Re-run Gemini against rev-3 plan |
| #2479 | claude MAJOR + gemini MAJOR | r1 patches in plan (per F1-F4 annotations) | Re-run Gemini against patched plan |
| #2523 | gemini MAJOR | revision in plan | Re-run Gemini against revised plan |

### Tier C — Under-reviewed (claude-internal only) — needs cross-provider passes

12 plans from the parallel /whats-next-style session's wave 1/2/3 of llm-wiki completeness audit. All have only single-author Claude reviews. Per skill, single-author isn't sufficient for `status:plan-approved` transition.

| # | Latest verdict | Action |
|---|---|---|
| #2597, #2596 | claude MAJOR | Revise + cross-review |
| #2595, #2594, #2593, #2592, #2591, #2590, #2587, #2586 | claude UNAVAILABLE/PASS | Cross-review needed |
| #2589 | (parse failure, manual check needed) | Manual verdict check + cross-review |

### Tier D — Multi-cycle plans with persistent MAJOR

| # | Latest verdicts | Pattern |
|---|---|---|
| #2552 | many provider rounds, latest still MAJOR | persistent MAJOR after multiple revision cycles |
| #2550 | many provider rounds, latest UNAVAILABLE/MAJOR | persistent MAJOR after multiple revision cycles |
| #2541 | mixed APPROVE+MAJOR across rounds | latest verdict ambiguous — needs human read |
| #2580 | claude-UNAVAILABLE + codex MAJOR | r2 plan revision present in main but no fresh review yet |

## What I did NOT do

- **Did not dispatch a re-review wave automatically.** That's 4-12 Gemini calls and the user should decide whether to spend that budget now vs. approve Tier A first and let Tier B/C remediation happen in the next session.
- **Did not edit any plan files.** This is an audit, not a remediation.
- **Did not change any GitHub labels.** No premature transitions to `status:plan-approved`.
- **Did not file any new issues.** The Tier-D persistent-MAJOR pattern (#2552, #2550, #2541) might warrant filing but the existing plans already document it.

## Recommended next-session actions, ranked

1. **Approve #2588 and #2532** if the user has read the plan bodies and accepts the MINOR findings as known. Smallest-effort queue reduction.
2. **Re-run Gemini against the 4 Tier-B plans** (#2563, #2533, #2479, #2523) — these were drafted today and just need fresh-review confirmation that the in-session revisions resolved the MAJOR findings. ~4 Gemini calls.
3. **Decide what to do about Tier D persistent-MAJOR** (#2552, #2550, #2541) — these have many revision cycles and are not converging. Per `feedback_codex_sustained_major_loop`, when a provider sustains MAJOR for 3+ rounds, surface a consensus-vs-minority decision instead of auto-cycling. May need user-level scope rewrite or close-as-superseded.
4. **Cross-review the Tier C llm-wiki wave** (#2586-#2597) — 12 plans, lowest priority because they're all `priority:medium`. Could be a separate dispatch wave on its own.

## Provider-availability constraint reminder

Per `feedback_codex_cli_0_124_upstream_regression`: codex-cli 0.124.0+ has stdin-hang regression (reproduced today on 0.128.0). All Codex review attempts will fail until the version-pin from #2479's plan is implemented. Until then, "full cross-provider coverage" practically means Claude + Gemini, not 3-of-3.
