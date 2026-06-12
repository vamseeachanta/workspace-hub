---
name: crossprovider hermes unbounded-intake-phases-cause-multi-session-cycl
description: Unbounded intake phases cause multi-session cycling
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [session-design, intake-gate]
---

Sessions repeatedly re-entered intake discovery for issue #2665 without producing exit artifacts (plan file, draft issue, or GitHub comment). When intake has no defined exit gate, subsequent sessions post-compaction restart the gather phase. Set explicit intake boundary: first intermediate artifact (e.g., plan file commit, issue draft, intake summary comment) marks completion and prevents re-discovery loops.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
