---
name: crossprovider codex policy-must-provide-both-prose-and-machine-consu
description: Policy must provide both prose and machine-consumable schema
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [governance, policy, compliance-automation, schema]
---

Governance rules written as prose alone get misinterpreted by downstream automation consumers. Escalation policies, cohort classification rules, and carry-forward semantics must include a normative machine-readable format (YAML schema, decision table, or equivalent) to prevent reimplementation drift.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
