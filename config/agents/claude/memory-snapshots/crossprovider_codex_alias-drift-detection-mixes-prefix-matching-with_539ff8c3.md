---
name: crossprovider codex alias-drift-detection-mixes-prefix-matching-with
description: Alias-drift detection mixes prefix matching with family membership
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [category-aliases, grouping-findings, false-positives]
---

#2486 detector false-triggered on `business/tax` with `category: business/admin` because it matched the top-level `business` prefix against the alias family token `business_admin`. Fix: only add raw tokens to `used_raw` if their normalized form is in the alias-family token set; prefix-matching alone is not sufficient.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
