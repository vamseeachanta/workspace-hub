---
name: crossprovider codex canary-batch-on-new-corpus-before-full-scale
description: Canary batch on new corpus before full scale
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [batch-operations, cost-estimation, canary]
---

When running a batch pipeline on a new document corpus, run 50–100 docs first to validate prompt fit, token behavior, and per-document cost. Full estimates from canary data are more reliable than theoretical cost. Reveals systematic classification drift early.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
