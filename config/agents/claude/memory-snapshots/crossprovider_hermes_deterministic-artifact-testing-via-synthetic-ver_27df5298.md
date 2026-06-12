---
name: crossprovider hermes deterministic-artifact-testing-via-synthetic-ver
description: Deterministic artifact testing via synthetic version
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [artifacts, test-determinism, verification]
---

For generated reports/artifacts: commit a synthetic deterministic version (not live-state output), inject fixed timestamp, then test exact string match against regenerated output. Prevents dirty-state overwrites and validates reproducibility. Concrete test: `test_committed_html_report_matches_deterministic_synthetic_generator_output`.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
