---
name: crossprovider hermes configuration-drift-requires-regression-test-gua
description: Configuration drift requires regression test guards
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [configuration, regression-testing, drift-detection]
---

Thresholds, settings, and toggles in YAML/config files revert without test pressure (governance threshold drifted 200→5000). Add pytest assertions that pin production values (e.g., `assert yaml['threshold'] == 200`) to catch silent reverts.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
