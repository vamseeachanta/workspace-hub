---
name: crossprovider hermes shell-exit-codes-and-json-status-are-independent
description: Shell exit codes and JSON status are independent: CLIs must fail-close via exit code
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [cli-contract, fail-closed, shell-automation]
---

A JSON-emitting CLI script that returns exit code 0 while JSON body contains `overall_status: "fail"` breaks shell automation patterns like `script && next-step`. The script proceeds on failure. Solution: exit codes must reflect JSON status; always return non-zero when JSON indicates failure, not just payload status fields.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
