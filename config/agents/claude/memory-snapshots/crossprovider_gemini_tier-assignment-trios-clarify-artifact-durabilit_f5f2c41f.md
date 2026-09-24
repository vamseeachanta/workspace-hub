---
name: crossprovider gemini tier-assignment-trios-clarify-artifact-durabilit
description: Tier-assignment trios clarify artifact durability and authority
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [architecture, durability, governance]
---

Artifacts are explicitly assigned to three tiers: Tier-1 (git-tracked authoritative), Tier-2 (preferred-when-reachable, e.g., mounted source L1 files), Tier-3 (local-only, never authoritative, e.g., audit logs, run caches). This clarity on what is durable vs ephemeral prevents confusion about truth sources and enables safe fallbacks.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
