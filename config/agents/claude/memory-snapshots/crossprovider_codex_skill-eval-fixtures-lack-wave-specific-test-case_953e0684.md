---
name: crossprovider codex skill-eval-fixtures-lack-wave-specific-test-case
description: Skill eval fixtures lack wave-specific test cases
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [testing, fixtures, coverage]
---

Existing skill evaluations (e.g., content triage) use generic examples and do not include wave-1 specific cases for text/JSON/code ingestion. New ingestion waves need dedicated fixture sets in skills/fixtures/ to prevent generic-example blind spots.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
