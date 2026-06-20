---
name: crossprovider codex generated-test-outputs-contain-nondeterministic-
description: Generated test outputs contain nondeterministic environment fingerprints
metadata:
  type: reference
  source: codex
  bridged: 2026-06-19
  tags: [testing, generated-output, portability, ci-cd]
---

Test baselines, benchmark reports, and generated YAML/JSON contain hardcoded local absolute paths, run timestamps, and matplotlib object IDs that churn on every run. These make diffs noisy and artifacts non-portable. Before committing generated outputs, validate that paths are scrubbed and timestamps are stripped.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
