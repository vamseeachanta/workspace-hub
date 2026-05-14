---
name: project-goal-catalog
description: /goal use-case catalog lives at issue
metadata: 
  node_type: memory
  type: project
  originSessionId: 0e16a7f8-2ee2-4d28-a34a-7bd971e7e011
---

The `/goal` use-case catalog is the durable artifact at [#2695](https://github.com/vamseeachanta/workspace-hub/issues/2695). Catalog body lists 30 work patterns (Tier 1 = 23 generic from external source, Tier 2 = 7 ecosystem-tuned for our domains), each tagged `[planning-heavy]`, `[execution-heavy]`, or `[bidirectional]` per the brain/hands three-layer model (design doc D7).

**Why:** `/goal` is highest-leverage multi-day planning command; without a catalog, invocations drift toward whatever current chat suggests, losing additive quota-pool efficiency (Anthropic Max base + Anthropic overage + OpenAI consumed *additively* via Hermes routing).

**How to apply:**
- Before invoking `/goal` (or `Skill planning-goal` / `planning-code-goal`), the rule `.claude/rules/goal-invocation.md` instructs Claude to fetch #2695 body + latest weekly comment. Rule auto-loads from `.claude/rules/*.md` glob.
- Codex/Hermes get the catalog # in their dispatch prompts at session-start (Verdict B from #2695 Task 3 audit — no script-level prompt-template surfaces exist).
- Weekly picklist comments encode 3-5 candidates per week with three explicit roles: `planning brain` (Claude main), `routing/hands` (Hermes → Claude Code | Hermes → Codex | Claude main direct), `review` (Codex T1, +Gemini T2, +Claude reviewer T3).

**Related:** [[project-claude-design-adoption]] for similar catalog-as-durable-artifact pattern; [#2696](https://github.com/vamseeachanta/workspace-hub/issues/2696) tracks Hermes v0.4.0 → v0.13.0 upgrade (D7's routing-layer depends on v0.13.0 capabilities); [#2701](https://github.com/vamseeachanta/workspace-hub/issues/2701) tracks half-approval marker audit (17 of 29 status:plan-approved issues missing markers as of 2026-05-13).

Design doc: `docs/governance/2026-05-13-goal-use-case-catalog-design.md` (D1-D7 rationale). Formal plan: `docs/plans/2026-05-13-issue-2695-goal-use-case-catalog-plan.md` (Step G implementation log).
