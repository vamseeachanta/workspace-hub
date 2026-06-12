---
name: crossprovider hermes validator-hardcoding-defeats-weekly-cadence
description: Validator hardcoding defeats weekly cadence
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [validation, weekly-cadence, testing-gap, llm-wiki]
---

Weekly-freshness validators that hardcode `DEFAULT_REPORT = docs/reports/2026-05-17-...` fail to find/validate latest dated output. If an old fixed report exists, validator passes against stale data instead of new weekly artifacts, silently breaking the cadence assumption.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
