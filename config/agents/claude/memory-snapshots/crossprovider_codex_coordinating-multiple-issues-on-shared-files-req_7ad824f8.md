---
name: crossprovider codex coordinating-multiple-issues-on-shared-files-req
description: Coordinating multiple issues on shared files requires minimal, well-separated edits
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [multi-issue-coordination, code-organization, git-workflow]
---

When issue #A and issue #B both modify the same file (e.g., search.py), keep each issue's changes minimal and compartmentalized (prefer helper modules over inline rewrites). Document the cross-issue dependency. This preserves commit clarity and reduces merge conflicts.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
