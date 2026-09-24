---
name: crossprovider codex plan-consistency-violations-across-prose-pseudoc
description: Plan consistency violations across prose, pseudocode, and acceptance criteria are blockers
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [planning, consistency, review-methodology]
---

Pseudocode for acceptance commands can silently omit required flags (e.g., `--require-private-deny-list`) while prose elsewhere mandates them. These internal contradictions are high-severity blockers missed by linear review. Use a consistency pass that cross-references every CLI flag, field, and policy across all prose sections, pseudocode, and test setup.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
