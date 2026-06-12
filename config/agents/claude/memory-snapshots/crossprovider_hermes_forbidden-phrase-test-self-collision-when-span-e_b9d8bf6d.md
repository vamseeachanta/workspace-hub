---
name: crossprovider hermes forbidden-phrase-test-self-collision-when-span-e
description: Forbidden-phrase test self-collision when span excludes the canonical sentence
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [tdd-contracts, forbidden-phrases, test-logic]
---

When a plan's test contract requires a canonical limitation sentence verbatim and also scans for forbidden tokens, the test-contract SPAN must explicitly EXCLUDE the canonical sentence before counting forbidden-token hits. Otherwise, the canonical sentence itself triggers forbidden-token counts, collapsing the test into self-sabotage.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
