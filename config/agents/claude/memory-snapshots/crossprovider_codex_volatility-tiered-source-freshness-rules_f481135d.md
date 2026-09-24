---
name: crossprovider codex volatility-tiered-source-freshness-rules
description: Volatility-tiered source freshness rules
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [documentation, source-management, freshness, policy]
---

Different source types require different update frequencies: critical (same-day for status/security/legal/compliance), high (7 days for APIs/release-notes), medium (quarterly for stable docs), low (6–12 months for conceptual-only). These rules must be consistent across test assertions, source contracts, and documentation or implementation will be internally inconsistent.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
