---
name: crossprovider codex pr-merge-gates-block-dependent-issue-closures
description: PR merge gates block dependent issue closures
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [git-workflow, issue-management, sequencing]
---

Sequential issue closures (e.g., child issues after epic merge) depend on upstream PR success. Verify commit existence before closing dependent issues to avoid race conditions and maintain audit trail integrity.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
