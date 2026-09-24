---
name: crossprovider codex empirical-config-schema-validation-required
description: Empirical config schema validation required
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [config-migration, tooling-quirk, validation]
---

When migrating legacy config keys (e.g., `[status_line]` to `tui.status_line`), validate against the actual tool rather than docs—tools may not strictly validate config or docs may be incomplete. Build empirical validation into acceptance criteria.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
