# Two-Machine Continuous Parallel Work Dispatch — 2026-04-27

Prepared machine prompts:

1. `docs/plans/machine-prompts/2026-04-27/ace-linux-1-continuous-parallel-work-prompt.md`
2. `docs/plans/machine-prompts/2026-04-27/ace-linux-2-continuous-parallel-work-prompt.md`

## Intended usage

### ace-linux-1

Paste the ace-linux-1 prompt into the primary operator session on ace-linux-1. This prompt makes ace-linux-1 the control plane for:

- Codex usage burn toward ~50% of remaining 24h capacity.
- GitHub issue labels/comments/closures.
- Active lane reconciliation.
- #2518 finish/land recovery.
- Dispatch ledger and final verification.
- Assigning overflow work to ace-linux-2.

### ace-linux-2

Paste the ace-linux-2 prompt into a login shell-backed AI session on ace-linux-2. This prompt makes ace-linux-2 an overflow execution worker for:

- 2–3 Codex implementation lanes in isolated worktrees/clones.
- Validation-only or adversarial review lanes.
- Local result reports for ace-linux-1 to post if `gh auth` is invalid.

## Key split of authority

| Function | ace-linux-1 | ace-linux-2 |
|---|---|---|
| Provider quota and queue control | Primary | Reports local status only |
| GitHub labels/comments/closure | Primary | Only if fresh `gh auth` passes; otherwise report file |
| Codex implementation lanes | 3–5 active lanes | 2–3 overflow lanes |
| #2518 recovery | Primary only | Do not touch |
| Final merge/closeout | Primary | Do not close unless explicitly authorized |
| Worktree isolation | Required | Required |
| Branch force-push | Forbidden | Forbidden |

## Current queue basis captured in prompts

Codex-ready issues from latest provider work queue:

- #2462 — `feat(digitalmodel): repo-wide operator map and canonical routing surfaces beyond OrcaWave/OrcaFlex`
- #2227 — `feat(acma-codes): promote OCIMF Tandem Mooring and CSA Z276 coverage into LLM-wikis`
- #2458 — `feat(canonical-spec): promote named OrcaWave multi-body benchmark fixture for roundtrip and handoff readiness`
- #2464 — `chore(workspace-hub): split curated tier-1 routing index from raw inventory and clean routing noise`

Additional explicit `agent:codex,status:plan-approved` candidates for overflow:

- #2124 — extend ingestion to Orcina resources/examples/training materials.
- #2125 — auto-refresh ingestion on new Orcina releases.
- #2126 — validate markdown conversion quality across 717 topics.
- #1962 — tier-1 repo ecosystem refactoring audit/plan/execute.

## Current quota basis

From `config/ai-tools/agent-quota-latest.json` at 2026-04-27 12:47:54-05:00:

- Codex: `week_messages=5`, `weekly_limit=1400`, `pct_remaining=100`, source `history.jsonl`.
- Target: burn roughly half of remaining useful capacity over 24h, approximately 700 Codex messages, by maintaining useful parallel lanes instead of synthetic usage.

## Launch reminders

Codex may hang if stdin remains open. If launching under a process manager:

1. Start `codex exec ...` in background.
2. Immediately close stdin for that process.
3. If sandbox fails with `bwrap: loopback: Failed RTM_NEWADDR`, use `--dangerously-bypass-approvals-and-sandbox` only inside an isolated worktree/clone.

## Reconciliation reminders

At each control-plane pass:

- Inspect process liveness.
- Inspect worktree git state.
- Verify branch contains only issue-scoped changes.
- Run targeted validation centrally if worker could not.
- Post evidence to GitHub from ace-linux-1.
- Keep the dispatch ledger current.

## Prompt files are uncommitted until staged by the operator

Suggested commit if desired:

```bash
git add docs/plans/machine-prompts/2026-04-27/
git commit -m "docs(orchestration): add ace-linux continuous work prompts"
git push origin main
```
