---
name: crossprovider hermes test-skeleton-pattern-600-tests-per-domain-in-1-
description: Test skeleton pattern: 600+ tests per domain in 1-2 hours
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [testing, coverage, TDD, skeleton-tests]
---

Read source, write 3-5 tests per module (import, instantiation, basic I/O, edge cases, mocked external deps). Mock external libraries with `pytest.importorskip()` or `monkeypatch`. Reusable across structural/geotechnical/hydrodynamics; yields high coverage uplift with low effort.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
