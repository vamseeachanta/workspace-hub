---
name: crossprovider codex provisional-test-fixtures-may-be-unusable
description: Provisional test fixtures may be unusable
metadata:
  type: reference
  source: codex
  bridged: 2026-07-29
  tags: [testing, data-quality, fixtures]
---

Fixtures with failed vendor analysis or incomplete metadata (e.g., 88% fillage coverage, Shutdown fixture with invalid load) should be rejected, not forced into tests with invented tolerances. Trace real data instead.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
