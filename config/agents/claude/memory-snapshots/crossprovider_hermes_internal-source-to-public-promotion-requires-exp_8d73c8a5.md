---
name: crossprovider hermes internal-source-to-public-promotion-requires-exp
description: Internal-source-to-public promotion requires explicit external sanitization record, not just residency relabeling
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [promotion-gates, source-provenance, fail-closed]
---

Schema accepting `source_class = internal-note` with `output_residency = public_llm_wiki` allows silent source laundering. Fail-closed requires explicit durable promotion artifact (external review/sanitization ledger) proving internal→public conversion, not just a field flip. Absence of promotion_record for public outputs claiming internal sources is a blocker.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
