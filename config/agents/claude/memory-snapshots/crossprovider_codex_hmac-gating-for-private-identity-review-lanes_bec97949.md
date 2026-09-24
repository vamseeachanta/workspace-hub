---
name: crossprovider codex hmac-gating-for-private-identity-review-lanes
description: HMAC-gating for private identity review lanes
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [hmac, private-identity, security, environment-gating]
---

Private identity mapping lanes require: HMAC key from environment only (fail on missing/empty/placeholder), deterministic canonical private identity input (not just opaque public lane ID), test-key rejection in production mode, and commitment input defined explicitly. The private identity map and HMAC material must remain untracked and operator-controlled; direct extraction batch generation stays blocked until identity review produces reviewed candidates.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
