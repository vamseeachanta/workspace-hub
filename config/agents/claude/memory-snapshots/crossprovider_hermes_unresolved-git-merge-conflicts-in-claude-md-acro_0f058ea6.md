---
name: crossprovider hermes unresolved-git-merge-conflicts-in-claude-md-acro
description: Unresolved git merge conflicts in CLAUDE.md across 6 repos
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [git-workflow, merge-conflicts, ops-issue, repo-maintenance]
---

During this audit, 6 repos were found with unresolved merge markers in CLAUDE.md (assethold, hobbies, investments, sabithaandkrishnaestates, teamresumes, achantas-data). This indicates a workflow failure where conflicts weren't resolved post-merge. Implement pre-push/CI validation to catch unresolved markers.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
