---
name: crossprovider gemini deterministic-policy-v1-should-freeze-key-parame
description: Deterministic policy v1 should freeze key parameters
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [versioning, policy, reproducibility]
---

For initial version of a normalization/policy feature, explicitly freeze key inputs: normalized units, base year, escalation rate, FX source (static in-repo table, not live API). Document version number and note that future versions can evolve the policy. Avoids ambiguity in reproducibility.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
