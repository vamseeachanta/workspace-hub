---
name: crossprovider hermes auto-host-routing-false-negative-on-missing-data
description: Auto host routing false-negative on missing_data
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [dispatch, routing]
---

Dispatch policy selecting first host meeting status/git criteria can fail later if that host has missing_data. Check missing_data during host selection, not after.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
