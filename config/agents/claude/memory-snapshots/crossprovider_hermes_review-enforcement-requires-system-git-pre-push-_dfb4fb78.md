---
name: crossprovider hermes review-enforcement-requires-system-git-pre-push-
description: Review enforcement requires system git pre-push hook for multi-provider enforcement
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [review-enforcement, multi-provider, git-hooks]
---

.claude/settings.json hooks only fire in Claude Code; Hermes, direct commits, and batch agents bypass them entirely. Solution: implement git pre-push.sh at repo level that checks review evidence before allowing push to main.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
