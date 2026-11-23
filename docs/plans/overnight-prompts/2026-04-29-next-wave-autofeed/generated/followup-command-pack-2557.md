# #2557 follow-up command pack (DRAFT — operator authorization required)

**Status:** DRAFT. **No GitHub mutations performed by this autofeed worker.** This pack records the recommended command shape for each H1/H2/H4 follow-up; the operator decides whether/when to run.

The pack is written to be executable by the future H4 allowlisted-comment-only executor (`scripts/govern/exec-safe-command-pack.sh`) — every command is `gh issue comment <NNNN> --body-file <path>`.

## Recommended actions (in order)

### 1. Comment on #2479 with H1 preflight pin proposal

```
gh issue comment 2479 --body-file docs/plans/overnight-prompts/2026-04-29-next-wave-autofeed/generated/followup-h1-codex-cli-pin.md
```

**Rationale:** H1 is covered by #2479 per the report's own duplicate-of analysis. Filing as a new issue would create a duplicate. Comment includes the preflight pin sketch and the scope caveat (un-sandboxed terminal only).

**Operator pre-action:** strip the DRAFT header from the file before commenting (or use a `sed` redirect to a temp file).

### 2. Comment on #2519 with H2 drain-ready proposal

```
gh issue comment 2519 --body-file docs/plans/overnight-prompts/2026-04-29-next-wave-autofeed/generated/followup-h2-drain-ready-queue.md
```

**Rationale:** Duplicate-of check inconclusive between standalone filing vs. absorption into #2519's Hermes-orchestration scope. Asking via comment lets the user decide.

### 3. Comment on #2519 with H4 allowlisted-executor proposal

```
gh issue comment 2519 --body-file docs/plans/overnight-prompts/2026-04-29-next-wave-autofeed/generated/followup-h4-allowlisted-command-pack-executor.md
```

**Rationale:** Same logic as #2 — coordinate with the orchestration umbrella before filing a separate issue.

## What this pack does NOT do

- Does NOT file any new issue (per the autofeed prompt's "do not create new issues unless duplicate checks are conclusive").
- Does NOT mutate any label.
- Does NOT promote any plan to `status:plan-review` or `status:plan-approved`.
- Does NOT send outreach.

## What the operator should do before running

1. Read each draft body and decide whether the comment is correct as-is, needs trimming, or should be re-routed to a different issue.
2. If H2 or H4 should be filed as new issues (operator's call after #2519 review), use:
   ```
   gh issue create --title "<title from draft>" --body-file <draft path> --label "<label set>"
   ```
3. After commenting, **also re-run** `bash scripts/review/plan-review-fanout.sh docs/plans/2026-04-29-issue-2557-weekly-productivity-flow-hacks.md` from a plain terminal to land Codex/Gemini reviews against the corrected report (the autofeed session could not dispatch them).
