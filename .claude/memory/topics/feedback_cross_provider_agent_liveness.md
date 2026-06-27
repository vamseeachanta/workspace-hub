> Git-tracked snapshot from Claude auto-memory. Captured: 2026-06-27
> Source: /home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/feedback_cross_provider_agent_liveness.md

---
name: feedback-cross-provider-agent-liveness
description: "Monitoring Claude+Codex+Hermes agents: normalize liveness on the process table/daemon, never on on-disk JSON; each provider's state file lies in a different way"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 08e3d2f3-8ca3-49c2-bc9d-390a767f25fa
---

When building a unified agent monitor across providers (2026-05-25, built
`scripts/monitoring/agents-board.sh` + `monitor-sessions.sh`), the load-bearing
rule is: **liveness is a property of the process table / authoritative daemon,
not of any JSON file.** Each tool's on-disk state misleads in its own way:

- **Claude** — `~/.claude/sessions/<pid>.json` is a real registry (has
  `status: busy|idle`, `cwd`, `startedAt`/`updatedAt`), but filenames are PIDs
  and entries linger after a crash/kill. Trust an entry only if `kill -0 <pid>`
  succeeds. CLI-launched sessions register here too, which is how the Cowork/Code
  desktop sidebar can show terminal sessions.
- **Codex** — has **no liveness registry at all**. `~/.codex/session_index.jsonl`
  is *history* (observed entries 9 days stale). A live agent = a running
  `~/.npm-global/bin/codex` process that is NOT `codex-update-manager daemon`.
  Reading the index as "current" shows phantom agents.
- **Hermes** — `~/.hermes/gateway_state.json` is authoritative for the gateway
  (`gateway_state`, platform health) BUT its `active_agents` counter **diverges
  from reality**: observed `active_agents:0` while a live
  `tui_gateway.slash_worker --session-key … --model …` process existed. Count
  workers via `pgrep`, not the counter. `processes.json` is the worker registry
  (often `[]`); `spawn-trees/<id>/_index.jsonl` holds agent history.

**Why:** trusting the JSON files would have (a) shown 8-day-old Codex threads as
live, and (b) under-counted live Hermes workers because the gateway's own counter
said zero. Process-first detection caught both.

**How to apply:** normalized board contract is `provider · status · ref · age ·
idle · detail`; let columns degrade to `—` per-provider (Codex has no idle
signal) rather than fabricating a value. Age from `ps -o etimes= -p <pid>` for
processes, from `updatedAt` ms-epoch for Claude. Both scripts are read-only
except `monitor-sessions.sh --prune` (removes only dead-PID registry files).

Related: [[feedback-hermes-session-grep-journal-vs-active]] (same discriminator,
Hermes-only), [[feedback_memory_aspire_to_hermes_level]] (cross-provider
consolidation goal), [[feedback_claude_desktop_agent_mode_embeds_cli]].
