---
name: crossprovider codex loose-temporal-sequencing-language-in-production
description: Loose temporal sequencing language in production gates creates incidents
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [production, sequencing, ambiguity]
---

Using 'same day' or 'back-to-back' without bounded intervals (minutes, merge order) leaves production sequencing ambiguous. Precedent #2391: 'same day' deferral left room for out-of-order deploys. Fix: production-critical sequencing must specify explicit intervals ('within 30 min of validation') or concrete gates ('merge #2357 first, await prod confirm').

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
