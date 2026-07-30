---
name: crossprovider codex scanner-composition-reuse-parent-s-cli-flag-don-
description: Scanner composition: reuse parent's CLI flag, don't rebuild logic
metadata:
  type: reference
  source: codex
  bridged: 2026-07-01
  tags: [security, gate-composition, scanner-design, ci]
---

Legal/security gates should compose existing scanners via CLI options (`--scan-public-path`), not duplicate logic. Keep command paths stable and repo-local to enable downstream gates to compose them predictably. Avoid requiring live GitHub API calls in CI.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
