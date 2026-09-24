---
name: crossprovider gemini timestamp-normalization-for-governance-policies
description: Timestamp normalization for governance policies
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [governance, timestamp, policy]
---

Governance policies comparing terminal-event timestamps must normalize to UTC RFC3339 with millisecond precision before comparison. Use committer-date for git evidence, GitHub API event time for labels, filesystem mtime for markers. Tie-break rule must be explicit.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
