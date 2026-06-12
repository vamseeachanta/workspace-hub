---
name: crossprovider hermes metadata-pointers-to-closed-resources-outlive-ro
description: Metadata pointers to closed resources outlive route corrections
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [metadata, cleanup, partial-fix]
---

In #88, route maps were updated to skip closed #79, but `generated_for_issue` metadata still referenced the closed issue. Updating active routes is insufficient; must also clean up stale metadata/pointers that record historical context but create false impression of full elimination.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
