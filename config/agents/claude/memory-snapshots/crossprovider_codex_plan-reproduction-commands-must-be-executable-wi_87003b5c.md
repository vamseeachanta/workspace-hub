---
name: crossprovider codex plan-reproduction-commands-must-be-executable-wi
description: Plan reproduction commands must be executable with verifiable output
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [plan-verification, evidence-reproducibility, acceptance-criteria]
---

A plan included a Python snippet claiming to produce specific output, but executing it produced nothing. Non-reproducible evidence breaks the resource-intel trail and blocks approval. Include only commands that can be run and verified to produce the claimed output, or replace them with synthetic test cases that actually execute.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
