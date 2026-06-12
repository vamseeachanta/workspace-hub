---
name: crossprovider gemini two-tier-legacy-discriminator-for-extending-gate
description: Two-tier legacy discriminator for extending gates across time
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [backwards-compatibility, gates, work-queue]
---

When extending gates to new providers (Codex, Gemini) or new work items created before gate enforcement, use two-tier discriminator: (1) ID number < cutoff (e.g., WRK < 658) → skip gate, (2) timestamp < cutoff date → skip gate. Prevents breaking pre-existing work while enforcing new requirements. WRK-658 uses `LOG_GATE_SINCE = 2026-03-09` + `if int(id_num) < 658`.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
