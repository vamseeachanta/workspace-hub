---
name: crossprovider codex cross-repo-contracts-need-pinned-version-hash-an
description: Cross-repo contracts need pinned version hash and compat windows in consuming repo
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [contract, cross-repo, versioning]
---

When a verifier runs in repo A but the contract lives in repo B, silent drift occurs. Consuming repo must pin contract hash, define compat windows, and fail CI on unknown schema versions rather than relying on implicit parity.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
