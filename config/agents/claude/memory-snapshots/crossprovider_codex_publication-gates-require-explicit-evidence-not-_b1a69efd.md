---
name: crossprovider codex publication-gates-require-explicit-evidence-not-
description: Publication gates require explicit evidence, not approval status
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [gates, publication-control, ci-wiring, downstream-clarity]
---

A gate like 'publication blocked until #63' must rest on implemented canary code with passing command/exit-code evidence, not just an approved issue. Document the distinction between approval (issue plan-approved), implementation (code merged), and evidence (passing test/command recorded). Avoid misleading downstream readers about which gate has actually fired.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
