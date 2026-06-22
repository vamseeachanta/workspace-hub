---
name: crossprovider codex approved-commands-fail-silently-in-test-only-pat
description: Approved commands fail silently in test-only paths
metadata:
  type: reference
  source: codex
  bridged: 2026-06-21
  tags: [test-harness-gap, approved-commands, fixture-parity]
---

Approved plan command `--generated-date 2026-06-20` fails with fixture still holding `2026-06-18`, but tests hide this by invoking generator with old date. Verification must run approved commands independently outside test harness to catch fixture/spec mismatches.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
