---
id: workspace-hub#1293
title: "Run batch deep extraction on all naval architecture manifests"
type: standard
status: pending
priority: high
complexity: moderate
route: B
created_at: 2026-03-19
target_repos: [workspace-hub]
computer: dev-primary
plan_workstations: [dev-primary]
execution_workstations: [dev-primary]
category: document-intelligence
subcategory: knowledge-extraction
parent: WRK-1339
blocked_by: []
github_issue_ref: https://github.com/vamseeachanta/workspace-hub/issues/1293
stage_evidence_ref: .claude/work-queue/assets/WRK-1369/evidence/stage-evidence.yaml
spec_ref: specs/modules/WRK-1369-batch-deep-extract-naval.md
plan_reviewed: true
plan_approved: true
---

## Mission

Execute `batch-deep-extract-naval.sh` on all 55 textbook/standard manifests. The multi-format parsers (EN400, Tupper/Biran, Attwood/PNA) are built and tested but have never been run against real manifests. This is the actual extraction step.

## What

1. Run `bash scripts/data/doc-intelligence/batch-deep-extract-naval.sh` (non-dry-run)
2. Verify extraction reports generated in `data/doc-intelligence/extraction-reports/naval-architecture/`
3. Count total worked examples extracted per textbook
4. Run `assess-extraction-quality.py --report` to get use_as_test counts
5. Rebuild JSONL indexes with `build-doc-intelligence.py --force`
6. Document yield vs plan expectation (target: 150-200 examples)

## Acceptance Criteria

1. Extraction reports exist for all 55 manifests
2. Total deep-extracted examples >= 100
3. JSONL indexes rebuilt with deep records preferred
4. Yield report written to `data/doc-intelligence/extraction-yield-report.yaml`
