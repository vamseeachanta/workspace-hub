---
name: crossprovider codex advisory-report-only-workflows-must-exit-0-not-1
description: Advisory/report-only workflows must exit 0, not 1
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [shell-semantics, ci-compatibility, workflow-design]
---

Exit code 1 signals failure to CI/shells and breaks conditional logic. Advisory workflows must exit 0 and express advisory status in manifest/report metadata, not process exit codes.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
