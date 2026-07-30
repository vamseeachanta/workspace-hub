---
name: crossprovider codex read-only-code-review-without-environment-setup
description: Read-only code review without environment setup
metadata:
  type: reference
  source: codex
  bridged: 2026-07-01
  tags: [code-review, troubleshooting, technique]
---

When a codebase lacks environment dependencies or setup is unavailable, use generated artifacts, git diff, and previously-passed test results as evidence rather than forcing environment setup. Verify code paths against artifact outputs and git state instead of attempting imports or live runs.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
