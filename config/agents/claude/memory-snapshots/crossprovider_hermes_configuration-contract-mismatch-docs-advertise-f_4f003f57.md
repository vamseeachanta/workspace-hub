---
name: crossprovider hermes configuration-contract-mismatch-docs-advertise-f
description: Configuration contract mismatch: docs advertise flexibility, code hardcodes
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [config, contract, documentation, implementation]
---

When documentation shows configurable env names or registry keys (e.g., `bot_token_env: CUSTOM_VAR`) but runtime code hardcodes them (e.g., `TELEGRAM_HERMES_BOT_TOKEN`), the contract is broken. Registry entries must carry the config keys and runtime code must respect them. Always cross-check docs + example config + implementation to catch misalignment.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
