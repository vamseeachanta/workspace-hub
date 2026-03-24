---
id: workspace-hub#1307
title: "Update paths and remove old skills"
status: pending
priority: high
complexity: medium
created_at: "2026-03-21"
parent: WRK-1321
blocked_by: []  # WRK-5112 done 2026-03-23
route: B
plan_reviewed: false
plan_approved: false
target_repos: [workspace-hub]
computer: dev-primary
orchestrator: claude
plan_workstations: [dev-primary]
execution_workstations: [dev-primary]
category: work-queue-infrastructure
subcategory: skill-architecture
github_issue_ref: https://github.com/vamseeachanta/workspace-hub/issues/1307
---

## Mission

Patch orchestration scripts for new folder-skill paths, remove old overlapping skill trees and bare stage files, verify all integrations work. OUT: modifying stage logic, changing contracts, or altering the 20-stage lifecycle.

## What / Why

After WRK-5110 (orchestrator), WRK-5111 (20 stage folder-skills), and WRK-5112 (script redistribution), the new two-tier structure is in place but old skill trees and bare stage files remain. Orchestration scripts may still reference flat paths. This final child cleans up the old structure and verifies everything works end-to-end.

## Acceptance Criteria

- [ ] AC1: dispatch-run.sh works with new stage folder paths
- [ ] AC2: exit_stage.py finds stage contracts in new locations
- [ ] AC3: verify_checklist.py works with new paths
- [ ] AC4: Old skill trees removed: coordination/work-queue sub-skills, workflow-gatepass sub-skills
- [ ] AC5: Bare stage-NN.md files removed (deferred from WRK-5111 AC6)
- [ ] AC6: All pre-commit hooks still work
- [ ] AC7: Full lifecycle test: dispatch-run.sh on a test WRK succeeds

## Entry Reads

- scripts/work-queue/dispatch-run.sh
- scripts/work-queue/exit_stage.py
- scripts/work-queue/verify-gate-evidence.py
- scripts/work-queue/verify_checklist.py
- .claude/skills/coordination/workspace/work-queue/SKILL.md (old tree)
- .claude/skills/workspace-hub/workflow-gatepass/SKILL.md (old tree)
- .claude/skills/workspace-hub/stages/stage-*.md (bare files to remove)
