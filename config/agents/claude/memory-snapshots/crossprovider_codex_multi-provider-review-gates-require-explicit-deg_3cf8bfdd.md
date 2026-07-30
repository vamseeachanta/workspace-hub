---
name: crossprovider codex multi-provider-review-gates-require-explicit-deg
description: Multi-provider review gates require explicit degradation decisions when providers unavailable
metadata:
  type: reference
  source: codex
  bridged: 2026-07-09
  tags: [governance, multi-provider, degradation-decisions, review-gates]
---

Issue-planning gates that require 2+ provider reviews cannot be automatically satisfied if some providers are unavailable (auth failures, service issues). If proceeding with fewer providers post-MAJOR, record a deliberate governance decision in the plan (e.g., 'Codex-only due to provider unavailability') rather than silently accepting incomplete review.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
