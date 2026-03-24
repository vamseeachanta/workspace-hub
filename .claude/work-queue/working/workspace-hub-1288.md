---
id: workspace-hub#1288
title: "Batch LLM summaries — ace_standards + workspace_spec (4,685 docs, Phase 1 of WRK-1245)"
status: working
priority: high
complexity: medium
route: B
created_at: "2026-03-17"
target_repos:
  - workspace-hub
category: engineering
subcategory: data-extraction
computer: dev-primary
plan_workstations:
  - dev-primary
execution_workstations:
  - dev-primary
parent: WRK-1245
blocked_by: []
tags: [doc-intelligence, extraction, llm-summary, phase-1]
key_scripts:
  - scripts/data/document-index/phase-b-claude-worker.py
github_issue_ref: https://github.com/vamseeachanta/workspace-hub/issues/1288
plan_reviewed: true
plan_approved: true
spec_ref: specs/wrk/WRK-1295/plan.md
claim_routing_ref: .claude/work-queue/assets/WRK-1295/claim-evidence.yaml
stage_evidence_ref: .claude/work-queue/assets/WRK-1295/evidence/stage-evidence.yaml
claim_quota_snapshot_ref: config/ai-tools/agent-quota-latest.json
---
## Mission

Run LLM summaries on 4,685 high-value documents (ace_standards 3,969 + workspace_spec 716).
These are engineering standards and specs — highest value per document in the corpus.
Phase 1 of WRK-1245 feature decomposition.

## Scope

- Run `phase-b-claude-worker.py --source ace_standards` and `--source workspace_spec`
- Deep extraction on engineering standard PDFs (tables, constants, equations)
- Promote extracted tables to `data/standards/promoted/`
- Budget: ~$9 at Haiku rates

## Acceptance Criteria

1. [ ] All 4,685 docs have LLM summaries with discipline classification
2. [ ] Deep extraction run on machine-readable standard PDFs
3. [ ] Promoted tables from high-value standards
4. [ ] Summary quality spot-checked on 20 random docs
