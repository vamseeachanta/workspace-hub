---
name: crossprovider hermes architecture-tests-are-the-contract-enforcement-
description: Architecture tests are the contract enforcement mechanism—no separate config file
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [testing-as-spec, contract-enforcement, no-separate-config]
---

Data-layer contracts are enforced via test suites (tests/architecture/test_data_layer_contract.py) with fixtures, not a standalone config/data-layer-contract.yml. Tests define valid source classes, transitions, boundary rules, and inventory requirements. Tests are ground truth; missing tests mean rules are not enforced.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
