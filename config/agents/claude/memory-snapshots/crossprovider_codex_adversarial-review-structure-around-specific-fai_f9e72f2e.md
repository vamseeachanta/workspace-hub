---
name: crossprovider codex adversarial-review-structure-around-specific-fai
description: Adversarial review: structure around specific failure-mode categories
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [code-review, adversarial-review, defect-hunting]
---

Instead of open-ended "review this code", structure adversarial reviews with targeted questions: (1) null/zero handling—can a null become 0 in output? (2) joins/merges—can a row silently fail to match? (3) schema collisions—can configured names overwrite existing columns? (4) dtype coercion—what happens on boundary values? (5) inference/gaps—does missing data become inferred zero? This catches spec-level defects that generic reading misses.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
