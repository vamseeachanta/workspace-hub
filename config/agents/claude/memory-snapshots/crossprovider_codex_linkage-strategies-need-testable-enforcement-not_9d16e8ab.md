---
name: crossprovider codex linkage-strategies-need-testable-enforcement-not
description: Linkage strategies need testable enforcement, not rhetorical claims
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [test-design, acceptance-criteria, schema-design]
---

Issue text like 'exact (operator, project_name) linkage for project-scope rows only' is not testable without explicit schema fields and tests. Acceptance criteria describing relationships must encode enforcement: required fields in schema, plus tests that verify operator-scope rows never have project linkage, etc.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
