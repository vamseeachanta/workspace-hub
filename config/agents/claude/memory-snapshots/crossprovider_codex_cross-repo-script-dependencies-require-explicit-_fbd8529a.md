---
name: crossprovider codex cross-repo-script-dependencies-require-explicit-
description: Cross-repo script dependencies require explicit env var export and path validation
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [testing, integration, cross-repo]
---

Plans depending on scripts in sibling repos must explicitly export environment variables (e.g., `export WORKSPACE_HUB=/path`) because Python's `os.environ` will silently fail if vars are only set but not exported. Relative-path resolution from sibling checkouts must be validated against the actual sibling layout, not assumed to work.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
