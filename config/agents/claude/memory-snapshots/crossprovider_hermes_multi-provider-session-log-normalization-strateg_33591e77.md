---
name: crossprovider hermes multi-provider-session-log-normalization-strateg
description: Multi-provider session log normalization strategies
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [audit, logging, multi-provider]
---

Classify missing repo reads without slashes/dots as 'symbolic_reference' (skill names) not missing files. Codex needs stateful dedup by timestamp+name+arguments (per native session structure). Hermes raw logs contain both structured and symbolic reads; normalize by provider context, not globally.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
