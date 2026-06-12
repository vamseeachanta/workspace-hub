---
name: crossprovider hermes multi-artifact-acceptance-criteria-diverge-acros
description: Multi-artifact acceptance criteria diverge across outputs
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [plan-review, acceptance-criteria, deliverables]
---

Acceptance text specifying report content can mismatch implementation when machine-readable data (YAML, JSON) exists elsewhere. E.g., #2508: report underdelivered per-role mappings that only YAML contained. Always specify each artifact's required content in acceptance criteria; don't assume field transposition.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
