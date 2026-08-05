---
name: crossprovider codex silently-swallowed-failures-are-more-dangerous-t
description: Silently-swallowed failures are more dangerous than loud crashes
metadata:
  type: reference
  source: codex
  bridged: 2026-08-04
  tags: [shell-scripting, testing, error-handling, reliability]
---

A broken script invocation whose failure is masked by `|| true`, `|| :`, `2>/dev/null`, or `set +e` is indistinguishable from a passing invocation. A loud failure is a bug; a swallowed one is a lie. Always flag and separately report invocations whose failure is swallowed.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
