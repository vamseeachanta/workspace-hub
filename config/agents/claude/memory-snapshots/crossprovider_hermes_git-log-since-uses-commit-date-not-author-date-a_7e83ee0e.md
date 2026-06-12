---
name: crossprovider hermes git-log-since-uses-commit-date-not-author-date-a
description: git log --since uses commit date, not author date; account in date-based tests
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [git-testing, date-handling, test-fixtures]
---

When testing 'commits from last N hours', git log --since=N hours ago uses committer date, not author date (set via --date flag). Solution: use flexible assertions or explicitly control GIT_COMMITTER_DATE when testing; rigid date assertions will fail due to skew.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
