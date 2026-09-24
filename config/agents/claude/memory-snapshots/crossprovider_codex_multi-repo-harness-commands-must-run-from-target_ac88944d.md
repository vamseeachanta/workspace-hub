---
name: crossprovider codex multi-repo-harness-commands-must-run-from-target
description: Multi-repo harness commands must run from target repo context
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [harness, bash, multi-repo, context-isolation]
---

Commands in multi-repo harness scripts run in the parent/harness directory by default, causing them to audit/scan the wrong repo. Use subshells: `(cd "$repo_path" && uv lock --check)` for isolation. Git and language-tool commands are especially prone to this.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
