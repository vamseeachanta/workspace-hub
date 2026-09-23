---
name: crossprovider codex schema-version-migrations-require-lockstep-updat
description: Schema version migrations require lockstep updates across collector, consumers, and test fixtures
metadata:
  type: reference
  source: codex
  bridged: 2026-07-25
  tags: [schema-versioning, test-coverage, regression, equality-matrix, fixtures]
---

When `collect-equality.sh` bumped the schema version from 4 to 5, the matrix builder still hard-rejected anything except schema 4 in `provider_row_verdict()`, silently regressing all provider capability rows to `MISSING-EVIDENCE`. The test suite missed this because provider-row fixtures were pinned to schema 4 while the top-level collector/schema tests only verified the new version. On future schema bumps, update the version gate, the fixture data, and the consumer acceptance check all in one PR to catch mismatches before they ship.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
