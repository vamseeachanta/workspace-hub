---
name: crossprovider hermes partial-implementations-diverge-from-approved-co
description: Partial implementations diverge from approved contracts
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [assessment, contract-verification, partial-landings]
---

Code may land with correct file structure but wrong API signatures or output types. Drilling_riser (#2063) was shipped with imperial fields instead of SI, wrong batch-registration signature. Always verify the implemented contract matches the approved acceptance criteria, not just file presence.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
