# Cross-Review Policy

> Minimal review-routing policy for the next 30-60 days
>
> Version: 2.0.0
> Last Updated: 2026-03-31
> Decision refs: #1514, #1515

## Overview

This document defines the minimal review-routing policy for workspace-hub after the architecture decision in [MINIMAL_HARNESS_OPERATING_MODEL_2026-03.md](MINIMAL_HARNESS_OPERATING_MODEL_2026-03.md).

The goal is to keep adversarial review in the workflow while reducing harness complexity.

## Core Policy

- Claude Code is the default orchestrator.
- Codex is the default adversarial reviewer for implementation diffs, tests, and concrete artifacts.
- Gemini is an optional third reviewer for architecture-heavy, research-heavy, ambiguous, or otherwise high-stakes work.
- two-provider review by default
- three-provider review only when justified

This replaces the older blanket policy that all Claude or Gemini work must always be reviewed by Codex.

## Default Routing

### Plans

For non-trivial work:

1. Claude frames the plan.
2. One independent adversarial review is required.
3. Use Codex by default unless the plan is architecture-heavy or research-heavy enough to justify Gemini.

### Code And Artifacts

For risky, architectural, cross-cutting, or hard-to-verify changes:

1. Claude frames or orchestrates the work.
2. Codex performs the default adversarial review of the implementation artifact.
3. Add Gemini only when a third independent angle is worth the added process cost.

For low-risk or easily verified work, keep review proportional.

## Provider Roles

| Provider | Default Role | Notes |
|----------|--------------|-------|
| Claude Code | Orchestrator | Primary planning, routing, synthesis, and final framing |
| Codex | Default adversarial reviewer | Default reviewer for implementation artifacts and diffs |
| Gemini | Optional third reviewer | Use for architecture, research, synthesis, or high-stakes ambiguity |

## Trigger Rules For Three-Provider Review

Use Gemini as an additional reviewer only when at least one of these is true:

- the change is architectural and design tradeoffs are the main risk
- the task is research-heavy or comparison-heavy
- local verification is weak or expensive
- the first adversarial review still leaves major ambiguity
- the impact surface is wide enough that a third independent perspective is justified

If these conditions do not apply, stop at the two-provider default.

## Legacy / Non-Default Control Planes

The following are not the default control plane for current work:

- `.hive-mind` is legacy or non-default until a live workflow proves it is needed
- `.swarm` is legacy or non-default until a live workflow proves it is needed
- `.SLASH_COMMAND_ECOSYSTEM` is legacy or non-default until a live workflow proves it is needed

These surfaces may remain in the repo, but they should not drive new workflow architecture.

## Practical Guidance

- Keep `AGENTS.md` as the canonical contract.
- Keep provider-specific surfaces thin.
- Do not require three-provider review for every task.
- Do not expand review automation faster than review reliability.
- Treat plugins and adapters as optional frontends, not the architecture center.

## Related Documents

- [Minimal Harness Operating Model](MINIMAL_HARNESS_OPERATING_MODEL_2026-03.md)
- [Codex Review Workflow](CODEX_REVIEW_WORKFLOW.md)
- [Gemini Review Workflow](GEMINI_REVIEW_WORKFLOW.md)
- [AI Agent Guidelines](AI_AGENT_GUIDELINES.md)
