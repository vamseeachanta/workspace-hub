---
name: crossprovider codex gemini-cli-trust-directory-failures-when-invoked
description: Gemini CLI trust-directory failures when invoked from /tmp in plan-review-fanout.sh
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [gemini-cli, ci-cd, environment-issue]
---

Running `(cd /tmp && gemini -p "$combined")` causes trust-directory failures in plan-review-fanout.sh. Gemini CLI requires explicit trust environment flags (e.g., GEMINI_CLI_TRUST_WORKSPACE=true) or execution from a trusted working directory.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
