---
name: crossprovider hermes canonical-limitation-sentences-require-verbatim-
description: Canonical limitation sentences require verbatim match, not semantic equivalence
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [planning-artifacts, forbidden-phrases, tdd-contracts]
---

In plan artifacts requiring strict signoff disclaimers (e.g. 'This demo does not constitute foundry-qualified verification'), the limitation sentence must be required exactly verbatim. Allowing 'semantically equivalent' variants opens overclaim loopholes. Test-contract span must EXCLUDE the canonical sentence before scanning for forbidden tokens to avoid self-collision.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
