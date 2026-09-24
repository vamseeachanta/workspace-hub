---
name: crossprovider codex tdd-coverage-gaps-when-acceptance-criteria-lack-
description: TDD coverage gaps when acceptance criteria lack concrete test names
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [tdd, acceptance-criteria, testing, plan-review]
---

Wildcard file patterns (`tests/data/*.py`), opaque carry-forward references (`all 20 v2 tests retained`), manual-approval tests, and missing test-name entries in AC-to-test mappings create coverage ambiguity. Every acceptance criterion must map to a concrete, named test; if implementation is deferred, mark deferred tests explicitly rather than omitting them.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
