---
name: crossprovider codex stage-metadata-contracts-need-executable-enforce
description: Stage metadata contracts need executable enforcement
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [workflow, stages, contracts]
---

Documenting a blocking condition or exit artifact requirement in stage YAML (blocking_condition, exit_artifacts) does not enforce it unless the executor (close-item.sh, exit_stage.py) actively checks/runs the gate. Metadata alone is inert. WRK-1131 showed feature-close-check.sh in stage-19.yaml but no caller of that script.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
