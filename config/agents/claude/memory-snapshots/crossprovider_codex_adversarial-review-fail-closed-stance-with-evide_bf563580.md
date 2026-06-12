---
name: crossprovider codex adversarial-review-fail-closed-stance-with-evide
description: Adversarial review: fail-closed stance with evidence gates
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [review-methodology, security, fail-closed]
---

Reviews enforce strict fail-closed posture: default NO unless affirmatively verified. For public-facing artifact changes, require explicit evidence that private/client/raw paths don't leak. Use forbidden-literal scans on committed artifacts to block exposure. Multi-round review (R1→patch→R2→patch→R3) converges on defects.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
