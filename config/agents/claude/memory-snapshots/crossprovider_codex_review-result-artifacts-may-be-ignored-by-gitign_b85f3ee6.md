---
name: crossprovider codex review-result-artifacts-may-be-ignored-by-gitign
description: Review result artifacts may be ignored by .gitignore; use force-add if part of evidence
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [git-conventions, review-artifacts]
---

scripts/review/results/ and similar review artifacts may be covered by .gitignore. Use git check-ignore --no-index or git add -f if review artifacts need to be committed as part of plan evidence or approval documentation.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
