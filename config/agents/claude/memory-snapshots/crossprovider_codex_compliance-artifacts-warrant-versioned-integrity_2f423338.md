---
name: crossprovider codex compliance-artifacts-warrant-versioned-integrity
description: Compliance artifacts warrant versioned integrity checking
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [compliance, artifact-integrity, governance]
---

Separate required (approval.txt, approved-heads.env, review-bindings.env) from optional artifacts and include SHA256 sums alongside each. This enables audit reconstruction and detects silent corruption during storage/transfer.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
