---
name: crossprovider codex terminal-status-hierarchy-for-multi-pass-documen
description: Terminal status hierarchy for multi-pass document verification
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [status-hierarchy, terminal-states, dedup-precedence, document-pipelines]
---

Pattern: use a rank-ordered hierarchy of terminal parse_statuses (e.g., verified=3, rejected=2, deferred=1) to define dedup precedence when the same document identity appears in multiple states. Deferred = real-data-table that cannot be parsed in the current pass (parked for future re-extract). Mirror the control flow of existing terminal statuses (rejection, triage freezing) rather than inventing new branches. Selector excludes all terminal statuses uniformly.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
