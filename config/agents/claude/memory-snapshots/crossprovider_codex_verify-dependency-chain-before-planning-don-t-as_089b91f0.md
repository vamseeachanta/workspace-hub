---
name: crossprovider codex verify-dependency-chain-before-planning-don-t-as
description: Verify dependency chain before planning, don't assume
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [planning-workflow, dependency-management, gate-discipline]
---

Before planning an issue that depends on infrastructure work (e.g., #161 depends on #3449), verify the dependency is actually unmet via GitHub gate audit—no plan, no PR, no approval. Prevents redundant planning cycles and clarifies whether predecessor work was already completed elsewhere.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
