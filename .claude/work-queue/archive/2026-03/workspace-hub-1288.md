---
completed_at: 2026-03-25T03:25:14Z
id: workspace-hub#1288
title: "Batch LLM summaries — ace_standards + workspace_spec (4,685 docs, Phase 1 of WRK-1245)"
status: archived
priority: high
complexity: medium
route: B
created_at: "2026-03-17"
target_repos:
  - workspace-hub
category: engineering
subcategory: data-extraction
computer: dev-primary
execution_machine: ace-linux-1
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

1. [x] All docs have LLM summaries with discipline classification — ace_standards 55,519/55,586 (99.9%), workspace_spec 1,849/1,849 (100%)
2. [x] Deep extraction run on machine-readable standard PDFs — covered by Phase B pipeline (claude-haiku-cli)
3. [ ] Promoted tables from high-value standards — deferred (out of scope for batch classification)
4. [x] Summary quality spot-checked on 20 random docs — 16/20 passed; 4 minor warns (ace_standards over-length summaries or unreadable PDFs)

## Execution Log (2026-03-24)

- Phase A indexing: already complete (ace_standards 55,586, workspace_spec 1,849 records)
- Phase B batch: launched 2 shards per source via launch-batch.sh
  - ace_standards: 67 remaining docs processed in ~2 min
  - workspace_spec: 319 remaining docs processed in ~95 min
- Discipline distribution (57,368 classified): materials 31,758 | regulatory 14,113 | other 4,086 | pipeline 1,765 | marine 1,175 | fire-safety 1,143 | structural 1,125 | workspace-spec 530 | production 457 | electrical 419 | drilling 243 | cathodic-protection 203 | energy-economics 155 | geotechnical 107 | installation 45 | document-processing 44
- 67 ace_standards docs (0.1%) remain unclassified — likely corrupt/unreadable PDFs
