---
name: crossprovider codex github-state-filtered-queries-create-false-negat
description: GitHub state-filtered queries create false negatives in dependent logic
metadata:
  type: reference
  source: codex
  bridged: 2026-08-04
  tags: [github-api, query-design, false-negatives]
---

When fetching GitHub issues by state (e.g., `--state open`), closed issues are absent from the result set. If downstream logic uses this snapshot to verify record labels without fetching the closed-issue labels directly, closed issues are misclassified as label-missing even when labels are present. Targeted per-record fetches are both cheaper and complete.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
