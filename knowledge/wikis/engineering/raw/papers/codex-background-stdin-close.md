# Archived Skill: `codex-background-stdin-close`

Original path: `/home/vamsee/.hermes/skills/autonomous-ai-agents/codex-background-stdin-close`
Archived into: `/home/vamsee/.hermes/skills/.archive/umbrella-2026-04-29/autonomous-ai-agents/codex-background-stdin-close`
Consolidation date: 2026-04-29

---

---
name: codex-background-stdin-close
description: Launch Codex CLI background runs in Hermes when Codex hangs at `Reading additional input from stdin...`; use explicit process stdin close and isolated worktrees.
version: 1.0.0
author: Hermes Agent
tags: [codex, hermes, background-process, stdin, orchestration]
related_skills:
  - codex
  - workstation-aware-provider-orchestration
---

# Codex Background Stdin Close Pattern

## Class of task

Use this skill when launching non-interactive Codex CLI execution from Hermes, especially for long-running implementation lanes or quota-burn batches in isolated worktrees.

## Trigger conditions

- `codex exec ...` prints `Reading additional input from stdin...` and appears to hang.
- `< /dev/null`, an empty pipe, or PTY launch does not make Codex proceed.
- The task is a background Codex implementation/review lane that should continue while Hermes does other work.
- Multiple Codex lanes are running and duplicate/stale launches must be avoided.

## Reliable Hermes launch pattern

1. Put the prompt in a file when it is long:
   ```bash
   cat > /tmp/codex-issue-NNN.md <<'EOF'
   ...self-contained prompt...
   EOF
   ```

2. Launch Codex as a Hermes-tracked background process, without shell stdin redirection:
   ```python
   terminal(
     command='codex exec -c model_reasoning_effort="high" --dangerously-bypass-approvals-and-sandbox --cd /path/to/worktree "$(cat /tmp/codex-issue-NNN.md)"',
     background=True,
     notify_on_complete=True,
   )
   ```

3. Immediately close stdin for the returned session:
   ```python
   process(action='close', session_id='proc_...')
   ```

4. Monitor with:
   ```python
   process(action='poll', session_id='proc_...')
   process(action='log', session_id='proc_...', limit=200)
   ```

5. If the run remains stuck at the stdin message, kill the Hermes process session and relaunch once with the same pattern. Do not launch duplicates before checking OS-level `ps`, worktree git state, and logs.

## Scope and safety rules

- Use isolated worktrees/clones for each issue lane.
- Verify the issue is `status:plan-approved` before implementation; otherwise do planning/review only.
- Use `--dangerously-bypass-approvals-and-sandbox` only when the user has authorized autonomous execution and the worktree scope is isolated. Record the sandbox failure reason, such as `bwrap: loopback: Failed RTM_NEWADDR`.
- Do not force-push.
- Require final output or handoff to include issue number, branch, commit SHA(s), validation commands/results, push status, issue URL, and blockers.
- On remote/overflow machines, CLI presence and auth files are not enough. Before assigning a Codex burn lane, run a tiny real `codex exec` smoke through the same login shell/launch path. A worker may have `codex --version` and `~/.codex/` present but still fail with `401 Unauthorized` / `Failed to refresh token: refresh token was already used`.
- If a remote worker falls back to Claude and produces a branch for an issue that another Codex lane also touched, do **not** push blindly. First compare commit/file scope against the already-pushed branch and choose one canonical branch/PR; treat the other as a salvage/reference artifact.

## Why this exists

In workspace-hub on 2026-04-27, Codex CLI 0.125 repeatedly hung at `Reading additional input from stdin...` with `< /dev/null`, `printf "" |`, and PTY launches. Starting the run as a Hermes background process and explicitly closing stdin with `process close` allowed it to proceed.
