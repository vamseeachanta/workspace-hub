---
name: subagent-write-verification
description: Independently verify subagent-claimed file writes with filesystem and git checks before treating the artifact as real, before committing it, and before referencing the path in downstream prompts.
version: 1.0.0
category: workspace-hub-learned
tags: [verification, subagents, trust-but-verify, write-tool, agent-claims, filesystem-proof]
---

# Subagent Write Verification

A subagent's report that it ran `Write` and the tool returned without error is **not** proof the file landed on disk. Several recurring failure modes — silent Write phantoms, sandbox write blocks, isolation worktree drift, working-directory mismatch — produce a clean-looking success summary while the claimed path is empty or absent. This skill is the verification gate the main session must run before believing, committing, or chaining off any claimed write.

## When to Use

- A dispatched agent (Claude subagent, Codex helper, Hermes worker) reports a successful `Write` / `Edit` / file-creation call.
- A planning, doc-writing, or memory-writing agent returns a summary that references new file paths.
- About to commit, reference in a GitHub issue body, or pass the path as input to a downstream agent.
- After context compaction that preserved a summary mentioning created files but not the verification block.
- During audit of an apparently-complete batch: confirming the artifact count matches the agent count.

## Source Provenance

This pattern was extracted from repeated occurrences across Hermes orchestrator session logs:

- `logs/orchestrator/hermes/session_20260501.jsonl` — sessions `20260501_133025_de04d9`, `20260501_133730_f4d221`, `20260501_134118_f7e0fb`, `20260501_134503_d51cba`, and `20260501_135803_ffeb24` all loaded the predecessor skill `verify-claude-run-commit-vs-working-tree-before-closing` before issuing commits, indicating the verification step had to be re-applied per-agent for a single workflow.
- Hard-rule memory `feedback_subagent_write_phantom` (workspace-hub MEMORY.md index entry: "Subagent Write phantom"): two subagents on 2026-05-03 (marine_ops triage draft, solvers/orcaflex triage draft) both reported successful `Write` calls; neither file existed at the claimed path. Recovery cost ~2 turns + downstream prompt resync.
- Codex sandbox class of failures (`feedback_codex_sandbox_write_blocked`, `feedback_codex_sandbox_no_execution`): pushed-artifact reviews report success despite the sandbox blocking filesystem writes entirely, so the failure mode is not exclusive to Claude subagents.

## Verification Procedure

Run these checks in order. Each is bounded — none requires reading the file contents to invalidate a phantom claim.

### 1. Independent `ls` of the exact claimed path

```bash
ls -la <claimed/path/to/file>
```

- Exit `0` with non-zero size → candidate real artifact (continue).
- Exit `2` / `No such file or directory` → phantom. Stop. Re-dispatch with proof-of-write protocol.
- Exit `0` with size `0` → silent truncation. Treat as phantom.

### 2. Size and head sanity

```bash
wc -c <path>
wc -l <path>
head -3 <path>
```

Confirms the file has content, has the expected structural shape (e.g., YAML frontmatter on a SKILL.md), and is not a stub or accidental empty redirect.

### 3. Git visibility check

```bash
git status --short -- <path>
git ls-files --others --exclude-standard -- <path>
```

- If the file is *meant* to be a new tracked artifact: it must appear in `git status` as `??` (untracked) or `A` (staged) — absence here while `ls` shows the file means the path is outside the working tree (e.g., dispatched to a stale CWD or a different worktree).
- If the file is meant to be an *edit* of an existing tracked file: it must appear as `M`. Absence means the agent wrote to a different path than the one it reported.

### 4. Working-tree origin proof

```bash
git rev-parse --show-toplevel
pwd
```

Resolves the most common silent failure: the subagent ran in a different CWD than the main session (sparse overlay, isolation worktree, or an absolute-path mismatch). If the toplevel does not match the path the main session expects, all `ls` results are about a different repo state.

### 5. Re-dispatch on phantom

If steps 1–4 indicate phantom, do **not** patch the gap from the main session unless the user has authorized it. Re-dispatch the original agent with an explicit proof-of-write block in the prompt:

> After your final Write, run and include in your report:
> `ls -la <path>; wc -c <path>; wc -l <path>; head -3 <path>; git status --short -- <path>`
> Treat your task as failed if any of those commands return error or empty output.

The agent's own verification is necessary but not sufficient — main-session re-check (steps 1–4) is still required after the second attempt.

## Verification Checklist

Before treating a claimed write as real, all of the following must hold:

- [ ] `ls -la` shows the file at the exact claimed path with non-zero size.
- [ ] `head -3` shows expected structural prefix (frontmatter, header, opening syntax).
- [ ] `git status --short -- <path>` or `git ls-files --others -- <path>` confirms working-tree visibility.
- [ ] `git rev-parse --show-toplevel` matches the repo the main session is operating in.
- [ ] If multiple files were claimed: each path verified independently — do not generalize from one success.

Only after this checklist passes may the path appear in: commit messages, issue bodies, plan citations, downstream agent prompts, or status summaries to the user.

## Pitfalls

- **Trusting the agent's own verification block alone.** An agent that fabricates a Write summary will also fabricate a plausible `ls` output. Main-session re-execution is what makes the check load-bearing.
- **Generalizing from the first verified file in a batch.** Each path needs its own `ls`. A 6-of-7 phantom rate is plausible when one agent crashes mid-batch.
- **Reading the file before checking visibility.** `Read` against a sparse-overlay path can succeed while `git status` shows nothing — proving the path exists on disk but is invisible to commit. Always check `git status` before believing the artifact is committable.
- **`stat` instead of `ls`.** `stat` follows symlinks and resolves remote-mounted paths; on an isolation worktree it can report a phantom as real because the underlying inode exists elsewhere. `ls -la` shows the symlink target plainly.
- **Skipping verification after context compaction.** Summaries preserve "I wrote file X" but lose the original `ls` evidence; on resume, treat every referenced new path as unverified until re-checked.
- **Applying this to GitHub side-effects.** For issue/PR/label actions, the verification surface is `gh issue view --json` / `gh pr view --json`, not the filesystem. Same trust-but-verify principle, different probe.

## Related Patterns

- `feedback_subagent_write_phantom` (workspace-hub memory) — origin incident.
- `feedback_attestation_enables_contradiction_detection` — broader contradiction-detection principle.
- `.claude/skills/development/artifact-commit-verification/SKILL.md` — companion skill for verifying the *commit* once the file has been verified to exist.
- `feedback_codex_sandbox_write_blocked`, `feedback_codex_sandbox_no_execution` — sandbox-class phantom write modes.
