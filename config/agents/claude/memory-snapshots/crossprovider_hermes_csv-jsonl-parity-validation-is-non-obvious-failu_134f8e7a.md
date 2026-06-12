---
name: crossprovider hermes csv-jsonl-parity-validation-is-non-obvious-failu
description: CSV/JSONL parity validation is non-obvious failure mode
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [data-format, validation, artifact-quality]
---

Artifact generators produce both CSV and JSONL but parity is not automatic. Validator must explicitly parse headers, compare row counts, and verify field values. Silent divergence on headers, extra/missing rows, or value mismatches can pass existence checks.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
