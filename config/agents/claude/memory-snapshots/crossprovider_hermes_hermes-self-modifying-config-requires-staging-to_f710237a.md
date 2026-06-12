---
name: crossprovider hermes hermes-self-modifying-config-requires-staging-to
description: Hermes self-modifying config requires staging to separate file, not live mutation
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [hermes-config, self-modifying-agent, safety-gates]
---

Hard rule for #1583-like config-template work: do NOT mutate live `~/.hermes/config.yaml` mid-run. Stage changes in a separate template file, surface for review, and apply only post-approval. Live mutation during planning breaks self-consistency and recovery.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
