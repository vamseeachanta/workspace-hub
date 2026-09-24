---
name: crossprovider codex multi-source-status-consensus-needs-explicit-pre
description: Multi-source status consensus needs explicit precedence and drift rules
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [schema-design, multi-source-consistency, status-normalization]
---

When status is stored in schema, README, coordination doc, and issue labels, the plan must enumerate precedence (which source wins), define 'drift' (when disagreement is OK), and include test cases for all precedence pairs. Implicit coarsening rules create hidden contradictions.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
