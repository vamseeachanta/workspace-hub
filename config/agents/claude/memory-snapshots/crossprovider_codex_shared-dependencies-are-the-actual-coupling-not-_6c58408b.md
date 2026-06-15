---
name: crossprovider codex shared-dependencies-are-the-actual-coupling-not-
description: Shared dependencies are the actual coupling, not architecture
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [dependencies, coupling, independence-claims, vendor-tools]
---

When claiming independence between two tools (e.g., extract-msg vs python-oxmsg), don't stop at 'both are pure Python.' Verify dependency overlap: both depend on olefile for CFB parsing, so they share binary format handling logic. The actual independence surface is narrower than the claim.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
