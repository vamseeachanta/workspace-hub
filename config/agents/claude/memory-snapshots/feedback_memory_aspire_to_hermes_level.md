---
name: feedback-memory-aspire-to-hermes-level
description: "User feedback 2026-05-17 — All AI provider work should flow through Hermes agent's memory strategy. Hermes-memory is the canonical backend; per-provider memory stores (Claude Code auto-memory, Codex state, Gemini session memory) should consolidate to Hermes rather than evolve in parallel. Originally framed as 'Claude Code memory should match Hermes' then refined same-session to the broader cross-provider architectural ask."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 232a32a4-c42b-48c1-96d9-2f5f1c95a9fd
---

User feedback recorded 2026-05-17 (in two refinements):

**First framing**: Claude Code's memory system should work as good as the user's Hermes agent's memory system.

**Second (refined) framing**: All AI providers' memory should work as good as Hermes — and specifically, **all AI provider work should flow through Hermes agent's memory strategy** (Hermes as the canonical memory backend, not parallel per-provider improvements).

**Why:** The user runs Hermes (their own multi-agent orchestrator — see [[project_hermes_installation]], [[feedback_hermes_active_preflight_check]], [[feedback_hermes_provider_openai_codex_routes_via_codex_exec]], etc.) which already routes work across providers (Claude Code, Codex, Gemini) per cost + quota. The natural extension: Hermes should also be the memory layer that all those providers read from and write to, so cross-provider work has coherent state rather than each provider starting cold relative to the others.

The current state is fragmented:
- Claude Code auto-memory lives at `~/.claude/projects/<project>/memory/` (local-machine-per-project)
- Codex has its own state at `~/.codex/` (separate)
- Gemini has its own session memory (separate)
- Hermes presumably has a unified memory store but other providers don't write to it

A Claude session learns something → Codex doesn't know. Codex resolves a problem → Claude doesn't know. Gemini surfaces a defect → neither Claude nor Codex carries that learning forward. The user is doing manual cross-provider memory propagation today via handoffs / explicit context restatement.

The architectural ask: collapse the per-provider memory silos. Hermes is already the orchestration layer; extend it to be the memory layer too. Per-provider invocations become "Hermes-mediated agent calls with Hermes-managed memory context" rather than "agent calls with per-provider local state".

**Sharpening directives added 2026-05-17 (post-approval clarification)**:

1. **Historical-memory consolidation is in scope.** Not just future writes go to Hermes — the existing per-provider accumulated history migrates in too. Concretely:
   - All existing Claude Code auto-memory files at `~/.claude/projects/<project>/memory/` (this file inclusive — bootstrapping irony noted) → into Hermes
   - All existing Codex state at `~/.codex/` → into Hermes
   - All existing Gemini session-memory exports → into Hermes
   - Migration loses no prior context; history is preserved with provenance

2. **Canonical memory goes with the repo ecosystem — i.e., should be in GitHub.** This is a major architectural sharpening:
   - Hermes canonical memory is **git-tracked**, not local-machine-only or in a private opaque store
   - **Cross-machine sync via standard git pull/push** rather than custom sync protocol
   - **Public-vs-private memory layering via repo visibility** — public repos hold public-safe memories (engineering lessons, tool quirks, generic feedback); private repos hold client-confidential / personal / employer-internal memories. Governance for what goes where mirrors existing per-repo data-routing rules (per `feedback_offrepo_intel_routing` and `feedback_service_provider_data_routing`).
   - **Discoverability via standard repo workflows** (browsing, forking, search) rather than agent-specific tooling
   - **Conflict resolution = git merge semantics** rather than custom conflict-resolution
   - **Format**: git-friendly (markdown/yaml/json), not opaque binary

   Implication for the bootstrap memory base: existing local-only auto-memory files (like this one) are pre-migration artifacts. Migration plan (#2736) covers their move into the repo-tracked canonical store.

**Follow-ups filed (2026-05-17)**: workspace-hub issues #2733 (umbrella epic) + #2734 (Hermes memory audit) + #2735 (write/read API design for non-Hermes providers) + #2736 (migration plan from per-provider stores). All `status:plan-review` awaiting user approval. Sequence: #2734 first (audit) → #2735 + #2736 in parallel after #2734 lands. Each sub-issue references the architectural ask in this memory.

**How to apply:**

1. **When the user critiques memory behavior** (memory file not retrieved when it should have been; memory base failed to surface relevant prior context; auto-memory updates didn't propagate; cross-session continuity broke down; cross-provider context didn't transfer), take it seriously — they have a directly-comparable better system in daily use, so the critique is grounded.

2. **When working on memory-adjacent improvements** (writing or refining feedback files, MEMORY.md curation, retrieval framing in prompts, cross-session handoff design, cross-provider context briefing), aim higher than "good enough" — the bar is "good as Hermes". Specifically:
   - Better discoverability of relevant memories at the right moment in a session
   - Better automation of capture (less reliance on Claude noticing-and-writing)
   - Better cross-machine sync (Hermes presumably handles this; Claude auto-memory is local-machine-per-project)
   - Better cross-provider sync (Claude / Codex / Gemini learnings should be unified, not siloed)
   - Better retrieval signal (relevant memories surface without explicit hinting)

3. **When working on cross-provider tasks** (a session involves both Claude and Codex via `codex exec`; a Hermes-routed task dispatches to Gemini; a workstream straddles multiple providers): the IDEAL is that Hermes is the memory backend mediating context for all of them. The CURRENT reality is that each provider has its own local state and context-passing happens via the user (explicit restatement) or via pushed git artifacts (Codex GitHub-connector pattern per [[feedback_codex_needs_pushed_artifact]]). Treat the current pattern as a workaround, not the target — when designing handoffs and dispatch prompts, structure them so a future Hermes-mediated-memory architecture would absorb them cleanly.

4. **When the user asks "is this in memory?" or "do you remember X?"**: lean toward checking AND surfacing the check transparently, not assuming retrieval already happened. Hermes-bar likely means proactive verification.

5. **When drafting feedback or evaluation of memory tooling itself**: cite this aspiration as the user's view; don't soften it to "memory could be improved" — the user's prescription is specific (Hermes as canonical memory backend for all providers), not vague.

6. **When the user proposes deprecating per-provider memory stores** (Claude auto-memory, Codex `~/.codex/` state, Gemini session memory): don't resist on grounds of "but Claude's memory is useful" — the user's stated architecture has those subsumed by Hermes, not living alongside Hermes.

**What I don't yet know (placeholder for enrichment):**

- Specific Hermes memory capabilities that are the bar (need user-side specification)
- Whether Hermes uses a graph database, vector store, structured schema, or other backing store
- Whether Hermes memory is cross-agent-shared (multiple agents read/write a common store) vs per-agent partitioned
- Whether Hermes auto-captures from agent traces vs requires explicit writes
- Whether Hermes has retrieval-time relevance ranking
- How Hermes handles memory staleness / contradiction / supersession
- **What the API/interface looks like for non-Hermes providers to write to Hermes memory** — would Claude Code's auto-memory be replaced by a Hermes-API write, or wrapped, or fed via post-session sync?
- **What the read-side looks like** — when Claude Code starts a session, would it pull relevant context from Hermes memory (and via what discovery mechanism)?
- **How Hermes memory schemas accommodate provider-specific metadata** — Claude might want to record "subagent invocations made", Codex might want "sandbox limitations encountered" — does Hermes have an open schema or fixed structure?
- **What's the migration path for existing per-provider memory** — do existing Claude auto-memory files (like this one) get imported into Hermes, or stay local, or get re-derived from session logs?

The next time the user critiques Claude memory behavior OR mentions Hermes architecture detail, surface this open list — concrete examples of where Hermes did it better would enrich this memory file and make the gap actionable.

**Do NOT apply when:**

- The user is asking about Hermes operational state (installation, machine deployment) — those are [[project_hermes_installation]] / [[feedback_hermes_active_preflight_check]] / related memories, not this aspiration memory
- The conversation is about Hermes-as-execution-layer (workload routing, machine selection) — that's `[[feedback_hermes_provider_openai_codex_routes_via_codex_exec]]` territory

**Related:**

- [[project_hermes_installation]] — Hermes v0.4.0 deployment state
- [[feedback_hermes_active_preflight_check]] — operational pattern for working alongside active Hermes
- [[feedback_hermes_codex_quota]] — Hermes routing / quota interaction
- [[feedback_hermes_provider_openai_codex_routes_via_codex_exec]] — Hermes provider routing

**Filing externally:** if the user wants this surfaced to Anthropic, the canonical path is opening an issue at https://github.com/anthropics/claude-code/issues. This memory captures the local-machine recording; external filing is a separate user-typed action (Claude cannot open issues on Anthropic repos without explicit per-issue user confirmation of body content).
