---
name: crossprovider codex verdict-propagation-from-failed-warning-evidence
description: Verdict propagation from failed/warning evidence is deterministic, not prose-only
metadata:
  type: reference
  source: codex
  bridged: 2026-07-14
  tags: [verdict-propagation, acceptance-logic, deterministic-gates]
---

Nonacceptance and failure propagation must have deterministic rules encoded in schema and tests (e.g., FAIL blocks acceptance, WARNING requires explicit resolution, any unresolved evidence blocks parent acceptance). Prose-only rules in comments allow inconsistent implementations. Current evidence with FAIL or WARNING validation states cannot coexist with accepted conclusions; aggregation rules must forbid overrides.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
