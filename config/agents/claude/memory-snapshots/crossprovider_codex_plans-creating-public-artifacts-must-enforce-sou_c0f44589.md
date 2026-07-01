---
name: crossprovider codex plans-creating-public-artifacts-must-enforce-sou
description: Plans creating public artifacts must enforce source-path de-identification before publication
metadata:
  type: reference
  source: codex
  bridged: 2026-06-30
  tags: [security, redaction, public-repo, source-tracking]
---

Plans that extract from private corpus and publish to public repo must distinguish source-path (private raw, never leaked) from public-safe reference (hash or opaque token). No plan should require raw `source_path` field in public ledger/case-study artifacts. Add explicit redaction rule and deny-list grep test before declaring artifact ready for public merge.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
