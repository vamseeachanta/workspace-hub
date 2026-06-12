---
name: crossprovider codex session-log-pattern-matching-is-unreliable-for-c
description: Session log pattern matching is unreliable for compliance detection
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [logging, drift-detection, compliance]
---

Truncated command logs (typical 150-char limit) produce false positives (matching prose examples) and false negatives (incomplete multiline commands like git commits). Better approaches: parse structured events, query authoritative artifacts (actual git commits, audit logs), or require full-context logging. Regex on raw prose logs is a losing game.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
