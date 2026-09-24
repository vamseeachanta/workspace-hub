---
name: crossprovider codex test-markers-for-licensed-dependencies-need-fine
description: Test markers for licensed dependencies need finer granularity
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [test-organization, licensing-constraints, marker-design]
---

Generic test markers (e.g., solver) can conflate 'tests of licensed code' with 'tests that require licensed dependencies to run locally'. This hides wrapper/protocol tests that can run without the license. Use explicit markers (e.g., requires_license_to_run) to distinguish tests that must be skipped locally from tests that verify unlicensed behavior.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
