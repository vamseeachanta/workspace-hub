---
name: crossprovider gemini structured-event-fields-beat-raw-text-regex-for-
description: Structured event fields beat raw-text regex for drift detection
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [drift-detection, pattern-matching, structured-logging]
---

Naive regex scanning of session logs produces false positives (conversational mentions, command output echoes). Detect violations via structured event fields (JSONL fields parsed by jq, git log --since on real commits) instead. Text patterns must be isolated to specific log entry types, not broad log searching.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
