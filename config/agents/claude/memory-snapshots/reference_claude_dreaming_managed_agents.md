---
name: Claude Dreaming feature scope
description: Dreaming = async memory consolidation. UPDATE 2026-05-26 — it SHIPPED to Claude Code CLI (v2.1.150, autoDreamEnabled); originally Managed-Agents-only at 2026-05-06 announce
type: reference
originSessionId: 4fbe2ee4-0567-4a6d-92ac-42b64da002de
---
**What it is:** "Dreaming" — asynchronous memory consolidation. Between sessions, reads the memory store + up to 100 past sessions, merges duplicates, drops stale entries, resolves contradictions, and surfaces recurring patterns (mistakes, converged workflows, preferences).

**UPDATE 2026-05-26 (verified against installed binary):** Dreaming is now IN Claude Code CLI as of **v2.1.150** — superseding the original "Managed-Agents-only" scope below. Implementation in the bundled `claude.exe`: `DreamTask` type, telemetry `tengu_auto_dream_{fired,completed,skipped,failed,toggled}`, two prompt variants (a *pruning* pass + a *reflective/synthesis* pass). Gated by `autoDreamEnabled` in settings.json ("overrides the server-side default"). **There is NO manual trigger / `/dream` command — dreaming is fully AUTOMATIC and background-only** (verified by decompiling the binary 2026-05-26). The `autoDream` routine fires when: `autoDreamEnabled` true AND `hours_since_last_consolidation >= minHours` AND `new_Claude_sessions_since_last >= minSessions` (thresholds from the `tengu_onyx_plover` config gate) AND the `.consolidate-lock` is acquirable. It then reads the auto-memory dir + recent sessions and consolidates. Emits `tengu_auto_dream_{fired,skipped(reason:sessions|lock),completed,failed}`. The ONLY manual levers are the settings toggle and (for the cross-provider bridge) running the bridge scripts that write into the auto-memory dir. Concurrency is gated by a `.consolidate-lock` file in the auto-memory dir holding a PID. **Failure mode (hit on this machine):** a dream killed mid-pass leaves a stale dead-PID lock → all future auto-dreams silently `skip`. Lock was stale from 2026-04-08 (dead PID 2959015) until cleared 2026-05-26 — nothing had dreamed in between. Re-check via `ls -la <memdir>/.consolidate-lock` + `kill -0 <pid>`; safe to `rm` when PID is dead. Companion: [[feedback_orphan_lock_doom_loop_monitor_reap]]. Heavy parallel-session/fleet usage makes mid-pass kills (hence stale locks) likely to recur.

**Original scope (2026-05-06 announce, now superseded):** Managed Agents platform only; NOT Claude Code, NOT Claude.ai consumer chat.

**Access:** Research preview, gated. Request at `platform.claude.com/docs/en/managed-agents/dreams`.

**Supported models:** Opus 4.7, Sonnet 4.6.

**Policies:** `automatic` (consolidations write back without review) or `review-before-apply` (user approves each consolidation before it lands). For engineering memory, review-before-apply is safer — auto-resolution can silently drop a load-bearing memory it perceives as a contradiction.

**Announced:** 2026-05-06 at the Code with Claude conference.

**Why this matters in workspace-hub context:**
The user already hand-curates `MEMORY.md` + `feedback_*.md` + `project_*.md` under `/home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/`. Dreaming solves the same dedupe / contradiction-resolution problem the user is solving manually — but only for Managed Agents, not for this local-file memory. If the user later deploys a Managed Agent (recruiter-triage, worldenergydata report assistant, Gmail-routing agent), Dreaming becomes directly relevant. For the current Claude Code session memory it does not.

**Verification:** Verified 2026-05-07 via claude-code-guide subagent (WebFetch). Sources: platform.claude.com Managed Agents docs, 9to5Mac coverage 2026-05-07, Simon Willison live blog of Code with Claude 2026-05-06.
