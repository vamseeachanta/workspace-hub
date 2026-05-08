---
name: Claude Dreaming feature scope
description: Dreaming is a Managed Agents memory-consolidation feature (research preview, announced 2026-05-06); NOT available in Claude Code CLI or Claude.ai consumer chat
type: reference
originSessionId: 4fbe2ee4-0567-4a6d-92ac-42b64da002de
---
**What it is:** "Dreaming" — asynchronous memory consolidation for Claude Managed Agents. Between agent runs, reads the agent's memory store + up to 100 past sessions, merges duplicates, drops stale entries, resolves contradictions, and surfaces recurring patterns (mistakes, converged workflows, team preferences).

**Where it lives:** Managed Agents platform only. NOT Claude Code (the CLI) and NOT Claude.ai (consumer chat). Memory in those two products remains local/file-based and is not touched by Dreaming.

**Access:** Research preview, gated. Request at `platform.claude.com/docs/en/managed-agents/dreams`.

**Supported models:** Opus 4.7, Sonnet 4.6.

**Policies:** `automatic` (consolidations write back without review) or `review-before-apply` (user approves each consolidation before it lands). For engineering memory, review-before-apply is safer — auto-resolution can silently drop a load-bearing memory it perceives as a contradiction.

**Announced:** 2026-05-06 at the Code with Claude conference.

**Why this matters in workspace-hub context:**
The user already hand-curates `MEMORY.md` + `feedback_*.md` + `project_*.md` under `/home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/`. Dreaming solves the same dedupe / contradiction-resolution problem the user is solving manually — but only for Managed Agents, not for this local-file memory. If the user later deploys a Managed Agent (recruiter-triage, worldenergydata report assistant, Gmail-routing agent), Dreaming becomes directly relevant. For the current Claude Code session memory it does not.

**Verification:** Verified 2026-05-07 via claude-code-guide subagent (WebFetch). Sources: platform.claude.com Managed Agents docs, 9to5Mac coverage 2026-05-07, Simon Willison live blog of Code with Claude 2026-05-06.
