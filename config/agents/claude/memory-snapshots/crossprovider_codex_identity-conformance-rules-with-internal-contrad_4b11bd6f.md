---
name: crossprovider codex identity-conformance-rules-with-internal-contrad
description: Identity/conformance rules with internal contradictions signal incomplete design
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [plan-review, identity-contract, compliance]
---

Plans defining identity contracts or rule-enforcement frequently contain contradictory assertions (e.g., 'SHA256 only' vs 'MD5 legacy reads accepted', or 'reject non-sha256 in CLI' vs 'accept md5 in conformance check'). Resolve the single rule before approval; conflicting rules expose unfinished design.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
