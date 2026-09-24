---
name: crossprovider codex shell-exit-code-capture-must-not-use-pipes-pipe-
description: Shell exit-code capture must not use pipes; pipe reports final command exit status
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [bash, exit-codes, pipes, error-detection]
---

Using `cmd | tail` or `cmd | grep` to capture exit status reports the pipe's exit status, not the command's. Use `cmd > file 2>&1; echo "rc=$?"` and read the file. This mistake has caused multiple wrong conclusions about whether commands actually succeeded or failed silently.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
