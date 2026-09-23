---
name: crossprovider codex workflow-triggers-must-cover-all-generator-input
description: Workflow triggers must cover all generator input dependencies
metadata:
  type: reference
  source: codex
  bridged: 2026-07-30
  tags: [ci-workflow, test-freshness, edge-cases]
---

CI path filters that trigger on output directories can miss fixture/data inputs that generators read. Stale generated output can merge undetected when only the fixture changes. Include all input paths (fixtures, configs, templates) alongside output paths in workflow triggers.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
