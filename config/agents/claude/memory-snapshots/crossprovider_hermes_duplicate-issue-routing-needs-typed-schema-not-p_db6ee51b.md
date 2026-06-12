---
name: crossprovider hermes duplicate-issue-routing-needs-typed-schema-not-p
description: Duplicate-issue routing needs typed schema, not presence checks
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [issue-routing, work-deduplication, schema-contracts]
---

Triage/routing mappings across multiple issues require explicit schema: primary vs secondary ownership, relation type (owns/feeds/excluded_due_to), precedence rules, uniqueness guards. Free-form presence checks are insufficient to prevent accidental re-opening of work.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
