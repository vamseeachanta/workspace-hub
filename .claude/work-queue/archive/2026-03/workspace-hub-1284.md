---
id: workspace-hub#1284
title: "Add scatter chart example YAML for calc report test coverage"
status: archived
priority: low
complexity: simple
compound: false
created_at: 2026-03-23T00:00:00Z
target_repos:
  - workspace-hub
category: engineering-calculations
related:
  - WRK-5120
blocked_by: []
synced_to: []
computer: local-analysis
plan_workstations: [local-analysis]
execution_workstations: [local-analysis]
subcategory: reporting
route: A
plan_reviewed: true
plan_approved: true
spec_ref: specs/wrk/WRK-5125/plan.md
github_issue_ref: https://github.com/vamseeachanta/workspace-hub/issues/1284
claim_routing_ref: .claude/work-queue/assets/WRK-5125/claim-evidence.yaml
stage_evidence_ref: .claude/work-queue/assets/WRK-5125/evidence/stage-evidence.yaml
claim_quota_snapshot_ref: config/ai-tools/agent-quota-latest.json
percent_complete: 100
completed_at: 2026-03-24T01:56:04Z
---
## Description

Add a scatter chart type example to `examples/reporting/` — currently 0 scatter examples exist (only bar, line, log_log). The test suite (`test_chart_validation.py`) tests scatter with synthetic data but no real example YAML validates the full pipeline.

## Acceptance Criteria

- [x] New example YAML with at least one scatter chart in examples/reporting/
- [x] test_chart_validation.py parametrized tests automatically pick it up
