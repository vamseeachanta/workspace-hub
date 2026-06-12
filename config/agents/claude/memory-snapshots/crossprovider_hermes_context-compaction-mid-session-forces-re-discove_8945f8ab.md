---
name: crossprovider hermes context-compaction-mid-session-forces-re-discove
description: Context compaction mid-session forces re-discovery and artifact loss
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [hermes, context-management, artifact-persistence]
---

When 'Summary generation unavailable' occurs, 20+ messages may be discarded; tasks must re-discover current state from file/git state and saved artifacts. Save intermediate artifacts (review results, patches, plans) to disk, not just session context, to survive context compression.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
