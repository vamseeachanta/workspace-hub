---
name: crossprovider hermes eval-runner-uses-string-containment-not-yaml-par
description: Eval runner uses string containment, not YAML parsing
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [testing, eval, YAML, hermes-skill-evals]
---

Multi-line commands with backslash continuations break eval runner's `grep` containment check. Extract only the first line of commands when generating eval specs; the runner matches literal strings, not syntax trees.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
