---
name: crossprovider codex test-isolation-pattern-for-home-directory-touchi
description: Test isolation pattern for home-directory-touching scripts
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [testing, shell-scripting, hermes, isolation]
---

Scripts that touch `~/.hermes` or other home dirs must be tested via environment-variable path overrides (e.g., `HERMES_HOME=/tmp/test-hermes`), not by deleting/mocking live paths. Preserve defaults when unset to retain CI smoke-test behavior; tests must never read/write/enumerate live orchestrator logs or home directories except through read-only post-test verification.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
