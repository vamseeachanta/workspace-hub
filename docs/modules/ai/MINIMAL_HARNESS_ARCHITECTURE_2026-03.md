# Minimal Provider-Neutral AI Harness — Architecture Proposal

> Issue: #1514 | Date: 2026-03-31
> Parent docs: [Operating Model](MINIMAL_HARNESS_OPERATING_MODEL_2026-03.md) | [Control-Plane Contract](../../standards/CONTROL_PLANE_CONTRACT.md) | [Review Routing Policy](../../standards/AI_REVIEW_ROUTING_POLICY.md)

---

## 1. Executive Summary

This architecture defines a minimal provider-neutral AI operating model for workspace-hub, optimized for the current paid account mix (Claude Max $200, Codex 2×$20, Gemini 1×$20). The core decision: **do not build a new framework**. Instead, formalize the de facto architecture already in place — Claude Code as orchestrator, Codex as coding worker and adversarial reviewer, Gemini as narrow third-lane — and enforce it through the existing GSD workflow, `AGENTS.md` contract, and thin provider adapters.

## 2. Provider Roles (Settled)

### 2a. Claude Code — Default Orchestrator

Claude Code is the default orchestrator. This is a settled decision based on:

- `.claude/` is already the richest maintained surface (skills, rules, hooks, docs)
- Claude has the strongest existing command, hook, and orchestration shape
- The paid account mix ($200 Max) gives Claude the deepest context capacity
- Switching orchestrators would require rebuilding substantial workflow infrastructure

**Boundaries**: Claude orchestrates and frames work but should delegate bounded implementation to Codex when:
- The task has clear file scope and can be described in a self-contained prompt
- Parallel execution across disjoint write scopes would increase throughput
- Adversarial implementation review is needed (Codex implements, Claude reviews — or vice versa)

Claude should NOT delegate when:
- The task requires live repo context that would be expensive to re-establish in Codex
- The task is primarily orchestration, routing, or workflow coordination
- The overhead of task framing exceeds the cost of direct execution

### 2b. Codex — Coding Worker + Adversarial Reviewer

Codex is the primary coding worker and default adversarial reviewer.

**Execution role**:
- Bounded implementation tasks after Claude frames the work
- Test-first changes and patch generation
- Refactors with clear file scope
- Rescue work on stalled implementation tasks
- Parallel worker execution when write scopes are disjoint

**Review role**:
- Default adversarial reviewer for plans (non-trivial work)
- Default adversarial reviewer for diffs, tests, and artifacts before completion
- Implementation review and diff scrutiny

Two Codex accounts ($20 each) provide the cheapest scalable execution capacity in the current mix. This is a cost advantage — use it.

### 2c. Gemini — Narrow Third-Lane

Gemini is restricted to specific high-leverage scenarios:

- Large-document or large-context research passes (1M-token context advantage)
- Alternative-approach comparison and architecture review
- Synthesis across multiple sources or artifacts
- Overflow analysis when Claude context is already saturated
- High-stakes reviews where a third independent perspective justifies the cost

Gemini is NOT a default execution lane for repo mutations. Per #1326, Gemini output reliability in structured review flows does not justify expanding its role now.

**Trigger conditions for Gemini involvement** are defined in the [AI Review Routing Policy](../../standards/AI_REVIEW_ROUTING_POLICY.md#gemini-third-lane-trigger-rules).

## 3. Canonical Command Model

These are the logical workflow intents that any provider adapter should be able to express:

| Command | Description | Primary Provider |
|---------|-------------|-----------------|
| `plan` | Frame a task: gather context, define scope, produce a plan | Claude |
| `execute` | Implement the plan: write code, run tests, iterate | Codex (default), Claude (trivial/orchestration) |
| `review` | Adversarial review of plan or artifact | Codex (default), Gemini (triggered) |
| `delegate` | Route a bounded task to another provider | Claude (routing decision) |
| `status` | Check progress on delegated or background work | Any |
| `result` | Retrieve output from completed delegated work | Any |
| `cancel` | Abort delegated or background work | Any |

These are **logical intents**, not a new CLI. They map to existing mechanisms:
- In Claude: GSD commands, skills, subagent dispatch, `codex:rescue`
- In Codex: direct task execution via Codex CLI or `codex-plugin-cc`
- In Gemini: direct prompting via Gemini CLI

No new command framework is needed. The canonical command model exists to ensure adapters express the same intents, not to standardize invocation syntax.

## 4. Adapter Strategy

### Contract Layer

`AGENTS.md` is the canonical contract. It defines workflow, policies, and hard gates. All providers read it first. This is enforced by the [Control-Plane Contract](../../standards/CONTROL_PLANE_CONTRACT.md).

### Provider Adapters

| Adapter | Path | Role | Thickness |
|---------|------|------|-----------|
| Claude | `.claude/` | Full orchestrator surface: CLAUDE.md, rules/, skills/, hooks, docs/ | **Thick** — this is the primary working surface |
| Codex | `.codex/` | Thin adapter: instructions.md, settings | **Thin** — imports AGENTS.md context, adds Codex-specific instructions |
| Gemini | `.gemini/` | Thin adapter: GEMINI.md, settings | **Thin** — imports AGENTS.md context, adds Gemini-specific instructions |

**Adapter rules** (from CONTROL_PLANE_CONTRACT.md):
1. Adapters MUST NOT contradict `AGENTS.md`
2. Adapters MAY add provider-specific detail
3. Empty adapter directories are acceptable
4. Plugins like `openai/codex-plugin-cc` are **adapters only** — useful frontends, not the core architecture

### What This Means in Practice

- New workflow logic goes in `.claude/` (skills, rules, hooks) because Claude is the orchestrator
- `.codex/` and `.gemini/` get updated only when provider-specific instructions change
- No effort is spent on command parity across providers
- The contract (`AGENTS.md`) is provider-neutral; the implementation is intentionally provider-asymmetric

## 5. Backend Decision

**Use `uv run` CLI + existing GSD. Do not build a new framework.**

Rationale:
- GSD is already the workflow framework for workspace-hub (#1431 completed)
- `uv run` provides isolated Python execution for scripts and tools
- The repo already has working enforcement scripts, hooks, and CI
- A new backend (MCP server, shared CLI, custom orchestrator) would add maintenance before proving the current model is insufficient

The backend is: existing GSD commands + `uv run` scripts + provider CLIs. That's it.

## 6. Migration

**GSD is already the workflow. No migration is needed.**

- GSD was onboarded in #1431 and is the sole workflow since 2026-03-25
- The old 20-stage pipeline has been removed
- Provider adapters already point to AGENTS.md
- Legacy surfaces (`.hive-mind/`, `.swarm/`, `.SLASH_COMMAND_ECOSYSTEM/`) are frozen with `LEGACY.md` markers

The only remaining migration work is:
- `.agent-os/` directories in starter repos need content migrated to `AGENTS.md` or `docs/` (tracked in CONTROL_PLANE_CONTRACT.md rollout plan)
- Legacy directories can be removed once confirmed dead — no urgency

## 7. Review Defaults

Defined in detail in the [AI Review Routing Policy](../../standards/AI_REVIEW_ROUTING_POLICY.md).

Summary:
- **Two-provider review by default**: Claude produces; Codex reviews
- **Three-provider review when justified**: add Gemini under trigger conditions (architecture-heavy, research-heavy, ambiguous, high-stakes, context saturation)
- Plans get adversarial review for non-trivial work
- Code/artifacts get adversarial review when risky, architectural, cross-cutting, or hard to verify locally

Enforcement is currently advisory (Level 0 — Prose). Promotion path per #1515 and #1537:
- Level 1: Micro-skill at review stage entry (planned)
- Level 2: Script checking PR metadata for review annotations (#1537)
- Level 3: Hook blocking completion without documented review (#1537)

## 8. Repo Hygiene

Repo hygiene is tied to the operating model. #1530 (closed) established the hygiene workstream. Key outcomes:

- Legacy surfaces identified and marked with `LEGACY.md`
- Control-plane contract written (CONTROL_PLANE_CONTRACT.md)
- Provider adapter directories standardized across repos
- Stale plugin directories, redundant folders, and dead paths catalogued

Ongoing hygiene rules:
- Do not create new workflow logic in legacy directories
- New provider-specific config goes in the appropriate adapter directory
- Scripts and tools live in `scripts/` or `tools/`, not in provider directories
- Remove or freeze stale surfaces rather than trying to preserve behavior parity

## 9. 30-60 Day Operating Guide

### Days 1-30: Stabilize

1. Use Claude Code as the default orchestrator for all active work
2. Route bounded implementation, tests, and refactors to Codex by default
3. Restrict Gemini to explicit research, comparison, and overflow requests
4. Apply two-provider review default on non-trivial work
5. Stop creating new workflow logic in legacy directories
6. Keep AGENTS.md as the canonical contract; update it when policies change

### Days 30-60: Tighten

7. Promote review routing from advisory to scripted enforcement (#1537)
8. Migrate `.agent-os/` content in starter repos to `AGENTS.md`/`docs/`
9. Evaluate whether Codex throughput justifies a third account
10. Evaluate whether Gemini's narrow role justifies continued $20/month
11. Remove legacy directories if confirmed dead after 30 days of non-use
12. Write a brief retrospective: is the minimal model working? What's the bottleneck?

### Steady State

- One orchestrator (Claude), one main worker (Codex), one narrow lane (Gemini)
- One canonical contract (AGENTS.md), thin adapters per provider
- Two-provider review default, three-provider on triggers
- GSD workflow, `uv run` scripts, no new framework

## 10. Tradeoffs and Risks

### Accepted Tradeoffs

| Tradeoff | Why Acceptable |
|----------|---------------|
| Claude as partial single point of orchestration | Already the thickest surface; switching cost exceeds lock-in risk for 30-60 days |
| Provider-asymmetric operation | The contract is neutral; operational asymmetry reflects the actual account mix and capability differences |
| Gemini underused vs. theoretical capability | Maintenance tax for broad parity exceeds value; narrow role is net positive |
| No command parity across providers | Parity work is the source of drift, not the cure |
| Advisory-only review enforcement initially | Scripted enforcement is planned (#1537); advisory is sufficient for the first 30 days |

### Risks

| Risk | Mitigation |
|------|-----------|
| Claude lock-in deepens over time | Keep contract in AGENTS.md (provider-neutral); adapters remain thin; review in 60 days |
| Codex task framing quality becomes the bottleneck | Claude must produce clear, self-contained task descriptions; monitor Codex success rate |
| Gemini atrophies from disuse | Scheduled review at day 60; explicit trigger conditions keep it in the loop for high-value work |
| Legacy surfaces create confusion | LEGACY.md markers + removal plan; do not reference in new workflows |
| Review enforcement stays at Level 0 forever | #1537 tracks promotion to script/hook enforcement; review at day 30 |

## 11. What NOT to Build

| Don't Build | Why |
|-------------|-----|
| New provider-neutral CLI framework | Current tools work; framework adds maintenance before proving need |
| MCP-first control plane | Provider surfaces change too quickly; MCP adoption is surface-dependent |
| Full command parity across providers | Source of drift, not the solution |
| Plugin-centric architecture | Plugins are frontends, not the core |
| Mandatory three-provider review | Process weight exceeds value for routine work |
| New slash command ecosystem | Legacy `.SLASH_COMMAND_ECOSYSTEM/` is frozen for a reason |
| Provider-neutral task queue | GSD already handles task lifecycle |
| Abstraction layer over provider CLIs | Thin adapters are sufficient; abstraction adds indirection without value |

## 12. Related Issues

| Issue | Title | Status | Relationship |
|-------|-------|--------|-------------|
| #1514 | Design minimal provider-neutral AI harness | Open | This proposal |
| #1515 | Operationalize minimal AI review/routing policy | Open | Review enforcement — child of this work |
| #1530 | Workspace repo hygiene and taxonomy | Closed | Hygiene workstream — completed |
| #1537 | Enforce cross-review policy via gate script + hooks | Open | Enforcement promotion path |
| #1532 | Control-plane contract | Closed | Contract established |
| #1431 | Onboard GSD framework | Closed | GSD is sole workflow |
| #1473 | Audit official Claude plugins | Closed | Plugin audit completed |
| #1326 | Fix Gemini cross-review NO_OUTPUT | Open | Evidence for narrow Gemini role |
| #1331 | Fix cross-review.sh Codex dispatch crash | Open | Evidence for stabilizing before expanding |

## 13. Acceptance Criteria Checklist

- [x] Written architecture proposal exists in-repo (this document)
- [x] Identifies canonical command contracts and provider adapters (§3, §4)
- [x] Covers orchestrator, coding-agent, and reviewer flows (§2, §7)
- [x] Includes tradeoffs, risks, and migration sequencing (§10, §6)
- [x] References existing related issues (§12)
- [x] Recommends minimal operating model for current paid account mix (§2, §9)
- [x] Decides Claude Code as default orchestrator (§2a — settled)
- [x] Assigns concrete roles to Codex and Gemini (§2b, §2c)
- [x] Includes "do less harness" path for next 30-60 days (§9, §11)
- [x] Includes repo-hygiene workstream (§8)
- [x] Recommends plugins like `codex-plugin-cc` as adapters only (§4)
