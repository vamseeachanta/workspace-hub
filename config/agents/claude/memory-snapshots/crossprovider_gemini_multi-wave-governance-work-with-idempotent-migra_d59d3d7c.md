---
name: crossprovider gemini multi-wave-governance-work-with-idempotent-migra
description: Multi-wave governance work with idempotent migration contracts
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [governance, migrations, agent-routing, multi-wave]
---

User systematically eliminates sprawl (specs in WRK-188, modules in WRK-201/202, work-queue metadata in WRK-185) through fail-safe migrations. Each wave includes dry-run validation, sha256sum verification, and idempotency checks (second --apply on clean state must produce no diff). Agents require deterministic routing paths; sprawl breaks this.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
