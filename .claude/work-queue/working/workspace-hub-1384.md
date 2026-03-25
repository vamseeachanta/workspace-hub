---
id: WRK-1384
title: "Review local-analysis folders for relocation to knowledge center"
repo: workspace-hub
type: task
complexity: B
route: B
priority: medium
status: working
created: 2026-03-24
workstations: [ace-linux-2]
orchestrator: claude
github_issue: https://github.com/vamseeachanta/workspace-hub/issues/1384
github_issue_ref: "https://github.com/vamseeachanta/workspace-hub/issues/1384"
claim_routing_ref: .claude/work-queue/assets/workspace-hub-1384/claim-evidence.yaml
stage_evidence_ref: .claude/work-queue/assets/workspace-hub-1384/evidence/stage-evidence.yaml
claim_quota_snapshot_ref: config/ai-tools/agent-quota-latest.json
---
# WRK-1384: Review local-analysis folders for relocation to knowledge center

## Description

Review all folders (except workspace-hub) and files in `/mnt/remote/ace-linux-2/local-analysis`. Identify what files need to be relocated to the knowledge center at `/mnt/ace/`. This is a file organization and consolidation task to ensure data is stored in the appropriate long-term location.

## Scope

- Inventory all folders and files in `/mnt/remote/ace-linux-2/local-analysis` (excluding workspace-hub)
- Classify each folder/file by type and purpose
- Determine which items belong in `/mnt/ace/` knowledge center
- Produce a relocation plan with source → destination mappings
- Flag any files that should remain in place or be archived differently

## Related

- Knowledge center: `/mnt/ace/`
