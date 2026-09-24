---
name: crossprovider codex plan-review-artifact-metadata-contract-is-missin
description: Plan-review artifact metadata contract is missing
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [plan-review, artifact-contract, continuous-planning, metadata]
---

Review artifacts should carry machine-checkable headers (issue, plan path, commit SHA, Plan-SHA256, provider, verdict, timestamp, reviewed revision) to support the continuous-planning pipeline (issue #2489). Current heuristics in `continuous-planning-pipeline.py` parse via filename trust and fragile regex (first APPROVE/MINOR/MAJOR match anywhere, Plan-SHA256 line recognition without strict parsing).

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
