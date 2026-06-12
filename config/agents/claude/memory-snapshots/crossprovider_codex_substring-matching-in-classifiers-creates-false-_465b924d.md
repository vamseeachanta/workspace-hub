---
name: crossprovider codex substring-matching-in-classifiers-creates-false-
description: Substring matching in classifiers creates false positives on field names
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [heuristics, classification, regex, false-positives]
---

Heuristic classifiers using raw `in` substring checks misclassify lines containing keywords in compound words (e.g., 'confirm' in field name 'gates_confirmed'). Use regex word boundaries or explicit token matching. Affects audit scripts that classify automation candidates.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
