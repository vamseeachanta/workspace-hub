> Git-tracked snapshot from Claude auto-memory. Captured: 2026-04-28
> Source: /home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/feedback_codex_sandbox_no_execution.md

---
name: Codex sandbox blocks all shell execution, not just writes
description: Codex subagent sandbox (bwrap) cannot execute shell commands at all — not just filesystem writes. Do NOT delegate code implementation, file editing, build/test runs, or git commits to Codex. Use Codex only for short inline-returnable reviews on pushed plans
type: feedback
originSessionId: 9b439b61-1bc0-4c85-b9a9-727564b48494
---
Codex subagent sandbox fails with `bwrap: loopback: Failed RTM_NEWADDR: Operation not permitted` on ANY shell execution attempt — `git status`, `pwd`, `curl`, `sha256sum`, `npm test`, even benign read commands. Previously thought to be "sandbox blocks writes", but broader: it blocks the entire `exec_command` path.

**Consequences:**
- Codex CANNOT implement code (can't edit files, can't run `npm run build`)
- Codex CANNOT run commits (can't `git add`/`git commit`/`git push`)
- Codex CANNOT verify its own findings by running commands
- Codex CAN read files via GitHub connector when plans are pushed
- Codex CAN return inline markdown reviews — but silent-drops if output exceeds roughly 600-1000 words (observed 3x)

**When to use Codex (still valuable):**
- Short adversarial reviews on plans pushed to GitHub, where findings cite file+line
- Cross-provider review payoff — Codex consistently catches defects Claude misses (past-tense drift, legal-authority overreach, citation specificity) because it forces fresh GitHub reads instead of inheriting conversational framing
- Keep Codex prompts tight: "≤600 words", "findings only", "no preamble"

**When NOT to use Codex:**
- Implementation tasks (any file editing, building, running tests)
- Git operations (committing, pushing, branching)
- Long-form reviews (>600 words output)
- Tasks that require executing verification commands
- Plan drafting with resource intel (needs local grep / ls)

**Pattern for multi-agent dispatches:**
- Codex = read-only reviewer on pushed artifacts; tight word limit
- Claude (general-purpose) = everything else, including reviews that need to run JSON Schema through a validator or grep the codebase

**Observed:** 2026-04-20. Track B of a 4-parallel dispatch sent Commit 2 implementation of #2342+#2343 to Codex rescue agent; agent returned 10/10 FAILED — all sandboxed shell probes failed before any work could start. Fallback to Claude general-purpose succeeded immediately.
