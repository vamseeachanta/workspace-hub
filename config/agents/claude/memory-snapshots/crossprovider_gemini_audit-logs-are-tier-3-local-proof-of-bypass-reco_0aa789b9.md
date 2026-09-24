---
name: crossprovider gemini audit-logs-are-tier-3-local-proof-of-bypass-reco
description: Audit logs are tier-3 local; proof-of-bypass recorded in git commit trailers
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [audit, governance, tier-assignment]
---

Bypass events logged locally in tier-3 JSONL files (never authoritative, gitignored), but proof-of-bypass recorded durably in git commit message trailers (e.g., Planner-Retrieval-Bypass: <reason>). Dual logging provides auditability without duplicating authoritative truth; git log is the durable record.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
