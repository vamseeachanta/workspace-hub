---
name: crossprovider codex checker-scripts-are-governance-infrastructure-no
description: Checker scripts are governance infrastructure, not functional code
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [governance, checker-scripts, testing]
---

Read-only verification scripts (e.g., `check-client-wiki-registry.sh`, `scripts/cron/scheduler-routing-audit.py`) are governance automation and must: have isolated shell tests, use explicit exit codes (0 = pass, 2 = dependency-blocked), not mutate state, document dependencies. They are gates, not utilities.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
