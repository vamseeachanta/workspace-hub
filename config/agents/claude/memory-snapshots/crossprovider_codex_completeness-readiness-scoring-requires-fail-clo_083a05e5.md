---
name: crossprovider codex completeness-readiness-scoring-requires-fail-clo
description: Completeness/readiness scoring requires fail-closed + no user selectability
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [scoring, validation, issue-2798, anti-gaming]
---

Scoring schemes (quality, completeness, readiness) are gameable unless: snapshot/matrix is fail-closed on staleness (SHA binding), all scored packages are verified present, scoring class is auto-derived (not user-selectable), evidence links are required for checklist items, and test inflation is floored. Tests must explicitly exercise gaming vectors (low-value tests, metadata tampering, selective path declarations).

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
