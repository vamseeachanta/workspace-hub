---
name: crossprovider codex config-files-touched-in-plans-need-explicit-test
description: Config files touched in plans need explicit test coverage gates
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [planning, config-testing, verification-gates]
---

When a plan modifies config files (YAML, JSON), the targeted pytest command must explicitly include existing test files that load those configs. Format/lint gates alone do not catch config parser failures or semantic drift.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
