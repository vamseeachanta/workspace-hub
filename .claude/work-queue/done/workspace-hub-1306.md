---
id: workspace-hub#1306
title: "Redistribute scripts to stage folders"
status: done
percent_complete: 100
completed_at: 2026-03-23T19:50:00Z
priority: high
complexity: B
route: B
created_at: "2026-03-21"
parent: WRK-1321
blocked_by: []
target_repos: [workspace-hub]
computer: dev-primary
orchestrator: claude
plan_workstations: [dev-primary]
execution_workstations: [dev-primary]
category: work-queue-infrastructure
subcategory: skill-architecture
github_issue_ref: https://github.com/vamseeachanta/workspace-hub/issues/1306
tags: [skills, folder-skills, script-redistribution]
plan_reviewed: true
plan_approved: true
spec_ref: specs/wrk/WRK-5112/plan.md
claim_routing_ref: .claude/work-queue/assets/WRK-5112/claim-evidence.yaml
stage_evidence_ref: .claude/work-queue/assets/WRK-5112/evidence/stage-evidence.yaml
claim_quota_snapshot_ref: config/ai-tools/agent-quota-latest.json
---
## Mission

Move stage-specific scripts from the flat scripts/work-queue/ directory into their corresponding stage-NN-name/scripts/ folder-skill directories, keeping shared/orchestration scripts in place. OUT: modifying script logic, changing stage contracts, or removing old skill trees (that is WRK-5113).

## What / Why

After WRK-5110 (orchestrator) and WRK-5111 (20 stage folder-skills), the folder-skill structure exists but scripts remain in the flat scripts/work-queue/ directory. Anthropic best practices require script co-location — stage-specific scripts should live inside their stage folder scripts/ directory for discoverability and progressive disclosure.

## Acceptance Criteria

- [x] AC1: Script-to-stage mapping YAML created (each script classified as stage-specific or shared)
- [x] AC2: Stage-specific scripts moved to stage-NN-name/scripts/ directories
- [x] AC3: Shared/orchestration scripts remain in scripts/work-queue/
- [x] AC4: No broken imports or references after redistribution
- [x] AC5: All existing tests pass after move

## Entry Reads

- .claude/skills/workspace-hub/work-queue-orchestrator/references/stage-mapping.yaml
- scripts/work-queue/*.sh (all shell scripts)
- scripts/work-queue/*.py (all Python scripts)
- .claude/skills/workspace-hub/stages/stage-*/contract.yaml (to identify stage-specific hooks/scripts)
