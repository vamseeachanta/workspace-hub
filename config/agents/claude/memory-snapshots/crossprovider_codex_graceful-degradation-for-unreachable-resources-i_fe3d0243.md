---
name: crossprovider codex graceful-degradation-for-unreachable-resources-i
description: Graceful degradation for unreachable resources improves resilience
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [error-handling, partial-results, resilience]
---

When an index or resource is missing or unreachable during a query/scan, warn to stderr, add a coverage_gaps entry, return partial results, and exit 0. This avoids cascading failures and lets consumers decide whether partial results are acceptable. Full coverage is not always possible; partial + transparent is better than hard failure.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
