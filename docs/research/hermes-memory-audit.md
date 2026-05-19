# Hermes memory canonical-backend audit

> **Issue**: [#2734](https://github.com/vamseeachanta/workspace-hub/issues/2734) — research: audit current Hermes agent memory capabilities + identify gaps for canonical-backend role
> **Parent epic**: [#2733](https://github.com/vamseeachanta/workspace-hub/issues/2733) — make Hermes agent memory canonical across all AI providers
> **Auditor**: Claude (Opus 4.7), inline session 2026-05-19
> **Host**: ace-linux-1 (Hermes v0.14.0 / build 2026.5.16)
> **Inspection method**: read live `~/.hermes/` + `scripts/memory/` + `hermes_state.py` on running install + read repo-tracked `config/agents/hermes/` artifacts

## Executive summary

**Verdict: significant gaps before Hermes can serve as the canonical memory backend for non-Hermes providers.**

Hermes has a sophisticated *internal* memory system — SQLite with FTS5 + trigram full-text search, source-tagged sessions, 141,698 messages across 4,055 sessions on this host, 3.4 GB of indexed history. But it is **not externally addressable** as a shared backend: there is no programmatic write or read API for Claude / Codex / Gemini, no semantic search, no provenance in the canonical curated extracts, and cross-machine sync is one-way Hermes→repo→others via git bridge (not real-time).

To become the canonical backend, the most critical gaps to close are:

1. **External write/read API** (HTTP, MCP, or local IPC) so other providers can `mem.put(...)` and `mem.search(...)` against Hermes.
2. **Provenance + supersession schema** on canonical memory facts (agent, session, timestamp, supersedes_id).
3. **Real-time bidirectional sync** that isn't gated on `git commit + git push`.
4. **Semantic search** (vector store) alongside the existing FTS5 text search.

The existing infrastructure is solid groundwork — the SQLite + session model is appropriate, FTS5 works well at this corpus size, and `bridge-hermes-claude.sh` already proves the cross-machine sync pattern (just via git, not in real-time). The canonical-backend role is an **extension** of what exists, not a rewrite.

---

## Live inventory (the empirical baseline)

| Surface | Path | Size on ace-linux-1 | Role |
|---|---|---|---|
| Session + message DB | `~/.hermes/state.db` (+ `-shm`, `-wal`) | 3.45 GB | Per-session full message history; FTS5-indexed |
| Curated memory facts | `~/.hermes/memories/MEMORY.md` | 1.9 KB | Hand-curated cross-session invariants (§-separated bullets) |
| User profile facts | `~/.hermes/memories/USER.md` | 1.2 KB | User preferences + working style |
| Session JSONL archive | `~/.hermes/sessions/` | 2.9 GB across 5,507 files | Pre-state.db format; still written for backward compat |
| Kanban store | `~/.hermes/kanban.db` | (separate SQLite, also WAL) | Project/task state, separate from message memory |
| Hermes binary | `~/.hermes/hermes-agent/venv/bin/hermes` | — | Hermes Agent v0.14.0 (2026.5.16) |
| State module | `~/.hermes/hermes-agent/hermes_state.py` | — | SessionDB Python class, schema v11 |
| Cross-machine sync | `scripts/memory/bridge-hermes-claude.sh` | — | One-way Hermes→repo→all-machines, cron-driven 04:00 daily |
| Curation logic | `scripts/memory/curate-memory.py` | — | Regex-based keep/domain-doc/skill-update/archive classifier |
| Drift check | `scripts/memory/check-memory-drift.sh` | — | Staleness detector |
| Quality eval | `scripts/memory/eval-memory-quality.py` | — | Memory quality metrics |

---

## Axis-by-axis audit

### 1. Storage backing

**Current state:**

- **Primary**: SQLite (state.db, schema v11) in WAL mode with FTS5 + trigram-FTS5 virtual tables.
  - `sessions` table: 4,055 rows on this host. Columns include `id`, `source` ('cli' / 'telegram' / 'discord' / etc.), `user_id`, `model`, `model_config`, `system_prompt`, `parent_session_id` (for compression-triggered splits), `started_at`, `ended_at`, `end_reason`, `message_count`, `tool_call_count`, `input_tokens`, `output_tokens`, `cache_read_tokens`, etc.
  - `messages` table: 141,698 rows. Columns: `id`, `session_id` (FK), `role`, `content`, `tool_call_id`, `tool_calls`, `tool_name`, `timestamp`, `token_count`, `finish_reason`, `reasoning`, `reasoning_details`, `codex_reasoning_items`, `reasoning_content`, `codex_message_items`.
  - `messages_fts` (FTS5) + `messages_fts_trigram` (FTS5 with trigram tokenizer) — fast text + substring search.
  - `state_meta` table: 99 rows of misc key-value state.
- **Curated**: flat Markdown — `~/.hermes/memories/MEMORY.md` + `USER.md`. §-separated facts, very small (~3 KB total), hand-curated by Hermes during sessions.
- **JSONL archive**: 5,507 session files in `~/.hermes/sessions/` (2.9 GB). Pre-state.db legacy format; still written.
- **Kanban**: separate `~/.hermes/kanban.db` for project/task state (not memory per se but adjacent).

**Resilience:** WAL mode for concurrent readers + one writer. Documented fallback to `journal_mode=DELETE` on filesystems where WAL fails (NFS, SMB, some FUSE) — see `hermes_state.py:_WAL_INCOMPAT_MARKERS`. SQLite at 3.45 GB is well within healthy size.

**No vector store.** No graph backing. Semantic queries impossible today; only keyword / FTS / trigram-substring search.

**Gap vs canonical-backend role:**

- ❌ **No vector/embedding store** — canonical backend needs semantic search across "what do I remember about catenary calcs?" type queries that don't share exact keywords.
- ❌ **No graph capability** — entity/relation queries (e.g., "what's connected to ace-linux-1?") would be expensive to express in pure SQLite.
- ✅ FTS5 + trigram is **excellent for keyword/exact-text recall** within Hermes's own sessions; not a gap for that use case.
- ⚠️ **MEMORY.md flat-file format** is human-friendly but lacks structure for programmatic queries by external providers.

### 2. Write surface

**Current state:**

- **Automatic capture**: every message in every session is persisted to `state.db.messages` via `SessionDB.add_message()`. Source is tagged per session ('cli', 'telegram', 'discord', custom). Tool calls + reasoning content captured.
- **Curated writes**: `MEMORY.md` / `USER.md` are explicit Hermes-internal writes via the `memory-bridge-operations` skill (`~/.hermes/skills/memory/memory-bridge-operations/`). Hermes asks itself "should this be a memory fact?" and appends via §-separator.
- **No external write API**: Claude / Codex / Gemini cannot write to Hermes memory programmatically. They have their own per-provider stores (Claude's `~/.claude/projects/<dir>/memory/`, Codex doesn't have a comparable surface, Gemini doesn't either).
- **Bridge writes**: `bridge-hermes-claude.sh` reads Hermes-side files + Claude auto-memory, synthesizes into `.claude/memory/agents.md` + `topics/` mirror, commits to repo. This is a *one-way pull from Hermes + Claude → repo*, run via cron 04:00 daily.

**Gap vs canonical-backend role:**

- ❌ **No external write API** — biggest single gap. Other providers can't write to Hermes. The repo-bridge pattern means Claude's auto-memory gets ingested daily, but Codex + Gemini have no equivalent path in.
- ❌ **No write-time validation** — what stops a malicious or buggy agent from writing 100 GB of garbage? Hermes itself is the writer today; that gates by trust. Multi-provider opens this attack surface.
- ❌ **No deduplication or contradiction detection at write time** — a duplicate fact just gets §-appended.
- ✅ **Source tagging via `session.source`** already exists — good foundation for "this fact came from Claude session XYZ".

### 3. Read surface

**Current state:**

- **In-Hermes slash commands**: `/resume`, `/title`, `/history`, `/branch` operate on `state.db`. Uses FTS5 + trigram-FTS for content search.
- **Curated file reads**: `MEMORY.md` + `USER.md` loaded at session start; full content fed to system prompt (small enough — ~3 KB).
- **No external read API**: other providers don't query Hermes. They read either their own per-provider memory OR the repo-bridged `.claude/memory/` (which is the *snapshot* of Hermes memory at last bridge run, not live).
- **Bridge-mediated reads**: `.claude/memory/agents.md` + `topics/` provide a read surface for ALL providers via git. Stale up to 24 hours (cron cadence). One-way (write-from-Hermes-only).

**Gap vs canonical-backend role:**

- ❌ **No external read API** — second-biggest gap. Other providers need a way to query Hermes for memory facts at runtime, not just consume a daily git-bridge snapshot.
- ❌ **No semantic search** — agents asking "what do I know about X conceptually" hit a wall.
- ❌ **No scope-filtered reads** — e.g., "all facts about catenary calcs" requires keyword match; no entity-typed query.
- ✅ FTS5 + trigram-FTS gives **excellent fast text/substring search** within state.db, accessible to in-Hermes commands.
- ✅ The `bridge-hermes-claude.sh` pattern of "synthesized canonical extract in git" works well for *eventual-consistency* canonical reads.

### 4. Cross-agent shape

**Current state:**

- **Hermes-namespaced today.** All memory is "Hermes memory" — written by Hermes, for Hermes. The bridge script extracts a *subset* (canonical invariants from MEMORY.md / USER.md) into repo for cross-agent visibility.
- **No per-agent annotations.** A fact in MEMORY.md doesn't know which agent (Claude / Codex / Gemini / Hermes) authored it. Per `session.source` in state.db, Hermes knows which UI surface the session came from, but not which AI provider produced any particular fact.
- **Claude auto-memory is separate.** `~/.claude/projects/<dir>/memory/` is per-Claude-project, Claude-managed. Bridge script samples it into `.claude/memory/topics/` for archival but not for query.
- **Codex + Gemini have no comparable memory.** They effectively rely on session context only — no persistent memory layer.

**Gap vs canonical-backend role:**

- ❌ **No multi-agent namespacing** in MEMORY.md / state.db facts. Canonical backend needs a way to say "this fact came from Claude session YYY at time TTT" so contradictions can be source-attributed.
- ❌ **No per-agent scope filter** — "show me only what Claude has written" is impossible today.
- ⚠️ Implicit per-provider stores **fragment** the memory landscape — exactly what #2733 epic exists to fix.
- ✅ The `bridge-hermes-claude.sh` precedent of merging Hermes + Claude into a single repo-tracked surface is the right architecture; it just needs to grow into bidirectional + multi-provider.

### 5. Provenance / attribution

**Current state:**

- **state.db**: every message has `session_id` (→ `session.source` + `started_at`) + `timestamp` + optionally `tool_name` + `model`. Full provenance for raw messages.
- **MEMORY.md / USER.md**: flat §-separated facts. **No provenance markers** — no `@vamsee added`, no timestamps, no source-session-id. Verified empirically: `grep -E "@|by|added|since" ~/.hermes/memories/MEMORY.md` returns nothing.
- **Bridge output (.claude/memory/agents.md)**: synthesized at bridge time with a timestamp at the top, but individual facts don't carry per-fact provenance.

**Gap vs canonical-backend role:**

- ❌ **Curated facts lack provenance.** A fact in MEMORY.md could have been written by Hermes yesterday or could be from 6 months ago — there's no record. Multi-provider canonical store would compound this confusion.
- ❌ **No supersession chain** — when fact B contradicts fact A, both just live in the file. No `supersedes_id`.
- ✅ **Raw message-level provenance is excellent** in state.db. If the canonical-backend schema borrows this (every fact has `source_session_id`, `agent`, `timestamp`), the gap closes cleanly.

### 6. Staleness / contradiction handling

**Current state:**

- **No automatic contradiction detection.** Two contradictory facts in MEMORY.md just coexist. Hermes is expected to read both and use the more recent one — but "more recent" isn't marked.
- **Curation script (`curate-memory.py`)**: regex-based classifier into `memory-keep` / `domain-doc` / `skill-update` / `archive`. Generates a candidates file only; does NOT mutate memory files. Human-in-loop required to actually archive anything.
- **Drift check (`check-memory-drift.sh`)**: detects when repo-tracked memory diverges from Hermes-live memory. Surfaces drift but doesn't auto-resolve.
- **Quality eval (`eval-memory-quality.py`)**: metrics around memory file health.
- **Compaction (`compact-memory.py`)**: presumed to deduplicate / merge — would need to read source for exact behavior.

**Gap vs canonical-backend role:**

- ❌ **No automatic supersession.** A "we now use brew, not apt on macOS" fact should mark the older "apt on macOS" fact as superseded.
- ❌ **No contradiction surface.** When a new fact contradicts an old fact, the system doesn't tell the user "you have two contradictory facts; pick one."
- ❌ **No staleness aging.** A 6-month-old fact about a deprecated tool stays in the file forever unless curated out.
- ✅ **The curation toolchain exists** — `curate-memory.py`, `check-memory-drift.sh`, `eval-memory-quality.py`, `compact-memory.py` are real assets. They need to grow into contradiction-aware logic, but the harness is there.

### 7. Cross-machine sync

**Current state:**

- **Repo-mediated only.** `bridge-hermes-claude.sh` runs on ace-linux-1 (the Hermes host), extracts Hermes memory + Claude auto-memory, writes to `.claude/memory/`, commits + pushes to git. Other machines get the canonical context via `git pull`.
- **Cadence**: cron 04:00 daily on Linux; Task Scheduler 04:30 daily on Windows hosts (where `bridge-hermes-claude.sh` runs in Windows-only mode that skips Hermes-specific steps but mirrors Claude auto-memory).
- **One-way.** Hermes (ace-linux-1) is the source of truth; other machines are read-only consumers. ace-linux-2, licensed-win-1, licensed-win-2 do NOT write back.
- **Real-time?** No. Up to 24h staleness between bridge runs. Plus git push/pull latency.

**Gap vs canonical-backend role:**

- ❌ **One-way sync.** Multi-provider canonical backend needs bidirectional — if Claude on licensed-win-1 writes a fact, Hermes on ace-linux-1 needs to see it. Today licensed-win-1 has no Hermes; bridge only ingests Claude's per-project memory daily.
- ❌ **24h staleness.** Not real-time. For canonical-backend reads, agents will want a fact written 30s ago, not yesterday's snapshot.
- ❌ **Git as transport.** Works but adds friction (commit, push, pull cycles). Doesn't scale to mid-session memory writes.
- ✅ **The pattern is sound.** Repo-mediated sync is `feedback_cross_machine_execution`-compliant ("per-machine tasks via shared git repo, not SSH/rsync") and survives offline scenarios. Should remain as a *fallback path* even when real-time sync exists.
- ✅ **Per-OS scheduler integration** already works (cron + Task Scheduler).

---

## Cross-cutting observations

### What Hermes does NOT have today

- HTTP / MCP / gRPC API surface for external providers.
- Vector embeddings (or any semantic search).
- Entity-relation graph.
- Write-time deduplication.
- Per-fact provenance in the canonical curated extracts.
- Supersession chains.
- Real-time multi-machine state replication.
- Quota / write-rate limits per external writer.
- Privacy/redaction at write time (other than what gets bridged out — see `scripts/operations/agent-execution/collect-machine-baseline.ps1` for the existing `Redact-Text` pattern).

### What Hermes DOES have today (the foundation)

- SQLite at 3.45 GB performing well — proven storage backing.
- FTS5 + trigram-FTS — fast text/substring search at this scale.
- Source-tagged sessions — good foundation for "which agent surface" tracking.
- A full bridge script with cron integration — proves the repo-mediated sync model.
- Curation toolchain (curate / drift-check / eval-quality / compact) — primitive but real.
- Schema versioning (v11) — migration-aware.
- Memory-bridge-operations skill — encodes write conventions.
- WAL fallback for hostile filesystems — production-grade.
- Adjacent `kanban.db` shows the multi-database pattern works.

### Adjacent work that should inform the design

- **#2751 G9 (just landed)**: `config/machine-baselines/<token>.{md,yaml}` registry pattern proves that **per-machine git-tracked state files** work for cross-machine assessment. The canonical-memory schema should align with this — every fact carries a `source_machine` field, the aggregator pulls all of them, drift detection surfaces inconsistencies.
- **`feedback_memory_aspire_to_hermes_level`**: the user's stated direction — "all-provider memory should flow through Hermes." This audit confirms it's possible but non-trivial.
- **`feedback_cross_provider_review_payoff`**: cross-provider review is already a working pattern (`scripts/review/`). A similar pattern for "cross-provider memory write" would land naturally.

---

## Recommendations — highest-leverage gaps to close first

Ranked by leverage / dependency-unblock:

### Priority 1 — External write/read API (unblocks everything)

Without this, no other provider can talk to Hermes memory at runtime. Options:

1. **Local IPC / Unix socket** — Hermes already runs as a daemon on ace-linux-1 (gateway). Add a memory-API endpoint over the existing socket. Lowest latency, requires Hermes process to be local.
2. **MCP server** — implement Hermes-memory as an MCP server. Claude/Codex/Gemini that support MCP can connect natively. Aligns with the ecosystem trajectory.
3. **HTTP + Tailscale** — REST API behind Tailscale for cross-machine access. Higher latency than IPC but works without Hermes-on-every-machine.

**Recommend MCP** for v1 — matches where the ecosystem is going and integrates naturally with existing Claude / Codex MCP clients. Fallback to local IPC for ace-linux-1-internal speed.

### Priority 2 — Per-fact provenance schema in canonical store

Without this, multi-provider memory becomes a confusion engine. Schema additions:

```sql
-- canonical fact table (new)
CREATE TABLE memory_facts (
    id TEXT PRIMARY KEY,                    -- ULID or UUID
    content TEXT NOT NULL,
    source_agent TEXT NOT NULL,             -- 'hermes' | 'claude' | 'codex' | 'gemini'
    source_session_id TEXT,                 -- FK to sessions if source=hermes; else external ID
    source_machine TEXT NOT NULL,           -- 'ace-linux-1' | 'ace-linux-2' | 'licensed-win-1' | etc.
    written_at REAL NOT NULL,
    supersedes_id TEXT REFERENCES memory_facts(id),
    superseded_at REAL,                     -- nullable
    fact_type TEXT,                         -- 'invariant' | 'user_preference' | 'tool_quirk' | etc.
    confidence REAL                         -- 0-1 if computed; null if asserted
);
```

This schema is small and additive. Migration path: read existing MEMORY.md / USER.md, write each §-separated bullet as a row with `source_agent='hermes'`, `source_session_id=NULL`, `source_machine='ace-linux-1'`, `written_at=file_mtime`. One-shot ingestion.

### Priority 3 — Bidirectional + real-time-ish cross-machine sync

The repo-bridge stays as the **eventual-consistency fallback**. Real-time path:

- If the API from P1 is HTTP/MCP behind Tailscale: writes from any machine hit ace-linux-1 directly. Hermes serializes via SQLite WAL writer lock.
- If a machine is offline: queue writes locally, replay on reconnect. Bridge script becomes the catch-up mechanism.

### Priority 4 — Semantic search (vector backing)

Bolt vector embeddings onto the existing schema. Recommend a separate SQLite table with [sqlite-vec](https://github.com/asg017/sqlite-vec) extension OR an embedded vector store (Chroma, LanceDB) keyed by `memory_facts.id`. Embeddings computed at write time (or batched daily for cost).

### Priority 5 — Contradiction-aware curation

Extend `curate-memory.py` to surface contradictions (when two facts in `memory_facts` table refer to the same entity but have conflicting content). Surface in a daily report; user resolves by writing a new fact with `supersedes_id` pointing at the loser.

### Priority 6 — Migration plan from per-provider stores

`#2736` design issue. Inventory what Claude auto-memory + Codex sessions + Gemini history contain that should migrate into the canonical store. One-shot import per provider.

---

## Acceptance check

| Acceptance criterion | Status |
|---|---|
| Audit doc filed at `docs/research/hermes-memory-audit.md` | ✅ This doc |
| All 7 axes covered with current-state + gap analysis | ✅ §1-7 above |
| Recommendations for highest-leverage gaps to close first | ✅ §Recommendations |

---

## Hand-off to downstream design issues

This audit unblocks:

- **[#2735](https://github.com/vamseeachanta/workspace-hub/issues/2735)** — design: memory write/read API for non-Hermes providers. Should consume §Recommendations P1 + P2 as input. Key decision points: MCP vs HTTP vs IPC; schema shape; auth model.
- **[#2736](https://github.com/vamseeachanta/workspace-hub/issues/2736)** — design: migration plan from per-provider stores into Hermes canonical memory. Should consume §Recommendations P6 + the inventory in §1. Key decision points: lossy vs lossless migration; whether to deprecate per-provider stores or keep as read-only mirrors.
- **[#2733](https://github.com/vamseeachanta/workspace-hub/issues/2733)** — parent epic. After #2735 + #2736 land, this synthesizes into a delivery plan.

## References

- Live state: `~/.hermes/state.db`, `~/.hermes/memories/`, `~/.hermes/sessions/`, `~/.hermes/hermes-agent/hermes_state.py`
- Repo-tracked: `config/agents/hermes/SOUL.md`, `config/agents/hermes/memories/`, `scripts/memory/bridge-hermes-claude.sh`, `scripts/memory/curate-memory.py`, `scripts/memory/check-memory-drift.sh`
- Memory rules: `feedback_memory_aspire_to_hermes_level`
- Adjacent design: `config/machine-baselines/` (per #2751 G9, just landed)
- Cross-machine pattern: `feedback_cross_machine_execution`
