# Codex Review Workflow

> Default adversarial review workflow for implementation artifacts
>
> Version: 3.0.0
> Last Updated: 2026-03-31

## Role In The Operating Model

Codex is the default adversarial reviewer for implementation diffs, tests, and concrete artifacts.

This means:

- Claude remains the default orchestrator
- Codex is the default adversarial reviewer
- Gemini is an optional third reviewer when the task is high stakes enough to justify it

See [Cross-Review Policy](CROSS_REVIEW_POLICY.md) for the governing routing policy.

## When To Use Codex Review

Use Codex review by default for:

- bounded code changes
- refactors
- test additions or modifications
- diff scrutiny before completion
- risky implementation artifacts that need an independent pass

## Default Review Path

The normal path is:

1. Claude frames or routes the work.
2. The implementation is produced.
3. Codex performs the default adversarial review.
4. If the review is sufficient, stop there.
5. Add Gemini only when the change is architecture-heavy, research-heavy, ambiguous, or otherwise high stakes.

This is the two-provider review by default path.

## Escalation To Three-Provider Review

Escalate beyond Codex only when justified:

- the first review leaves unresolved architectural ambiguity
- the change crosses many systems and local verification is weak
- the task depends heavily on research synthesis or comparison
- the cost of a missed flaw is materially high

If those conditions do not apply, do not add a third reviewer.

## Practical Focus Areas

Codex review should focus on:

- correctness
- regression risk
- test adequacy
- security or data-handling issues
- concrete implementation gaps

## Related Documents

- [Cross-Review Policy](CROSS_REVIEW_POLICY.md)
- [Gemini Review Workflow](GEMINI_REVIEW_WORKFLOW.md)
- [Minimal Harness Operating Model](MINIMAL_HARNESS_OPERATING_MODEL_2026-03.md)
