---
name: crossprovider hermes tdd-validation-gate-sequence-non-negotiable-skip
description: TDD validation gate sequence non-negotiable: skip → silent defects
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [testing, validation, gates]
---

Required sequence: targeted tests → full suite → legal/safety scan → adversarial review before commit. Skipping any stage produces undetected MAJOR findings (confirmed: #2726–#2729 all blocked on review stage). Legal scan diff-only for public repos with pre-existing deny-list hits.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
