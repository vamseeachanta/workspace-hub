---
name: crossprovider codex scan-commands-should-not-hard-code-missing-futur
description: Scan commands should not hard-code missing future artifacts
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [scan-commands, review-artifacts, dependency-management]
---

Don't reference future r2 review artifacts in final plan scan commands. Either materialize them with UNAVAILABLE markers if provider quota fails, or update commands to scan only existing artifacts. Hard-coded missing paths cause scan failures.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
