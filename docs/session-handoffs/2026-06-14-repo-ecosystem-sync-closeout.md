# Repo Ecosystem Sync Closeout - 2026-06-14

Timestamp: 2026-06-14T08:33:51-05:00

## Scope

Wind down the local repo ecosystem after the multi-hour sync/cleanup session:

- merge/preserve completed work on `main`
- prune stale worktrees and stale merged branches
- avoid stash use
- avoid work loss
- document anything that remains approval-gated

## Completed

- `workspace-hub` is on `main` at `2d8685e3387637cdcee88caf6b6d025ce90c378e`.
- `llm-wiki` is on `main` at `14c8521dc2566428c87fedc31621c82e1b370e70`.
- `llm-wiki` PRs merged during the cleanup wave:
  - #686, #687, #688, #689
- Stale `llm-wiki` auxiliary worktrees were removed.
- Stale merged `llm-wiki` local/remote branches were pruned after PR/issue checks.
- Remaining behind repos were fast-forwarded with `git pull --ff-only --prune`:
  - `aceengineer-strategy`
  - `assethold`
  - `assetutilities`
  - `deckhand`
  - `digitalmodel`
  - `worldenergydata`
- Obvious generated cache directories were removed across first-level repos:
  - `.pytest_cache/`, `.ruff_cache/`, `.mypy_cache/`, `.uv-cache/`
  - `.venv/`, `.venv-manim/`, `.venv-test/`
  - `.workflow_cache/`, `.baseline-cache/`
  - `workspace-hub/examples/claude-code-course/uigen/.next/`

## Verified State

Final repo table after fetch/prune, fast-forward pulls, and cache cleanup:

| Repo | Branch | Tracked | Untracked | Stash | Behind | Ahead | Worktrees |
|---|---:|---:|---:|---:|---:|---:|---:|
| CAD-DEVELOPMENTS | main | 0 | 1 | 0 | 0 | 0 | 1 |
| aceengineer-admin | main | 0 | 1 | 0 | 0 | 0 | 1 |
| aceengineer-strategy | main | 0 | 0 | 0 | 0 | 0 | 1 |
| aceengineer-website | main | 0 | 2 | 0 | 0 | 0 | 1 |
| achantas-data | main | 0 | 8 | 0 | 0 | 0 | 1 |
| achantas-media | main | 0 | 0 | 0 | 0 | 0 | 1 |
| assethold | main | 0 | 3 | 0 | 0 | 0 | 1 |
| assetutilities | main | 0 | 0 | 0 | 0 | 0 | 1 |
| deckhand | main | 0 | 0 | 0 | 0 | 0 | 1 |
| digitalmodel | main | 0 | 3 | 0 | 0 | 0 | 1 |
| hobbies | main | 0 | 4 | 0 | 0 | 0 | 1 |
| kaggle-rogii-2026 | main | 0 | 2 | 0 | 0 | 0 | 1 |
| llm-wiki | main | 0 | 5 | 0 | 0 | 0 | 1 |
| llm-wiki-acma | main | 0 | 0 | 0 | 0 | 0 | 1 |
| llm-wiki-fdas | main | 0 | 3 | 0 | 0 | 0 | 1 |
| raw-to-knowledge-playbook | main | 0 | 1 | 0 | 0 | 0 | 1 |
| sabithaandkrishnaestates | main | 0 | 2 | 0 | 0 | 0 | 1 |
| teamresumes | main | 0 | 8 | 0 | 0 | 0 | 1 |
| workspace-hub | main | 0 | 18 | 0 | 0 | 0 | 1 |
| worldenergydata | main | 0 | 17 | 0 | 0 | 0 | 1 |
| worldenergydata-wiki | main | 0 | 1 | 0 | 0 | 0 | 1 |

Process/worktree probes:

- No targeted stale worktree siblings found under `/mnt/local-analysis`.
- `/mnt/local-analysis/worktrees` is empty.
- No targeted `/tmp` worktree/review leftovers found for `wt-vbatch-*`, `wt-index-*`, `wt-pr*`, `vision-review-*`, or `issue1579-plan-r*`.
- No active `plan-review-fanout`, `issue1579-plan`, `legal-sanity-scan.sh`, or stale worktree processes remained after terminating the full legal-scan attempt.
- No `.cleanup-lock` or `.cleanup-trash` residue found.

## Active Preserved Branch

`llm-wiki` still has one local non-main branch:

- `chore/dedup-verification-queue-291` tracking `origin/chore/dedup-verification-queue-291`

This is active preserved work, not a stale branch. It maps to draft PR #685 / issue #291 and was not deleted.

## Remaining Untracked Residue

The remaining untracked files are not simple caches. They are local planning/agent state, evidence/data, generated examples, or repo-specific artifacts. They were preserved in place to avoid work loss.

Representative remaining paths:

- Local planning/agent state: `.planning/`, `.agent-os/`, `.agents/`, `.codex/`, `.claude/checkpoints/`, `.claude/agent-memory/`
- Evidence/data outputs: `docs/email/attachments/`, `docs/email/review/`, `docs/email/spreadsheets/`, `data/modules/`, `data/standards/`, `logs/overnight/`
- Generated/reporting/example content: `.benchmarks/`, `modules/reporting/examples/`, `assets/img/case-studies/`, `tests/modules/`
- Repo-specific unusual paths requiring inspection:
  - `assethold/src\\assethold\\tests\\test_data\\analysis\\Portfolio\\results\\Data/`
  - `digitalmodel/D:\\workspace-hub\\digitalmodel\\docs\\charts\\phase2\\ocimf/`

## Approval-Gated Next Step

To make every first-level repo untracked-clean, run a separate preservation pass:

1. Generate a manifest of every remaining untracked path.
2. Archive non-derived/evidence-bearing content into `workspace-hub/docs/sessions/archives/`.
3. Commit the manifest and checksum, not the archive by default.
4. Move archived paths out of repo working trees only after the manifest/checksum verify.
5. Re-run the ecosystem summary table.

This needs explicit approval because it moves local-only files out of repo working trees. The current state is synced and non-divergent, but not sterile/untracked-clean.
