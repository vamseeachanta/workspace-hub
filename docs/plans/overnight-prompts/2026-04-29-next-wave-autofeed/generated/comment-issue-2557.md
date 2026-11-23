## Adversarial review (r1, single-author Claude) — 2026-04-29 nextwave

A planning-only autofeed worker ran a single-author Claude adversarial review against the canonical plan and the 14-hack productivity-flow report. **Status remains `draft` — no labels mutated, no follow-up issues filed, no Tier-1 hacks executed.**

### Provider coverage

| Provider | Verdict | Artifact |
|---|---|---|
| Claude (single-author r1) | **MAJOR** | `scripts/review/results/2026-04-29-plan-2557-nextwave-claude.md` |
| Codex | UNAVAILABLE | `scripts/review/results/2026-04-29-plan-2557-nextwave-codex.md` (Bash permission gate + #2479 codex-cli 0.124 stdin-hang) |
| Gemini | UNAVAILABLE | `scripts/review/results/2026-04-29-plan-2557-nextwave-gemini.md` (Bash permission gate; wrapper itself is healthy) |

Multi-provider consensus is **not** established — same permission-gate pattern as the #2556 review.

### Headline blocking findings (3 of 8)

1. **Stale W18 utilization in report TL;DR.** Report cites `claude 6.6%`; live `docs/reports/provider-utilization-weekly.md` (Generated `2026-04-29T09:20:08Z`) shows `claude 5.8%`. The 6.6% figure does not appear anywhere in the current source. Plan and report both repeat the wrong number in TL;DR / friction map / H2 framing.
2. **Stale Codex work-queue numbers.** Report H2 cites "8 ready / 17 routed"; live source shows "18 ready / 41 routed". The hack's underlying inventory data is wrong, and the example issue list under-represents available work by >50%.
3. **H1 owner-time-impact misframed.** H1 ("Pin codex-cli to 0.123.0 in Hermes preflight") is presented as Tier-1 immediate ≈2-3h/week recovered. Per `feedback_codex_cli_0_124_upstream_regression.md` (verified 2026-04-24), 0.123.0 also hangs from inside Claude Code's Bash tool — the pin only restores Codex for plain-terminal invocations, not Hermes-dispatched lanes. Owner-time-impact framing must reflect that scope.

Five additional MINOR-MAJOR findings (stale generation timestamp, stale Claude work-queue numbers, EC-2 internal inconsistency, H10 GTM-split overlap with #2556 brochure outline, ambiguous overnight-prompts canonical location) are in the Claude artifact.

### Follow-up drafts (Tier-1 hacks H1/H2/H4)

Four files written under `docs/plans/overnight-prompts/2026-04-29-next-wave-autofeed/generated/`:

- `followup-h1-codex-cli-pin.md` — recommends commenting on [#2479](https://github.com/vamseeachanta/workspace-hub/issues/2479), not filing new (duplicate).
- `followup-h2-drain-ready-queue.md` — recommends commenting on [#2519](https://github.com/vamseeachanta/workspace-hub/issues/2519) for scope decision.
- `followup-h4-allowlisted-command-pack-executor.md` — recommends commenting on [#2519](https://github.com/vamseeachanta/workspace-hub/issues/2519) for scope decision.
- `followup-command-pack-2557.md` — operator-runnable command pack with all three `gh issue comment` invocations + caveats.

**No new issues filed.** All three drafts include duplicate-of-checks against #2479 / #2519; H1 is conclusively a duplicate of #2479; H2 and H4 are ambiguous between standalone filing and absorption into #2519's scope.

### Recommended next steps (operator)

1. Regenerate the productivity-flow report against freshly-read live sources (especially `provider-utilization-weekly.md`, `provider-routing-scorecard.md`, `provider-work-queue.md`) — the snapshot in the current report is overwritten.
2. Re-frame H1's owner-time-impact estimate against the actual surface the pin restores.
3. Run `bash scripts/review/plan-review-fanout.sh docs/plans/2026-04-29-issue-2557-weekly-productivity-flow-hacks.md` from an un-sandboxed terminal to land Codex + Gemini reviews.
4. Decide for H2/H4 whether to file as new issues or absorb into #2519, and post the H1 comment on #2479.
5. **Do not** flip `status:plan-review` until at least one additional provider returns a structured verdict.
6. **Do not** flip `status:plan-approved` — explicitly forbidden by the autofeed prompt.

### What did NOT happen

- No labels mutated. `#2557` remains `cat:ai-orchestration, cat:business, domain:gtm, priority:high`.
- No follow-up issues filed.
- No Tier-1 hacks executed (the bash permission gate would have blocked them anyway).
- No GitHub mutations of any kind.

### Pointers

- Plan: `docs/plans/2026-04-29-issue-2557-weekly-productivity-flow-hacks.md` (Adversarial Review Summary section refreshed in this wave)
- Reviews: `scripts/review/results/2026-04-29-plan-2557-nextwave-{claude,codex,gemini}.md`
- Follow-up drafts + command pack: `docs/plans/overnight-prompts/2026-04-29-next-wave-autofeed/generated/followup-*.md`
- Result summary: `docs/plans/overnight-prompts/2026-04-29-next-wave-autofeed/results/gtm-review-2556-2557.md`
