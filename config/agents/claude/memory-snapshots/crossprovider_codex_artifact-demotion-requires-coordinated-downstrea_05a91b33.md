---
name: crossprovider codex artifact-demotion-requires-coordinated-downstrea
description: Artifact demotion requires coordinated downstream consumer updates
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [artifact-lifecycle, breaking-change, tool-coupling]
---

When demoting resource-intelligence-summary.md to optional in SKILL.md, downstream tooling still hard-depends on it: final-review.py loads it in _collect_sections(), init-resource-pack.sh scaffolds it, validate-resource-pack.sh asserts it, and tests check for it. Demotion alone creates silent failures; must update all consumers simultaneously or keep artifact required.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
