---
name: crossprovider hermes schema-scope-per-type-not-global-required-fields
description: Schema scope-per-type, not global required fields
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [schema-design, scope-creep, validation]
---

Broad globally-required fields across diverse artifact types (raw_output, evidence_bundle, internal_report) break backward compatibility and over-constrain scope. Define required fields per artifact type; enforce globally only fields that apply universally. #2748 example: corpus_scope/audience_classification required even for raw outputs, conflicting with contract that raw outputs are 'not deliverables by default.'

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
