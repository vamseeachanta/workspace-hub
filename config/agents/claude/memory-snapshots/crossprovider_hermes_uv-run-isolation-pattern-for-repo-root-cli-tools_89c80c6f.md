---
name: crossprovider hermes uv-run-isolation-pattern-for-repo-root-cli-tools
description: uv run isolation pattern for repo-root CLI tools
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [python-tooling, isolation, ci-cd]
---

Use `uv run --no-project` for scripts running at workspace root that need isolation from any local project dependencies. Canonical for test discovery, CI verification, and provider audits that must not inherit transient project environments.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
