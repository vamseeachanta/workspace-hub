---
name: crossprovider codex threat-model-consistency-in-exception-categories
description: Threat-model consistency in exception categories
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [data-governance, threat-model, policy-scanning]
---

Data governance scans must apply threat models uniformly across artifact contexts. If raw hashes are identified as membership oracles, they must be flagged consistently, not exempted based on prose framing like "private ledger example." Exception categories that contradict the underlying threat model create undetected vectors.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
