---
name: crossprovider hermes codex-review-finds-path-safety-violations-that-c
description: Codex review finds path-safety violations that Claude logic review misses
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [adversarial-review, path-safety, codex-strength]
---

In #2769 disposition-reporter adversarial review, Codex flagged `/mnt/ace` output-path escaping and raw input echo in `--blocked-by` parsing that passed logic/syntax inspection. Cross-provider review is load-bearing for infrastructure-safety gates.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
