---
name: crossprovider codex non-ready-schema-rows-skip-validation-silently-a
description: Non-ready schema rows skip validation, silently accepting stale metadata
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [validator-gap, schema-validation, coordination]
---

Validators that gate plan/status checks behind implementation_ready=true leave non-ready rows unchecked; wrong plan_path, blank status_snapshot, or swapped issue data passes validation. Document this gap or validate all rows regardless of readiness state.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
