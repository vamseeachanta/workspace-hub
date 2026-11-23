<!-- Generated 2026-06-13 by the fable-corpus-analysis workflow (run wf_c5a441ab-18d). Epic #3043 / sub-issue #3056. -->
# Provenance

- **Corpus:** 193 genuine Fable-5 sessions (≥1 `claude-fable-5` assistant turn), **both Linux boxes**: ace-linux-1 = 92, ace-linux-2 = 101. ~17,567 Fable-5 turns total.
- **Method:** deterministic per-session digests (no LLM) → 14 parallel `Explore` characterization agents → 1 synthesis agent. PII-free by construction (digests stayed in /tmp; this report carries no client identifiers).
- **Anchored to ratified decisions:** primary `claude-opus-4-8[1m]`, Route C plan + cross-review on 1M-Opus, compound fan-out 12→4-6, `/fast` manual-only, routine on Sonnet 4.6.

---

# Parity-Learning Report: Fable-5 -> Opus 4.8 (epic #3043 / #3056)

## Scope

~193 Fable-5 sessions across two dev hosts, aggregated from 14 batch reviews. Goal: name what Fable-5 did well across the corpus and the concrete behaviors Opus 4.8 (now primary as `claude-opus-4-8[1m]`) must reproduce to hold parity. Findings anchored to the already-ratified decisions: primary = 1M-Opus, Route C plan + cross-review on 1M-Opus, compound review fan-out cut 12 -> 4-6, `/fast` manual-only, routine work on Sonnet 4.6.

---

## 1. Fable Usage Profile

### Task classes (by observed frequency)
- **Autonomous GitHub issue triage** — the single largest class. Multi-repo, 70-175 issues per session, single user prompt, zero clarification breaks. Includes label/skip/dup/close decisions and mid-run crash recovery (idempotent "RESUMING prior agent died" pattern).
- **Adversarial plan/code review** — 40+ dedicated sessions. Structured VERDICT / RETRIEVAL / FINDINGS / BLOCKERS template, non-praise stance, defect-first framing held across 25-45 turns.
- **Long-context development / refactoring** — TDD red-green loops, multi-file edits, PR management, lint/test fix cycles, git worktree isolation.
- **Vision verification of extracted tables** — image-to-CSV QA with pixel-coordinate mapping against source PDFs, multi-batch state.
- **Autonomous agent delegation** — parent sessions fanning out 8-30+ subagents for triage slices and read-only gh queries.
- **Long-running multi-system workflow / onboarding** — MCP-integrated (Gmail / Drive / Calendar / Telegram), 5-18h sessions, terse user prompts ("continue", "merged", "sent").

### Volume signature
- Avg ~91 turns/session; 100+ turns the norm; longest sessions 318-1022 turns over 16-36h.
- Output tokens: 78k avg, up to 835k-898k on the longest sessions.
- Two bimodal output shapes: **terse loop mode** (3-77 tokens/turn for triage/implementation iteration) and **synthesis mode** (200-2000+ tokens/turn, max 8-11k, for adversarial reviews and structured critiques).

### Tool mix
- **Bash-dominant** (in 167/193 sessions; 20-185 calls/session) for discovery (ls/find/grep), state (git/gh), log parsing, test cycles.
- **Read** strategic, placed after Bash discovery — not speculative; 22-35 reads in vision-verification, 1-2 in metadata triage.
- **Edit/Write** reserved for actual mutations: surgical Edit-heavy in plan patching (13-23 edits), Write-heavy in triage/CSV (up to 49).
- **Agent** for fan-out parallelism; **TaskCreate/Update + Monitor** for async/background work; **ToolSearch** used sparingly to load deferred schemas then delegate; **AskUserQuestion** rare (2 in a 920-turn session).
- Phase-clustered: planning = Read+Write; patching = Edit+Bash; implementation = Bash-dominant + Edit; review = Read+Bash, minimal Write.

---

## 2. What Fable Did Well — Behaviors to Preserve

1. **Sustained stateful autonomy.** 100-318 turn sessions on a single prompt with no context reset, no re-briefing every 20-30 items, consistent decision criteria held across the whole run.
2. **Output-shape discipline by task.** Compressed to 3-24 tokens/turn in triage/loop mode; expanded to dense 8-10k synthesis only when findings warranted it. The model chose, it was not re-prompted each turn.
3. **Adversarial stance without drift.** Defect-first, non-praise framing maintained 25-45 turns; structured VERDICT/RETRIEVAL/FINDINGS/BLOCKERS output every time.
4. **Idempotent resumption.** Recovered from crashed prior agents off a brief task notification, avoided duplicate labels/comments, re-derived state implicitly.
5. **Phase-adaptive tool selection.** Bash-first discovery, targeted reads, surgical edits without full re-reads; minimal re-reading because prior reads stayed in context.
6. **Fan-out orchestration.** Single parent spawned 8-30+ subagents with bounded slices + rich context, polled status, relaunched failures — without per-spawn re-loading.
7. **Async lifecycle tracking.** TaskCreate -> Monitor -> TaskUpdate -> TaskStop across multi-hour windows; resumed from notifications instead of re-prompting.
8. **Multi-file edit coherence.** Edited file A, B, C in sequence (shared code paths) without defensive re-reads, maintaining cross-references.

---

## 3. Behavioral Deltas vs Opus 4.8 — Where Parity Is at Risk and Why

The 1M-Opus config flip removes the largest historical risk (context cliff), so the residual deltas are behavioral, not capacity. Risks below are framed for `claude-opus-4-8[1m]`.

- **D1 — Output verbosity / compression mismatch.** Fable held 3-24 tokens/turn in triage and 34-92 in implementation loops. Opus defaults to fuller prose (est. 80-200 tokens/turn). On 100-225 turn sessions this 3-5x output inflation burns budget, slows iteration cadence, and bloats turn count. *Highest-leverage delta.*
- **D2 — Autonomous decision confidence.** Fable made marginal label/skip/dup calls and inferred repo patterns from the first prompt with zero clarification breaks. Opus is more likely to pause for confirmation, breaking the one-prompt-per-agent contract that made triage agents viable.
- **D3 — Adversarial-stance fidelity.** Fable's non-praise defect-hunting was held by design; Opus's default constructive tone risks softening, balanced takes, or restating the plan — missing blockers in the dominant review use case.
- **D4 — Loop-exit / autonomy-horizon detection.** Fable autonomously decided "I've triaged 140, move to next slice." Opus may prematurely declare done or request permission before exhausting a batch.
- **D5 — Defensive re-reads breaking tight loops.** Fable trusted tool success and prior context; Opus may insert "let me verify this cell / re-read file A" steps, inflating turns and slowing TDD/edit velocity even with 1M context available.
- **D6 — Fan-out + async brittleness.** Fable's spawn-then-TaskCreate-Monitor pattern assumed cheap parallelism and implicit state. Opus may default to sequential bash chains, spawn fewer agents, or mishandle out-of-order status updates.
- **D7 — Skill/tool discovery hesitation.** Fable used ToolSearch then immediately delegated; Opus may over-invoke ToolSearch or ask "which skill?" instead of trying and learning.
- **D8 — 1M-context utilization, not just availability.** Having the 1M window flipped on does not guarantee Opus reuses prior reads instead of re-fetching, or holds multi-batch verification state without rollups. Utilization must be validated, not assumed.

---

## 4. Concrete Parity Actions (mapped to sub-issues)

### #3051 — config flip
- Confirm `claude-opus-4-8[1m]` is the resolved primary everywhere Route C plan + cross-review run, and that `/fast` is manual-only (no auto-routing). Routine work pinned to Sonnet 4.6.
- Set output-discipline defaults at config layer: terse-by-default response shaping for triage/loop task profiles, with synthesis mode reserved for review profiles. (Addresses D1.)

### #3052 — context-1M
- Add a 1M-utilization validation probe: re-run a long triage and a long TDD session; assert prior reads are reused (no redundant re-fetch) and multi-batch state is held without explicit rollups. (Addresses D5, D8.)
- Establish a long-session checkpoint convention only as a fallback for >300-turn / multi-hour interactive runs; do not force it where 1M context already covers state. (Addresses D8.)

### #3053 — workflows + quota
- Re-validate the reduced 4-6 fan-out under Opus: spawn 4-6 subagents with bounded slices + rich per-agent context, parent polls and relaunches failures; verify no sequential-bash fallback and graceful out-of-order status handling. (Addresses D6.)
- Encode the idempotent-resumption contract in workflow templates: every triage/verify agent action must be idempotent and resumable from a brief task notification. (Addresses D4, D6.)
- Track quota impact of D1 verbosity: monitor tokens/turn on triage agents; if Opus runs 3-5x Fable's rate, tighten output guardrails before scaling fan-out. (Addresses D1.)

### #3054 — skills + learning loops
- Bake the adversarial-review template (VERDICT / RETRIEVAL / FINDINGS / BLOCKERS, non-praise) into the review skill with explicit stance reinforcement so tone does not drift over 25-45 turns. (Addresses D3.)
- Add ToolSearch-then-delegate guidance to skill prompts: try-and-learn on tool availability, do not ask the user which skill to use. (Addresses D7.)
- Stand up a learning loop that samples Opus triage/review transcripts against the Fable behavioral baseline (output shape, clarification-break count, stance fidelity) and feeds regressions back into skill/prompt updates. (Addresses D2, D3.)

### #3055 — playbook
- Write the operator playbook section: one-prompt-per-agent contract, autonomous-decision rules (decide marginal calls, never hedge), loop-exit criteria ("exhaust the slice, then advance"), and the terse-vs-synthesis output-mode switch by task class. (Addresses D1, D2, D4.)
- Document the trust-tool-output / no-defensive-re-read norm for tight TDD and multi-file-edit loops, with the phase-clustered tool pattern (Bash discovery -> targeted Read -> surgical Edit). (Addresses D5.)

---

## Bottom line

The 1M config flip neutralizes the historical capacity gap; the remaining parity work is behavioral. The two deltas that most threaten parity are **output-compression discipline (D1)** and **autonomous decision confidence / stance fidelity (D2/D3)** — both are prompt/skill/playbook-shaped, not capacity-shaped, and all map cleanly onto #3054 and #3055 with config and validation support from #3051-#3053.
