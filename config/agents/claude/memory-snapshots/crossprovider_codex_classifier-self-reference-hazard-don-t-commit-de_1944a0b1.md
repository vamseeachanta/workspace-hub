---
name: crossprovider codex classifier-self-reference-hazard-don-t-commit-de
description: Classifier self-reference hazard: don't commit denied examples
metadata:
  type: reference
  source: codex
  bridged: 2026-07-01
  tags: [security-gate, classifier-design]
---

A firewall/classifier forbidding runnable patterns can accidentally publish the very examples it's designed to deny. Build denied-pattern examples from string fragments at runtime, not committed code. Identified as risk in #67 plan review.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
