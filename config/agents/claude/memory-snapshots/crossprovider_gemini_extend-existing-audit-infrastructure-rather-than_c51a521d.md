---
name: crossprovider gemini extend-existing-audit-infrastructure-rather-than
description: Extend existing audit infrastructure rather than creating parallel telemetry
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [architecture-governance, telemetry, repo-policy, single-source-of-truth]
---

When auditing runtime patterns or provider behavior, extend existing audit scripts (e.g., provider_session_ecosystem_audit.py) rather than inventing parallel telemetry sources. Centralized audit ownership prevents divergence between generated reports (JSON vs markdown) and keeps the numeric source of truth authoritative.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
