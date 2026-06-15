---
name: crossprovider codex optional-verification-commands-can-leak-scope-th
description: Optional verification commands can leak scope through backdoor integrations
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [scope-management, issue-boundaries, verification-design]
---

When an issue explicitly excludes work (e.g., 'defer #635 navigation/query to a separate issue'), check that optional/conditional verification commands don't provide backdoor access to that work. Graph regeneration, manifest re-writes, and similar integration commands need explicit boundary guards.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
