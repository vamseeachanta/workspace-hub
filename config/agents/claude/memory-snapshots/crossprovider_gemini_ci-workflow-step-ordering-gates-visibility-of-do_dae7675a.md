---
name: crossprovider gemini ci-workflow-step-ordering-gates-visibility-of-do
description: CI workflow step ordering gates visibility of downstream test failures
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [ci-workflows, github-actions, test-gates, feedback-loops]
---

When linting steps run before smoke tests in a CI job, lint failures abort the job before smoke tests execute, masking underlying test health. Reordering steps to run smoke tests first (or in parallel) surfaces hidden test failures earlier and provides faster feedback on actual test viability.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
