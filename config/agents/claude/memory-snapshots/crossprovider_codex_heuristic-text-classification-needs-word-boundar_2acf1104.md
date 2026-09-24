---
name: crossprovider codex heuristic-text-classification-needs-word-boundar
description: Heuristic text classification needs word boundaries and semantic negation patterns
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [text-heuristics, false-positives, testing]
---

Unbounded substring matching for keywords (e.g., searching `classify` for `confirm`) produces false positives when keywords appear inside field names (`gates_confirmed`) or write actions that incidentally contain a keyword. Use regex word boundaries for single-word patterns and maintain explicit denial lists for judgment-oriented verbs (assess, evaluate, decide, summarize, investigate) to avoid over-classifying non-scriptable items.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
