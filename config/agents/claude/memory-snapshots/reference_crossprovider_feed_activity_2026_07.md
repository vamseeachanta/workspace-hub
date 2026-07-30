---
name: reference_crossprovider_feed_activity_2026_07
description: "As of 2026-07-11 only Claude+Codex actively feed the cross-provider dream; Gemini dormant since 07-07, Hermes daemon-alive but no new conversation sessions since 06-10 — so distiller learnings=0 for those two is expected, not a bug"
metadata: 
  node_type: memory
  type: reference
  originSessionId: acc706a9-81c2-44f9-bdd1-a7840f58259d
---

Session-activity snapshot from the 2026-07-11 fleet assessment (dev-primary / ace-linux-1). Point-in-time — **re-verify before relying**; the useful, durable part is the *method* and the *asymmetry*, not the exact counts.

**Who actually feeds the cross-provider dream (`distill-provider-sessions.py`):**
- **Codex** — ACTIVE. ~3,720 session files, newest 2026-07-11T16:00, ~81 in last 24h. The primary non-Claude feed. Incremental runs distill real new learnings (e.g. 94 from 98 sessions on the 09:05 run).
- **Gemini** — DORMANT since 2026-07-07 (no new `~/.gemini/tmp/.../chats/session-*.jsonl`). Distiller pending≈1, learnings=0. [[crossprovider_codex_gemini-mcp-unavailable-in-non-interactive-ci-con]]
- **Hermes** — daemon ALIVE (`~/.hermes/state-snapshots/` stamped 07-11) but NO new *conversation* session since 2026-06-10. Distiller draws ~0 new learnings from it. Don't read "hermes learnings=0" as a broken bridge — it's an empty queue. [[feedback_hermes_session_grep_journal_vs_active]]
- **Claude** — its own dream ingests its own auto-memory + `~/.claude/projects/*/*.jsonl` natively (316 sessions/24h).

**Why this matters:** the design intent ([[feedback_claude_dream_is_crossprovider_consolidator]]) is a 4-provider consolidator, but in practice mid-2026 the *new-signal* feed is effectively **Claude + Codex**. When a bridge/dream run reports gemini/hermes `learnings=0`, that is the expected steady state (drained backlog + no new sessions), NOT a failure to investigate. A genuine regression would be **codex** going to 0 while its session dir keeps growing.

**How to re-check quickly:** `session-curation-digest-<machine>.md` in `.claude/state/` has a per-provider table (Present / Sessions / Last 24h / Newest); or `find ~/.codex/sessions ~/.gemini/tmp -name '*.jsonl' -printf '%TY-%Tm-%Td %p\n' | sort -r | head`. Hermes state-snapshot mtime ≠ session mtime — check for new *conversation* jsonl, not snapshot manifests.
