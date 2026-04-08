---
title: "Three-Agent Cross-Review"
tags: [methodology, review, cross-review, adversarial, quality]
sources:
  - compound-engineering-methodology
  - ai-agent-guidelines-doc
added: 2026-04-08
last_updated: 2026-04-08
---

# Three-Agent Cross-Review

Independent reviewers for plans AND artifacts. Self-review by the implementing agent is unreliable because the same biases that created a bug will miss it in review.

## Review Architecture

```
Claude (orchestrator) -> Implementation produced
  -> Codex (adversarial review)
    -> Need third angle?
      No -> Present with two-provider review
      Yes -> Gemini (third review)
        -> Present with three-provider review
```

## Default Roles

| Agent | Role | Default |
|-------|------|---------|
| Claude Code | Orchestrator + implementer | Always |
| Codex | Adversarial reviewer | Default for all reviewable work |
| Gemini | Third reviewer | Optional, triggered by complexity |

## Gemini Trigger Conditions

- Architecture-heavy changes
- Research-heavy or synthesis-heavy work
- Weak local verification relative to risk
- Unresolved ambiguity after first adversarial review

## Review Verdicts

Normalized to: `APPROVE`, `MINOR`, `MAJOR`, `NO_OUTPUT`, `ERROR`

Script: `scripts/review/normalize-verdicts.sh`

## Enforcement

The [[compliance-dashboard]] tracks review compliance rates. Target: 80%. The [[enforcement-over-instruction]] principle means reviews are enforced via pre-push hooks, not just instructions.

## Cross-References

- **Source**: [AI Agent Guidelines](../sources/ai-agent-guidelines-doc.md)
- **Related concept**: [[compound-engineering]]
- **Related concept**: [[enforcement-over-instruction]]
- **Related entity**: [Compliance Dashboard](../entities/compliance-dashboard.md)
