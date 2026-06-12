---
name: crossprovider hermes validator-cli-should-not-require-explicit-argume
description: Validator CLI should not require explicit arguments for common runs
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [cli-design, usability, validation]
---

When a validator script accepts optional arguments (artifact-dir, report-path), provide sensible defaults (e.g., artifacts/retrieval/public-graph for artifact-dir, inferred date-stamped path under docs/reports/ for report-path) so users can run `./validate_artifacts.py` without flags. Explicit-only CLIs burden TDD and integration.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
