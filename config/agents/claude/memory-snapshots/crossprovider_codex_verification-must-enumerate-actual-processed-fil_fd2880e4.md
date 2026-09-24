---
name: crossprovider codex verification-must-enumerate-actual-processed-fil
description: Verification must enumerate actual processed files against coverage claims
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [verification, quality-assurance]
---

Claim 'processed exactly 12 PDFs' must match by file listing, not by page count. Session 4 found a claim that missed one usable PDF that existed but was not processed. Compare claimed file set against actual action-taken entries in log/index before sealing coverage.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
