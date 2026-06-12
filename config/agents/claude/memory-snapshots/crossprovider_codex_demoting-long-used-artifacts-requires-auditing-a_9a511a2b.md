---
name: crossprovider codex demoting-long-used-artifacts-requires-auditing-a
description: Demoting long-used artifacts requires auditing all downstream consumers atomically
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [artifact-lifecycle, refactoring, dependencies]
---

When changing an artifact from primary to optional (e.g., resource-intelligence-summary.md), grep all scripts, tests, and generators for references. Update all consumers in one change or the old artifact remains a hidden hard dependency. Piecemeal changes leave blockers.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
