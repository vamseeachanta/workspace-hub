---
name: crossprovider codex fixture-scope-must-match-approved-specification
description: Fixture scope must match approved specification
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [testing, acceptance-criteria, issue-260, issue-2945]
---

Test suites can pass on narrow fixtures without covering the full approved scope, creating unverified surface area. Issues #2945/#260: fixtures tested 1 of 5+ approved items, tests asserted only `count >= 3`, allowing implementation to pass despite missing required sources. Fixture scope must match the approval spec exactly.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
