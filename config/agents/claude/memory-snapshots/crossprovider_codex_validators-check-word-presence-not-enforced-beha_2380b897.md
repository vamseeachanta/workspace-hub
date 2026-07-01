---
name: crossprovider codex validators-check-word-presence-not-enforced-beha
description: Validators check word presence, not enforced behavior
metadata:
  type: reference
  source: codex
  bridged: 2026-06-30
  tags: [governance, validation, ci-gates, testing-strategy]
---

CI gates that validate keyword presence in governance artifacts (e.g., 'bounded', 'deny', 'snapshot') pass if words appear, not if behavior is enforced. Test the actual behavior: bounded-read validators must reject full-tree walks; denied-command validators must reject on attempted traversal. Keyword-only validation creates false confidence.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
