# Gemini Review Workflow

> Optional third-reviewer workflow for architecture and research-heavy work
>
> Version: 3.0.0
> Last Updated: 2026-03-31

## Role In The Operating Model

Gemini is an optional third reviewer in the minimal operating model.

Gemini is not the default implementation reviewer. Its narrow role is:

- architecture-heavy review
- research-heavy review
- comparison or synthesis-heavy review
- high-stakes ambiguity reduction when a third independent angle is justified

See [Cross-Review Policy](CROSS_REVIEW_POLICY.md) for the governing routing policy.

## When To Add Gemini

Add Gemini only when one or more of these are true:

- the task is architecture-heavy
- the task depends on large-context research or synthesis
- the Codex review still leaves major uncertainty
- local verification is weak relative to the change risk
- the impact surface is wide enough to justify a third reviewer

This is the three-provider review only when justified path.

## When Not To Add Gemini

Do not add Gemini by default for:

- routine implementation diffs
- small bug fixes
- normal refactors with clear local verification
- changes where Codex review already gives enough confidence

## Default Routing Reminder

The normal path remains:

1. Claude orchestrates
2. implementation is produced
3. Codex provides the default adversarial review
4. Gemini is added only when the task justifies a third independent pass

That keeps review pressure high without turning every task into a three-provider ceremony.

## Practical Focus Areas

When Gemini is used, it should focus on:

- alternative design interpretations
- missing tradeoffs
- research gaps
- context-window-heavy synthesis
- overlooked system-level risks

## Related Documents

- [Cross-Review Policy](CROSS_REVIEW_POLICY.md)
- [Codex Review Workflow](CODEX_REVIEW_WORKFLOW.md)
- [Minimal Harness Operating Model](MINIMAL_HARNESS_OPERATING_MODEL_2026-03.md)
