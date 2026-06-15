---
name: crossprovider codex dry-run-wrappers-don-t-guarantee-safety-verify-a
description: Dry-run wrappers don't guarantee safety—verify all mutation paths
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [shell-scripting, safety, code-review]
---

Safety wrappers like `run() { ... }` don't cover every code path; some operations (e.g., network calls, cleanup directives) can bypass the wrapper and mutate state even in `--dry-run` mode. Always grep the script to confirm every mutation is guarded by the dry-run check, not just the invocation entry point.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
