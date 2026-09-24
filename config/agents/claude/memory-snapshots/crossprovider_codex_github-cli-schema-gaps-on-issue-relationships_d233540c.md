---
name: crossprovider codex github-cli-schema-gaps-on-issue-relationships
description: GitHub CLI schema gaps on issue relationships
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [github-cli, issue-tracking, schema-limitations]
---

The `blockedBy` relationship is not exposed in GitHub CLI schema. Fetch blocking relationships from issue bodies, repository-local standards, or use `gh api` to query GraphQL directly.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
