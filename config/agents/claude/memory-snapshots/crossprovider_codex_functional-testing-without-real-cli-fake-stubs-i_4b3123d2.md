---
name: crossprovider codex functional-testing-without-real-cli-fake-stubs-i
description: Functional testing without real CLI: fake stubs in PATH
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [testing, isolation, cli-mocking]
---

For CLI tool testing, create a minimal fake stub and place it earlier in `$PATH` than the real tool. This eliminates dependency on real tool installation and lets tests assert process state (exit codes, log output, process cleanup) without side effects.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
