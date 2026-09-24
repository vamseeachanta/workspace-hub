---
name: crossprovider codex row-set-identity-must-include-envelope-hash-in-k
description: Row-set identity must include envelope hash in kind-specific ordering keys
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [determinism, identity-keys, envelope-versioning]
---

When response envelopes can have multiple approved revisions sharing a response ID, kind-specific keys lacking the envelope hash permit collisions and non-deterministic ordering. Metadata joins require both response ID and envelope hash; canonical ordering cannot use deficient keys without creating collisions that violate exact row-set commitments.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
