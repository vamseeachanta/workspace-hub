---
name: crossprovider codex legal-scan-scripts-may-default-to-scanning-their
description: Legal scan scripts may default to scanning their own location, not target repo
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [security-gates, script-behavior, scanning-scope]
---

If a legal-scan script defaults to scanning its own filesystem location and requires an explicit --repo argument, scanning without arguments will miss generated artifacts in the target repo. Verify script defaults and pass explicit repo argument in gate commands.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
