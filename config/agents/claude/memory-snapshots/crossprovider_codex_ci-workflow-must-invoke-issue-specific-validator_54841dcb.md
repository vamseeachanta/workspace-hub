---
name: crossprovider codex ci-workflow-must-invoke-issue-specific-validator
description: CI workflow must invoke issue-specific validators on issue-specific paths
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [ci-coverage, workflow-design, issue-specific-validation]
---

When a new issue (e.g., #63) defines its own canary/validator, CI must explicitly invoke it on the issue's required paths. Generic public-surface scan does not cover issue-specific checks. Example: #63 canary must run on `docs/18-security-and-pii.md` via `--scan-public-path`; workflow default misses this.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
