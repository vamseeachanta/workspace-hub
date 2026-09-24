---
name: crossprovider codex system-python-environment-differs-from-repo-venv
description: System Python environment differs from repo .venv; test runs write cache artifacts
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [testing-hygiene, environment-isolation, read-only-reviews]
---

System Python may lack dependencies required by repo tests (e.g., plotly). Use repo's .venv to match intended environment. Read-only reviews should avoid pytest if it writes cache/coverage artifacts unless those are pre-ignored in .gitignore. Verify worktree state before/after with bash.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
