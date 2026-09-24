---
name: crossprovider gemini yaml-blocking-condition-is-informational-only-en
description: YAML blocking_condition is informational only — enforcement requires shell code
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [work-queue, stage-contracts, yaml-semantics]
---

Stage YAML files (like stage-19-close.yaml) use `blocking_condition` as documentation, not execution. WRK-1131 found that actual enforcement must happen in shell scripts (e.g., close-item.sh calling feature-close-check.sh) or in exit_stage.py. YAML documents intent but does not enforce checks.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
