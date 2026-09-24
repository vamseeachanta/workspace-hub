---
name: crossprovider codex dry-run-side-effects-must-occur-after-condition-
description: Dry-run side effects must occur after condition checks, not before
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [bash, side-effects, dry-run]
---

Creating temporary files before checking `DRY_RUN` makes read-only target directories fail validation even though the flag was meant to prevent writes. Order conditions first, side effects second; late checks do not prevent early mutations.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
