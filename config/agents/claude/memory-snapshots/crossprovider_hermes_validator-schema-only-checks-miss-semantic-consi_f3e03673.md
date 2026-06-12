---
name: crossprovider hermes validator-schema-only-checks-miss-semantic-consi
description: Validator schema-only checks miss semantic consistency
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [validation, data-integrity, llm-wiki]
---

LLM-wiki issue #77: validator checks self-reported JSON fields but not CSV/report body fidelity. CSV row counts can diverge from node counts; report sections can be stale/truncated without detection; digest can be invalid hex. Schema validation is necessary but insufficient; validators must enforce consistency between artifact formats (CSV row count = node count, report thresholds = summary values, digest validity).

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
