---
name: crossprovider codex semantic-inversions-in-label-meanings-require-ex
description: Semantic inversions in label meanings require explicit test cases
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [test-design, semantic-clarity, label-inversions]
---

When a field reverses meaning across axes (model: absence = executor chooses default, vs machine: absence = assignment gap), write tests for the inversion itself. Otherwise inversion-aware code looks redundant and regresses silently.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
