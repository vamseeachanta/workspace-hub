---
name: crossprovider codex codex-stdin-invocation-contract-must-be-verified
description: Codex stdin invocation contract must be verified against real CLI
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [codex-cli, stdin-handling, external-tool-quirks]
---

Plan-review-fanout.sh proposed `codex exec - < "$file"` to pass stdin, but the installed Codex CLI contract for `-` is unverified; mocks may pass while live CLI treats `-` as a literal prompt or fails. Requires empirical testing against real CLI before promoting to artifact.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
