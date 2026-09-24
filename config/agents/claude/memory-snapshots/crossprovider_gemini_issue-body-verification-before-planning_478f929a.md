---
name: crossprovider gemini issue-body-verification-before-planning
description: Issue body verification before planning
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [planning, verification, github-api]
---

Repo descriptions in issue bodies often become stale; verify file existence and actual state via GitHub API (`gh api repos/.../contents/...`) before trusting self-descriptions in issue text. Planning based on outdated claims leads to incorrect scope.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
