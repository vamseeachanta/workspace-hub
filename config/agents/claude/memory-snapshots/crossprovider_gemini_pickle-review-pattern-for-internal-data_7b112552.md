---
name: crossprovider gemini pickle-review-pattern-for-internal-data
description: Pickle review pattern for internal data
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [code-review, pickle, security-justification]
---

When reviewing pickle use, confirm data source is internal-only (trusted) and justify exceptions with `# nosec B301`. Pair with integration tests on real data to validate serialization round-trip.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
