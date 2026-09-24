---
name: crossprovider gemini github-workflow-scope-requirement-for-github-wor
description: GitHub workflow scope requirement for .github/workflows/ commits
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [github, oauth, cicd]
---

Git push fails with workflow-touching commits if OAuth token lacks `workflow` scope. Fix: `gh auth setup-git` reconfigures git to use the current `gh` token with correct scopes. Affects CI/CD automation changes.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
