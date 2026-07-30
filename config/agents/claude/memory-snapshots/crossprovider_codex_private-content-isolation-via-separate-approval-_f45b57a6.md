---
name: crossprovider codex private-content-isolation-via-separate-approval-
description: Private-content isolation via separate approval cycles
metadata:
  type: reference
  source: codex
  bridged: 2026-07-15
  tags: [privacy, api-design, governance, architecture]
---

When APIs handle both private and public content, architecturally prohibit direct writes to public/generic surfaces (e.g., llm-wiki). Instead, require separate issue, plan review, and user approval cycles for private-originated features. This prevents accidental leakage and enforces governance boundaries.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
