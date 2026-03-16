---
name: work-queue-work-execution-principle-scripts-over-llm-overhead
description: 'Sub-skill of work-queue: Work Execution Principle: Scripts Over LLM
  Overhead.'
version: 1.8.0
category: coordination
type: reference
scripts_exempt: true
---

# Work Execution Principle: Scripts Over LLM Overhead

## Work Execution Principle: Scripts Over LLM Overhead


> Canonical rule: `.claude/rules/patterns.md §Scripts Over LLM Judgment` (includes the 25% repetition threshold).

For every WRK item: if there is a ≥25% chance an operation will recur — write a script first, then call it. Scripts are reusable WRK assets; LLM prose is not.
