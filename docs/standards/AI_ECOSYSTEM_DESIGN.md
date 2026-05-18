# AI Ecosystem Design

> **Purpose:** durable, reverse-prompted design contract for how the workspace-hub repo ecosystem uses Claude, Hermes, Codex, and Gemini together — anchored to *measurable outcomes per work class*, not to provider features. This document is the **single source of truth** for provider-routing intent; operational settings live in `config/agents/` and `config/ai-tools/` and must align here.
>
> **How to read:** start with §A (what good output looks like) → §B (who owns which work) → §C (how the work flows) → §D (when to invoke or not) → §E (what we've already paid for as lessons) → §F (downstream work).
>
> **Authority:** derived from [#2675](https://github.com/vamseeachanta/workspace-hub/issues/2675) plan ([`docs/plans/2026-05-12-issue-2675-ai-ecosystem-reverse-prompt-plan.md`](../plans/2026-05-12-issue-2675-ai-ecosystem-reverse-prompt-plan.md)) through 3 cross-review waves, status `plan-approved` 2026-05-13. Maintenance contract at end of document.
>
> **Related governance**: [`docs/standards/CONTROL_PLANE_CONTRACT.md`](CONTROL_PLANE_CONTRACT.md) (entry-point/adapter authority — referenced, not superseded); [`docs/standards/AI_REVIEW_ROUTING_POLICY.md`](AI_REVIEW_ROUTING_POLICY.md) (operational routing policy — this doc anchors to outcomes, the policy implements the routing); [`docs/standards/PARALLEL_FIRST_EXECUTION.md`](PARALLEL_FIRST_EXECUTION.md) (canonical dispatch method for non-trivial work).

---

## §A — Outcome ledger

The ledger declares *what good output looks like* for each top-level work class the repo runs. Each row pairs an outcome with a **measurable signal** and a **good-enough threshold**. Signals are deliberately *artifact-based* — they survive review handoffs and audit later.

| Work class | Outcome (what good looks like) | Measurable signal | Good-enough threshold |
|---|---|---|---|
| **Issue planning** | Plan cites ≥3 distinct sources, names concrete gaps, has reproduction proof or N/A justification | `Resource Intelligence Summary` source-count + presence of `Reproduction proofs` block | ≥3 sources AND repro or N/A-marked |
| **Adversarial review** | Each provider verdict cites file paths or quoted claims; no praise/restatement; MAJOR/MINOR dominates over rubber-stamp APPROVE | Verdict + per-finding citation density in `scripts/review/results/*` | ≥1 cited finding per provider; APPROVE allowed only with checklist evidence |
| **Implementation execution** | Parallel-first dispatch decision, tests-first, atomic commits per logical change, no `--no-verify`, no self-approve gate breach | Mode decision (`single-lane` / `parallel-readonly` / `parallel-worktree`) + commit log + pre-commit-hook logs + attestation block (per [#2405](https://github.com/vamseeachanta/workspace-hub/issues/2405)) | Mode stated for non-trivial work; zero bypassed hooks; ≥1 failing test before its fix lands |
| **Knowledge/wiki contribution** | Concept pages cite public references (textbooks/DOIs/public manuals), not LinkedIn-only sourcing; aligns to repo licensing | Page frontmatter references; lint pass on `feedback_llm_wiki_concept_pages_need_public_references` rule | All non-vendor concept pages cite ≥1 textbook/DOI/public manual |
| **Comms (issue/PR comments, recruiter routing)** | Single summary comment per issue (per `feedback_gh_issue_comment`); recruiter outreach replied to only when consulting-level + credible (per `feedback_recruiter_engagement`) | Comment count per issue; recruiter-reply log | ≤1 status comment per agent-session per issue |
| **Ops/automation (Hermes/cron/batch)** | Preflight check passes before commit storms; no merge-race silent reverts; agents write-only-shared (commits serialized in main session) | Hermes activity log + `git reflog` audit for race events | 0 silent reverts per week; 0 dual-write commit races per week |
| **Cross-machine readiness** *(referenced from [#2089](https://github.com/vamseeachanta/workspace-hub/issues/2089); owned by that issue, not duplicated here)* | Reflected in #2089's weekly checklist | Output of weekly review | Owned by #2089 — see [`docs/ops/hermes-weekly-cross-machine-parity-checklist.md`](../ops/hermes-weekly-cross-machine-parity-checklist.md) |

**Structure**: 6 owned + 1 referenced = 7 rows. Every owned class has at least one paid-for failure mode in memory (§E maps each to its mitigation). The referenced row makes the boundary with #2089 explicit so future readers don't duplicate its scope.

---

## §B — Provider role matrix (with fallbacks)

Extends `config/agents/provider-capabilities.yaml`'s `strategy_role` field by anchoring each provider role to a §A work class.

| Work class | Primary | Why primary | Fallback 1 | Fallback 2 | When fallback fires |
|---|---|---|---|---|---|
| Issue planning | **Claude** (Sonnet 4.6 default; Opus 4.6 for Route-C complex) | Long-context multi-source synthesis; orchestrator role; tool-driving in main session (`feedback_claude_in_chrome_session_scoped`) | Hermes | Codex | Claude quota exhausted → Hermes; never delegate planning to Codex (sandbox cannot execute) |
| Adversarial review (T1 — scoped) | **Claude** single-author r3 | Cost-efficient; sufficient when permission gates block dispatch (`feedback_permission_gate_blocks_cross_review`) | — | — | No fallback; if scope grows, escalate to T2 |
| Adversarial review (T2 — standard, 3-of-3 attempt) | **Claude** (headless, post-#2683 fix) + **Codex** (when not under Claude-Code Bash) + **Gemini** | Three-provider parallel dispatch via `plan-review-fanout.sh`. Codex empirically catches non-overlapping defects vs. Claude (`feedback_cross_provider_review_payoff`); Gemini is the cheap third lane. | When Codex returns UNAVAILABLE (under Claude-Code Bash per `#2684`): accept 2-of-3 with documented exception, OR re-dispatch from plain terminal via `env -u CLAUDECODE` | OpenAI GPT-4.1 if Codex CLI breaks at a future version | Gemini sandbox overlay blind (`feedback_gemini_sandbox_overlay_blindness`) → verify with `git ls-files` before accepting MAJOR file-missing claims |
| Adversarial review (T3 — complex) | **Claude** + **Codex** + **Gemini** full 3-of-3 with operator commitment to recover Codex from plain terminal | `routing-config.cross_review.COMPLEX: true` already mandates it | Any 2 of 3 if one provider down | — | Provider unavailability → record explicit failure, never auto-approve |
| Implementation execution | **Hermes/Claude orchestrator** using parallel-first classification | Main session owns gate checks, lane contracts, verification, GitHub closeout, and serialized commits. Small/unclear work stays `single-lane`; read-heavy work uses `parallel-readonly`; approved disjoint implementation uses `parallel-worktree`. Codex remains review-only; subagent Write phantoms require direct verification. | Codex *review-only* | Gemini *review-only / large-context read-only* | Never delegate writes to Codex; never trust subagent Write reports without local verify; write-capable parallel lanes require isolated worktrees and owned/read-only/forbidden path contracts |
| Knowledge/wiki contribution | **Claude** (drafting) + **Codex** (independent check) | Claude long-context for source synthesis; Codex sandbox can still *read+critique* even when it cannot write | Hermes (overnight batch) | Gemini (large-doc overflow) | — |
| Comms (issue/PR comments) | **Claude** main session | Comment is part of issue-workflow surface; subagent comm phantoms possible | — | — | Never let subagents post comments without main-session re-verify |
| Ops/automation/scheduled | **Hermes** | Skill tooling, delegation, document-heavy workflows; `feedback_hermes_active_preflight_check` requires Hermes to preflight | Claude (manual fallback) | — | If Hermes mid-rebase: pause delegation, never dispatch parallel commits |

### Operational rules baked into the matrix

- **Claude/Hermes orchestrator sessions remain the write authority**, but execution is no longer assumed to be single-threaded. The canonical method is parallel-first classification: `single-lane`, `parallel-readonly`, or `parallel-worktree` per [`PARALLEL_FIRST_EXECUTION.md`](PARALLEL_FIRST_EXECUTION.md). The orchestrator owns final synthesis, direct output verification, GitHub closeout, and serialized commit/push operations.
- **Codex is review-only by hard policy.** No Codex file writes, no Codex shell execution. The `submit-to-codex.sh` wrapper enforces this; the matrix reinforces it.
- **Gemini lane requires `git ls-files` ground-truth check before accepting MAJOR file-missing claims** (per `feedback_gemini_sandbox_overlay_blindness` — empirical false-positive rate is high enough to warrant the precondition).
- **Fallback firing must be logged** (`scripts/review/results/...-fallback.md`) so the weekly review ([#2089](https://github.com/vamseeachanta/workspace-hub/issues/2089)) can audit whether fallbacks happen often enough to update the matrix.

---

## §C — Workflow walk-throughs

### §C1. Issue planning

**Ideal output:** A plan file under `docs/plans/YYYY-MM-DD-issue-NNN-*.md` that satisfies §A.outcome-ledger row 1 (≥3 sources, gap list, repro proof or N/A) and is ready for adversarial review.

**Minimal provider pipeline:**

```
1. Claude main session: read issue body, load issue-planning-mode skill
2. Claude main session: Resource Intel survey (parallel Bash + Read tool calls)
3. Claude main session: classify T1/T2/T3
4. [GATE 1] issue-planning-mode skill Step 1.5: reproduce-or-N/A
5. Claude main session: draft plan against docs/plans/_template-issue-plan.md
6. Claude main session: spec self-review (placeholder scan, internal consistency, scope, ambiguity)
7. [GATE 2] user reviews draft
8. → walkthrough §C2 (adversarial review)
9. [GATE 3] user approval at status:plan-approved
10. Claude main session: implement (TDD)
```

**Gate checkpoints (existing repo workflows, not new):**
- `issue-planning-mode` skill: Steps 1, 1.5, 2, 3, 4, 5, 6
- `require-plan-approval.sh` (pre-commit hook) — enforces `status:plan-approved` before writes outside safe paths
- `require-cross-review.sh` (pre-push hook) — enforces adversarial-review artifacts before push

**Provider choice rationale:** The orchestrator owns the canonical plan text and GitHub state. Read-only resource-intelligence lanes may run in parallel when they reduce wall-clock time, but final planning authority is not delegated. Do not let subagents write the plan without main-session verification; Codex and Gemini remain review/read-only lanes unless a future tool contract proves otherwise.

### §C2. Adversarial review (T1 / T2 / T3 depth scaling)

**Ideal output:** ≥1 review artifact per active provider under `scripts/review/results/YYYY-MM-DD-plan-NNN-<provider>.md`, each containing per-finding citations to file paths or quoted plan text.

**Minimal provider pipeline:**

```
T1 (scoped, single-provider):
1. Claude review-of-record only
2. Verdict written to scripts/review/results/...-claude.md
3. No fanout; if scope grows, escalate to T2

T2 (standard, 3-of-3 attempt; accept 2-of-3 with documented exception):
1. Push plan file to origin (per feedback_codex_needs_pushed_artifact)
2. scripts/review/attest-plan-claims.sh injects evidence block (per #2405)
3. Parallel dispatch ALL THREE providers via scripts/review/plan-review-fanout.sh:
   - claude (headless, with CLAUDE_PLUGIN_DIR override per #2683 — independent adversarial review, NOT just synthesis)
   - codex  (review-only; env-guard per #2684 fast-fails under Claude-Code Bash)
   - gemini (with GEMINI_CLI_TRUST_WORKSPACE=true; cwd=/tmp per fanout's documented gemini workaround)
4. Codex emits UNAVAILABLE in ~0.033s under Claude-Code Bash (per #2684 env-guard, by design). Operator may re-dispatch from a plain terminal via `env -u CLAUDECODE bash scripts/review/plan-review-fanout.sh ...` to add a real Codex verdict for high-stakes plans.
5. Verify Gemini MAJOR findings with `git ls-files` before acceptance (per feedback_gemini_sandbox_overlay_blindness).
6. If any provider returns MAJOR with validated findings: revise plan, GOTO 1 (re-attest, re-dispatch).
7. Single-dissent loop control: if sustained-MAJOR 3+ rounds from ONE provider while a DIFFERENT provider returns MINOR/APPROVE on the same content, surface to user; do NOT auto-cycle (per feedback_codex_sustained_MAJOR_loop).

T3 (complex, full 3-of-3 with synthesis):
1. Steps 1–4 from T2 with operator commitment to re-dispatch Codex from a plain terminal (no UNAVAILABLE-by-design acceptance)
2. scripts/review/render-structured-review.py synthesizes the 3 verdicts
3. Apply T2 step 6 + 7 logic
```

**Gate checkpoints:**
- `require-cross-review.sh` (hook) — enforces review artifacts before push
- `cross-review-gate.sh` (hook) — gates plan-status promotion
- `issue-planning-mode` skill Step 3 reviewer-stance contract — every prompt must force defect-hunting, forbid praise/restatement, require evidence per finding

**Provider choice rationale:**
- **Codex is the cross-review hard gate** per `agent-capability-scores.yaml` (`badge: hard gate`) and `provider-capabilities.yaml` (`strategy_role: cross_review_hard_gate`). Its non-overlapping defect detection is the empirically-paid-for value (`feedback_cross_provider_review_payoff`).
- **Gemini is the third lane** for its 1M-token context (large plans fit whole) and free-tier capacity, with the `git ls-files` precondition.
- **Single-author r3 fallback** is allowed when dispatch is structurally blocked; provenance must be transparent in the artifact.

---

## §D — Efficient-usage rules

### When to invoke each provider

| Decision | Rule |
|---|---|
| Planning work (any tier) | Orchestrator owns final plan; parallel read-only intel lanes allowed. |
| T1 review | Claude single-author r3 with transparent provenance. |
| T2 review | Claude + Codex + Gemini (parallel via fanout). |
| T3 review | All three independently → render-structured-review.py synthesis. |
| Implementation writes | Parallel-first classification: `single-lane` for small/shared work; `parallel-worktree` only for plan-approved disjoint write surfaces; orchestrator verifies and serializes commits. |
| Overnight batch work | Hermes — but preflight `pgrep -af 'git (rebase\|stash push\|commit\|merge\|reset\|checkout)'` first (`feedback_hermes_active_preflight_check`). |
| Wiki/concept page first-drafting | Claude — never LinkedIn-only sourcing (`feedback_llm_wiki_concept_pages_need_public_references`). |
| Recruiter / email triage | Claude main session — apply `feedback_recruiter_engagement` and `feedback_email_cross_noise` filters before drafting. |

### When NOT to invoke a provider

- **Don't delegate writes to Codex** — sandbox cannot write (`feedback_codex_sandbox_write_blocked`) or shell-exec (`feedback_codex_sandbox_no_execution`).
- **Don't trust Gemini file-missing MAJOR findings without `git ls-files`** — overlay-blindness false-positives (`feedback_gemini_sandbox_overlay_blindness`).
- **Don't dispatch Hermes during user's active git operations** — merge-race silent reverts (`feedback_merge_race_silent_revert`, `feedback_hermes_active_preflight_check`).
- **Don't auto-cycle Codex MAJOR loops** beyond 3 rounds — surface consensus-vs-minority decision (`feedback_codex_sustained_MAJOR_loop`).
- **Don't have subagents drive Chrome** — `mcp__claude-in-chrome__*` is session-scoped (`feedback_claude_in_chrome_session_scoped`).
- **Don't run worktree-isolation for every agent** — use it only for write-capable, plan-approved, disjoint streams. Use `parallel-readonly` lanes for discovery/review to avoid worktree overhead.

### When to parallelize vs. serialize

- **Parallelize**: independent provider reviews (T2/T3); read-only Resource Intel surveys; validation/review lanes; non-conflicting Bash + Read tool calls in one message; approved implementation streams with isolated worktrees and explicit path ownership.
- **Serialize**: user approval, final plan synthesis, shared-file edits without one owner, commit/push/closeout, and git operations during Hermes activity (per preflight check).

### When single-author r3 is the right answer

- Permission-gate blocks dispatch (`feedback_permission_gate_blocks_cross_review`).
- T1 scope (small, focused).
- T2/T3 dispatch structurally blocked (e.g., both Codex and Gemini unavailable for documented reasons; record both failures explicitly).

### When to escalate T1 → T2 → T3

- T1 → T2: scope grew during planning, multi-file changes detected, or first review surfaced unknowns.
- T2 → T3: MAJOR finding from one provider while a different provider returns MINOR (tie-breaker needed), or `cat:engineering*` / `cat:data-pipeline` label (per `engineering-issue-workflow` skill).

---

## §E — Failure-mode design contract (Memory-to-Surface map)

Each row maps a paid-for memory lesson to its durable mitigation surface in the repo. This is the **anti-orphaning contract**: memory feedback files at `~/.claude/projects/.../memory/` are connected to the artifacts that enforce them.

| Memory feedback | Durable mitigation surface |
|---|---|
| `feedback_codex_sandbox_no_execution` | `scripts/review/submit-to-codex.sh` review-only mode; provider matrix forbids Codex implementation work |
| `feedback_codex_sandbox_write_blocked` | Same as above |
| `feedback_codex_needs_pushed_artifact` | `scripts/review/attest-plan-claims.sh` runs after `git push` |
| `feedback_codex_sandbox_fallback_paths` | Codex prompt authorizes `js_repl` + GitHub connector fallback; MAJOR verdicts without fallback-read citation are weakly grounded — flagged in `scripts/review/validate-review-output.sh` |
| `feedback_codex_sustained_MAJOR_loop` | §C2 walkthrough Step 7 — surface decision after 3 sustained-MAJOR rounds (single-dissent pattern) |
| `feedback_codex_cli_0_124_upstream_regression` + sibling [#2684](https://github.com/vamseeachanta/workspace-hub/issues/2684) (CLAUDECODE env-guard at `0cd40c6ab`) | §C2 walkthrough Step 4 — `scripts/review/lib/codex-version-guard.sh` fast-fails under Claude-Code Bash; operator re-dispatches from plain terminal via `env -u CLAUDECODE` to recover Codex verdict |
| `feedback_gemini_sandbox_overlay_blindness` | §C2 walkthrough Step 5 — `git ls-files` precondition before accepting Gemini MAJOR file-missing claims |
| `feedback_gemini_trust_env_blocks_reviews` | `submit-to-gemini.sh` sets `GEMINI_CLI_TRUST_WORKSPACE=true` (landed 2026-04-24) |
| `feedback_hermes_active_preflight_check` | Hermes worker scripts call `pgrep -af 'git (rebase\|stash push\|commit\|merge\|reset\|checkout)'` and abort on hit |
| `feedback_multi_agent_commit_serialization` | Main session commits; subagents write only (Provider matrix execution row) |
| `feedback_parallel_agent_write_only_pattern` | Same as above; codified in `gsd-context-monitor.js` |
| `feedback_git_status_lock_storm` | `GIT_OPTIONAL_LOCKS=0 git commit` documented in scripted commit helpers |
| `feedback_cross_provider_review_payoff` | §C2 T2 provider matrix mandates Claude + Codex + Gemini parallel review |
| `feedback_always_adversarial_review_scale_depth` | Tier-based depth scaling in §C2; never skip |
| `feedback_permission_gate_blocks_cross_review` | Single-author r3 with transparent provenance allowed; encoded in §C2 fallback |
| `feedback_subagent_write_phantom` | Main session re-verifies subagent writes via `ls` before declaring success |
| `feedback_isolated_clone_dispatch_race` | Subagent in exec-clone checks for parallel-session landing on main workspace before writing |
| `feedback_attestation_enables_contradiction_detection` | `attest-plan-claims.sh` block (per [#2405](https://github.com/vamseeachanta/workspace-hub/issues/2405)) used in every T2/T3 review |
| `feedback_worktree_isolation_large_repo_cost` | Default `Agent` calls to write-only-shared mode; reserve `isolation: worktree` for must-commit agents |
| `feedback_lane_result_path_outside_sandbox` | Lane results fall back to `docs/sessions/` when sandboxed paths blocked; emit ENV-MISMATCH banner |

**Promotion rule:** every row above is mirrored in this document under the **single-source-of-truth contract** — when a memory feedback file is renamed or deleted, this row must be updated in the same PR (cycle ≤24h, not quarterly). Quarterly baseline sweep is the floor; same-PR updates are the ceiling. See §F #10 for the maintenance contract.

---

## §F — Follow-up work (reference)

10 follow-up issues are enumerated at [`docs/reports/2026-05-12-issue-2675-followup-issues-list.md`](../reports/2026-05-12-issue-2675-followup-issues-list.md) for filing when each work-stream is ready to dispatch. The list is **maintained, not frozen**: as items are filed and closed, the report updates with status + commit links. Two harness-bug follow-ups ([#2683](https://github.com/vamseeachanta/workspace-hub/issues/2683), [#2684](https://github.com/vamseeachanta/workspace-hub/issues/2684)) were filed live during plan-2675 execution and are already CLOSED.

---

## Revision history

| Version | Source | Notable lessons |
|---|---|---|
| v0 (draft) | plan-2675 v1 (commit `da19310ae`, 2026-05-12) | Issue filed; plan drafted; resource-intel surveyed 12+ sources; original verdict-summary committed |
| (wave 1) | fanout 2026-05-12T16:34 | Both Claude (SessionEnd crash) and Codex (stdin-hang) UNAVAILABLE due to harness regressions; Gemini MAJOR with overlay-blindness false-positives. Two follow-up bugs filed: [#2683](https://github.com/vamseeachanta/workspace-hub/issues/2683), [#2684](https://github.com/vamseeachanta/workspace-hub/issues/2684). |
| v2 | plan-2675 v2 (commit `a7581e454`, 2026-05-13) | Folded wave-2 cross-provider findings: self-clearance pattern flagged + retracted; §B concentration rule honestly restated; §C2 walkthrough corrected to include Claude as adversarial reviewer; stale codex citations replaced with #2684 references. |
| (wave 2) | fanout 2026-05-13T08:15 (post-#2683 + #2684 harness fixes) | Claude + Gemini both MAJOR with non-overlapping content findings — first wave with real cross-provider signal. 8 distinct blocker-class findings. |
| v3 | plan-2675 v3 (commit `49507b582`, 2026-05-13) | Folded wave-3 audit-trail-rot findings: state mismatch ([#2684](https://github.com/vamseeachanta/workspace-hub/issues/2684) CLOSED); TDD test globs converted to write-time recompute rules; source count + §A row count reconciled; Artifact Map dedupe. |
| (wave 3) | fanout 2026-05-13T12:07 (post-v2) | Claude MAJOR with bookkeeping-rot findings only (content substantively approval-grade); Gemini UNAVAILABLE with NEW failure mode (server-side 429 capacity exhaustion). Single-provider effective coverage. |
| v3-final | This document (2026-05-13) | Plan #2675 advanced to `status:plan-approved`; primary deliverable + §F follow-ups list landed as durable artifacts. |

**Defect-class trajectory across waves:** harness-broken (W1) → content-defects (W2) → bookkeeping-rot (W3). Each wave caught a different class. None overlap. This is the cross-review apparatus functioning as designed, not as performative ritual.

---

## Maintenance contract

This document is **the single source of truth for provider-routing intent**. Operational settings in `config/agents/`, `config/ai-tools/`, and `scripts/review/` must align here — divergence is a defect to fix, not a feature.

### Update triggers (in priority order)

1. **Same-PR (≤24h)**: any commit that renames or deletes a `~/.claude/projects/.../memory/feedback_*.md` slug cited in §E must update the row in the same PR. The plan that caused the rename owns the update.
2. **Same-PR (≤24h)**: any change to `config/agents/provider-capabilities.yaml`'s `strategy_role` or `consolidation_*` fields must update the corresponding §B row.
3. **Same-PR (≤24h)**: any change to `scripts/review/plan-review-fanout.sh`'s provider invocation shape must update §C2 walkthrough.
4. **Same-PR**: §A outcome ledger rows must align with `routing-config.yaml` tier definitions; either rename or update simultaneously.
5. **Quarterly baseline sweep** (next: 2026-08-13): full §E table walk against current memory feedback file inventory; full §B table walk against current `provider-capabilities.yaml`; full §F status walk against GH issue states.
6. **Per-incident** (post-mortem trigger): any documented failure of the harness or provider during operations should produce either a new §E row (if a new lesson) or update an existing one (if recurrence) — not just a bug fix.

### Authority precedence (when sources disagree)

1. **This document** for *intent* (what we should do)
2. `routing-config.yaml` for *behavior* (what the dispatcher actually does)
3. `provider-capabilities.yaml` for *facts* (what the providers can do)
4. Memory feedback at `~/.claude/projects/.../memory/feedback_*.md` for *paid-for lessons*

If 1 and 2 disagree: update 2 to match 1, OR update 1 if reality has moved past intent. Drift in either direction is a defect.

### Re-review cadence

This document was reviewed adversarially across 3 cross-review waves during the plan-2675 process. The expectation is **not** that it's now permanent — it's that the next deep re-review happens when:

- A new provider joins the matrix (e.g., a fifth provider beyond Claude/Hermes/Codex/Gemini)
- A provider materially changes capability (context window 10×, pricing 5×, etc.)
- The "Claude concentrated in 5 of 7 work classes" structural property changes (e.g., another provider becomes able to drive tools in main session)
- The defect-class trajectory across waves stops being clean (i.e., waves start catching the same class repeatedly, signaling the apparatus needs refresh)

In the absence of those triggers, baseline quarterly sweep is sufficient.
