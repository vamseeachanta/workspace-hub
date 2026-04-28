> Git-tracked snapshot from Claude auto-memory. Captured: 2026-04-28
> Source: /home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/feedback_codex_sandbox_write_blocked.md

---
name: Codex sandbox cannot write local files
description: Codex subagent sandbox blocks filesystem writes ("bwrap: loopback" error), even for pushed artifacts — review findings must be captured inline or via GitHub comments
type: feedback
originSessionId: 9b439b61-1bc0-4c85-b9a9-727564b48494
---
Codex subagent (codex:rescue, codex:codex-rescue) runs in a sandbox that blocks `apply_patch` and shell-write operations to the local filesystem with errors like `bwrap: loopback: Failed RTM_NEWADDR: Operation not permitted`.

**Why:** This is separate from the read-side issue captured in `feedback_codex_needs_pushed_artifact.md`. Pushing the plan to GitHub lets Codex READ the artifact (via GitHub connector), but WRITING the review output to the local filesystem still fails.

**How to apply:** When dispatching Codex for adversarial review:
1. Push the plan to GitHub BEFORE dispatch (so Codex can read it).
2. Capture Codex findings in the agent's RETURN TEXT — do not rely on the artifact file path you gave it.
3. After the agent returns, manually create the `scripts/review/results/YYYY-MM-DD-plan-NNN-codex.md` file yourself using the text the agent returned.
4. Do not re-dispatch expecting the write to succeed the second time — the sandbox restriction is persistent.

Observed twice on issue #2342 adversarial reviews (v1 on 2026-04-17, v2 on 2026-04-19). Both rounds: Codex returned a detailed verbal review but could not write `scripts/review/results/*-codex.md`.
