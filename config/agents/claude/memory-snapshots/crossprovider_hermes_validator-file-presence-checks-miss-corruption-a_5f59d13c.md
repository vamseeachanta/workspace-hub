---
name: crossprovider hermes validator-file-presence-checks-miss-corruption-a
description: Validator file-presence checks miss corruption and content leakage
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [validation-gap, csv-validation, test-discipline]
---

Validators that only check for artifact file existence (not content/structure) pass over corrupted CSVs, stale data, and untracked paths. CSV content validation and row-count matching against summary metadata are required for fail-closed posture.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
