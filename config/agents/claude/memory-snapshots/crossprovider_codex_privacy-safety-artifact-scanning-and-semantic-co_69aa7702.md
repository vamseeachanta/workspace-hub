---
name: crossprovider codex privacy-safety-artifact-scanning-and-semantic-co
description: Privacy/safety artifact scanning and semantic correctness are orthogonal defect classes
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [security, privacy, validation, orthogonal-gates]
---

Unsafe-token scans can pass (no raw paths/titles exposed) while semantic correctness fails (duplicated candidates, wrong classifications). Run both checks separately; do not let one pass gate the other. Example: staged artifacts passed privacy scan but had duplicate post-dedupe source IDs, requiring separate consistency review.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
