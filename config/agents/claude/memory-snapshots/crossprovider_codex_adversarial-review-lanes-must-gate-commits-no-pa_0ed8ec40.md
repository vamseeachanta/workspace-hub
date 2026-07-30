---
name: crossprovider codex adversarial-review-lanes-must-gate-commits-no-pa
description: Adversarial review lanes must gate commits; no parallel writers
metadata:
  type: reference
  source: codex
  bridged: 2026-07-19
  tags: [code-review, verification, workflow, quality-gate]
---

Run independent adversarial review lanes (spec compliance, contract semantics, security) in parallel, but do not commit while any lane reports MAJOR. Route corrections through a single writer; parallel writers on the same files collide. Each iteration must pass all lanes.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
