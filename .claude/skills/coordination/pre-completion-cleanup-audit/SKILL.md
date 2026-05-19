---
name: pre-completion-cleanup-audit
description: Audit and dispose of session residue (orphan files, scratch dirs, sibling-repo state, locks, trash-stages) BEFORE claiming a task complete. Required gate before any agent says "all done", "task complete", or hands work back to user/orchestrator.
when_to_use: '- About to report "task complete" / "done" / "ready for review"

  - Hermes receives a completion signal from a Claude/Codex/Gemini sub-agent and is about to relay it upward

  - End of any session that touched files outside the canonical repo working tree

  - After running tools that may leave artifacts (cleanup operations, archive workflows, codex-burn runs, multi-repo fanouts)

  - Before creating a PR or running ``/ship``-style commands

  '
tags:
- session-hygiene
- closeout-gate
- hermes-orchestration
- residue-audit
- post-task-cleanup
---

# Pre-completion cleanup audit

A required gate before claiming task completion. Surfaces residue that would otherwise accumulate and force later remediation passes (see `operations/mnt-analysis-cleanup` for the heavyweight version that runs after this has been skipped enough times).

## Why this exists

Sessions accumulate four categories of residue that aren't always visible from the immediate task:

1. **In-repo working-tree drift** — uncommitted changes, untracked files, stashes, leftover `.tmp/` or `.partial` artifacts from interrupted operations
2. **Sibling-of-canonical accumulations** — `/mnt/local-analysis/` siblings, outer-clone duplicates, orphan worktrees
3. **Scratch artifacts** — `/tmp/<session-id>/` files, ad-hoc patches in unusual locations
4. **State markers** — `.cleanup-lock`, `.cleanup-trash/`, abandoned `*.partial` files, half-completed two-phase deletes

Each category has its own remediation skill. This skill's job is **detection**, not full disposition — it surfaces what exists, the agent decides what's required.

## The audit (Iron Law: report, don't auto-delete)

Run these in order. Each step is a single grep/find/ls; combined runtime should be under 10 seconds.

**Pipefail pitfall:** if you run the audit inside `set -euo pipefail`, `find ... | head` and similar early-closing pipelines can exit `141` from SIGPIPE even though the audit succeeded. Use `sed -n '1,20p'` or wrap the pipeline with `|| true` for report-only probes; cleanup audit commands should surface residue, not fail the closeout because `head` closed the pipe.

### 1. Repo working-tree state
```bash
cd <canonical-repo>
git status --short
git stash list
find . -name '*.partial' -o -name '*.tmp' 2>/dev/null | head
```

### 2. Sibling-of-canonical state (only when canonical repo is under `/mnt/local-analysis/` or analog)
```bash
ls -la <repo-parent-dir>
# Cross-reference each non-canonical entry against the mnt-analysis-cleanup taxonomy
```

### 3. Scratch artifacts under /tmp
```bash
find /tmp -maxdepth 3 -user "$USER" -mmin -240 -type f \
  ! -path '*/claude-*/tasks/*' ! -path '*/snapshot-*' 2>/dev/null | head
```
(Exclude harness-managed paths; surface only user-meaningful scratch.)

### 4. Lock/trash-stage state
```bash
ls /mnt/local-analysis/.cleanup-lock 2>/dev/null
ls -la /mnt/local-analysis/.cleanup-trash/ 2>/dev/null | head
```

### 5. Session-local handoff/session-doc state
```bash
git status --short docs/sessions/ docs/session-handoffs/ 2>/dev/null
```

## Verdict format

Report to the upstream consumer (user or orchestrator) in three buckets:

| Bucket | Meaning | Required action |
|---|---|---|
| **CLEAN** | No residue surfaced | Proceed to "all done" |
| **EXPECTED** | Residue exists but is expected output of the task (e.g., a new handoff doc not yet committed) | Surface explicitly; "all done" allowed with the residue named |
| **UNEXPECTED** | Residue exists that doesn't trace to the requested task | Block "all done"; route to remediation (commit, archive, delete, or escalate) |

Never report "all done" with **UNEXPECTED** residue present.

## Hermes flow-through integration

When Hermes orchestrates sub-agents (Claude/Codex/Gemini), Hermes SHOULD run this audit on every sub-agent completion signal before relaying "done" to the user:

1. Sub-agent sends `task_status: complete` over the gateway
2. Hermes pauses the completion signal
3. Hermes invokes this skill's audit checklist via `bash -lc '<inline-script>'`
4. If CLEAN → relay completion
5. If EXPECTED → relay completion + append a "residue surfaced" annotation
6. If UNEXPECTED → dispatch back to the sub-agent: "audit found residue; resolve before completion"

The Hermes-side hook is tracked in workspace-hub issue (file follow-up: cleanup-audit-flow-through).

## When NOT to run

- Trivial single-tool-call tasks (e.g., "show me the diff") — overhead exceeds value
- Mid-task checkpoints — only run before *completion*, not between steps
- Inside subagent contexts that report back to a main session — let the main session run the audit once, not N times

## Adjacent skills

- `operations/mnt-analysis-cleanup` — heavyweight retroactive cleanup when this audit has been skipped repeatedly
- `workspace-hub-learned/full-branch-cleanup-and-worktree-hygiene` — branch/worktree-specific
- `workspace-hub-learned/blocked-branch-preserve-tag-cleanup` — when preservation is needed before cleanup
- `github/github-issue-closeout-race-safe` — closeout sequencing for GH issues specifically

This skill is the *trigger upstream of all of them*: detect what exists, then route to the right disposition skill.
