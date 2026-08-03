---
name: crossprovider codex github-cli-tooling-limitation-no-blockedby-schem
description: GitHub CLI tooling limitation: no blockedBy schema
metadata:
  type: reference
  source: codex
  bridged: 2026-07-11
  tags: [tooling, github, ci-cd]
---

GitHub CLI's issue/PR schema does not expose blocking/dependency relationships (`blockedBy`) directly. Fetch full issue bodies and GitHub API responses separately to establish cross-issue context and dependency chains.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
