---
name: crossprovider codex behavioral-claims-in-plans-require-retrieval-ver
description: Behavioral claims in plans require retrieval verification
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [review, verification, source-of-truth]
---

Statements like 'currently does X' or 'returns None on failure' must be verified against source code, not trusted from plan text. Plans can cite outdated or incorrect behavior. Adversarial review must grep and read actual implementation to confirm behavioral claims.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
