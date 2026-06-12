---
name: crossprovider gemini fail-open-audit-mechanisms-undermine-governance
description: Fail-open audit mechanisms undermine governance
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [audit, governance, design-pattern]
---

Audit logging with `|| true` or `[[ -x $LOGGER ]] ||` means failures silently drop events, defeating the mechanism. Audit trails must fail-closed or require explicit bypass tokens with reason logging; governance gates need accountability (WRK-1087).

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
