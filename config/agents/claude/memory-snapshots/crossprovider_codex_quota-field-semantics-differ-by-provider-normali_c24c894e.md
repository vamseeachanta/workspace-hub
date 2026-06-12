---
name: crossprovider codex quota-field-semantics-differ-by-provider-normali
description: Quota field semantics differ by provider; normalize at boundary
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [provider-specific, quota-management, data-normalization]
---

Claude logs `week_pct` (consumed), Codex/Gemini log `pct_remaining` (available). Normalization logic must happen at provider ingestion point, not in display/threshold logic downstream. Otherwise thresholds become provider-specific.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
