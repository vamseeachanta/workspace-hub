# Worktree / Branch Closeout Ledger — 2026-05-02

## Purpose

Close out the remaining local worktree and branch debt after the #2544/#2567 preserved-branch PR collapse, while preserving evidence for anything not safe to delete.

## PR merge evidence

Fresh GitHub verification showed both preserved issue branches were merged to `main`:

| PR | State | Merged at | Merge commit | Head branch | Head OID |
|---:|---|---|---|---|---|
| #2583 | MERGED | 2026-05-02T11:23:56Z | `65129e2b855d4ebc86fa5f1a9c32bbf3ff1a5b53` | `codex/issue-2544-woodfibre-pointer-v2` | `ec1a3d728cb30325156876515bf3c3f5fe83ac26` |
| #2584 | MERGED | 2026-05-02T11:24:10Z | `dcc315e8cd674984e7654ecb9771e2590ce2df68` | `codex/issue-2567-standards-rudder-v2` | `781510448bdcd8dbece10bcefe18cdf6fe8aeda3` |

## Removed contained worktrees / branches

After Git recovered from earlier status/diff hangs, the following local branches were verified zero-unique and contained in `origin/main` before cleanup:

| Branch | Head prefix | `origin/main..branch` | Result |
|---|---:|---:|---|
| `integration/main-2544-2567` | `641d96dac4fb` | 0 | worktree removed; branch deleted |
| `codex/issue-2544-woodfibre-pointer-v2` | `ec1a3d728cb3` | 0 | worktree removed; branch deleted |
| `codex/issue-2567-standards-rudder-v2` | `781510448bdc` | 0 | worktree removed; branch deleted |

Removed worktrees:

- `/mnt/local-analysis/agent-worktrees/workspace-hub-integration-main-2544-2567`
- `/mnt/local-analysis/agent-worktrees/workspace-hub-issue-2544`
- `/mnt/local-analysis/agent-worktrees/workspace-hub-issue-2567`

## Removed detached nightly worktree

Detached worktree:

- `/mnt/local-analysis/worktrees/nightly-batch-2-20260502T050847Z`

Verification before removal:

- HEAD: `9b1e0ebda803e3dbf8b6566efa7ad9a042df481f`
- Branch: detached
- `origin/main..HEAD`: 0
- `HEAD` ancestor of `origin/main`: yes
- Active process CWD: none found
- Only dirt: untracked `.claude/state/session-signals/2026-05-02.jsonl`

The generated session-signal dirt was preserved in stash:

- `closeout-preserve-nightly-detached-generated-state-20260502T161436-0500`

Then the detached nightly worktree was removed.

## Remaining registered worktrees

Remaining registered worktrees after cleanup:

```text
/mnt/local-analysis/workspace-hub                                            bd427a408 [main]
/mnt/local-analysis/workspace-hub/.claude/worktrees/agent-a3925cd343bf6d44d  2bb38a27e [worktree-agent-a3925cd343bf6d44d] locked
/mnt/local-analysis/workspace-hub/.claude/worktrees/agent-a3ad56da104fdfd57  dcc315e8c [worktree-agent-a3ad56da104fdfd57] locked
```

The two `.claude/worktrees/agent-*` entries are intentionally preserved because they are locked agent-owned worktrees.

## Root repository state before this ledger commit

Fresh state before committing this ledger:

- Branch: `main`
- HEAD: `bd427a408`
- `origin/main`: `bd427a408`
- ahead/behind: `0\t0`
- `.git/index.lock`: absent
- active rebase: absent

Root checkout still had unrelated/generated or concurrent-work dirt. It was not folded into this closeout commit:

```text
 M .claude/state/corrections/.edit_sequence_counter
 M .claude/state/corrections/.recent_edits
 M .claude/state/session-signals/2026-05-02.jsonl
 M docs/plans/2026-05-02-issue-2559-ocimf-tandem-wiki-source-promotion.md
?? .claude/state/corrections/session_20260502.jsonl
?? docs/plans/2026-05-02-issue-2580-quality-gates-followups.md
?? docs/plans/2568-turning-circle-estimator-plan.md
?? docs/plans/overnight-prompts/2026-04-28-elements-wave/README.md
?? docs/plans/overnight-prompts/2026-04-28-elements-wave/child-issue-drafts/
?? docs/plans/overnight-prompts/2026-04-28-elements-wave/morning-synthesis.template.md
?? docs/plans/overnight-prompts/README.md
?? docs/reports/2568-plan-r1-adversarial-review.md
?? docs/reviews/2026-05-02-issue-2580-r1-adversarial.md
?? docs/sessions/2026-05-02-collect-ignore-cumulative-audit.md
?? knowledge/wikis/engineering/wiki/standards/ocimf-tandem-mooring.md
?? scripts/review/results/.failed-fanout-2026-05-02/
?? tests/knowledge/test_ocimf_tandem_no_raw_pdf_text.py
```

## Closeout rule reinforced

Issue closure must be transactional in the same closeout window:

1. verify PR merged or branch contained in `origin/main`;
2. push any final evidence to origin;
3. remove or explicitly preserve worktree;
4. delete local branch only after containment proof;
5. record remaining dirty files / locked worktrees;
6. verify `HEAD == origin/main` and ahead/behind `0\t0`.

Closing first and cleaning later is what created the stale files, stale branches, and preserved worktree backlog.
