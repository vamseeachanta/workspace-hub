---
name: crossprovider hermes silent-defaults-in-config-validation-weaken-data
description: Silent defaults in config validation weaken data contracts
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [data-contracts, config-validation, silent-defaults]
---

Config validation via `.get(key, default)` allows tools to generate results with missing critical inputs, causing semantic drift. B1528: OCIMF current loads depend on vessel beam/draft, but config silently filled missing values, allowing contradictory claims (report used hull-current terms while YAML disclaimed them). Fail-fast on required inputs.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
