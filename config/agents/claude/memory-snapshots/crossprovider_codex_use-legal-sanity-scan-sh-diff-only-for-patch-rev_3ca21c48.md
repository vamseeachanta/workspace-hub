---
name: crossprovider codex use-legal-sanity-scan-sh-diff-only-for-patch-rev
description: Use legal-sanity-scan.sh --diff-only for patch review to avoid historical violations
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [legal-scanning, repo-tool, review-workflow]
---

Repo legal scan has --diff-only mode. Use it for reviewing uncommitted/patch diffs to avoid flagging pre-existing violations in tracked files. Full-repo scan drags in noise; diff-only focuses on the changed surface.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
