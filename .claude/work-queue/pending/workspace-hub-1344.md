---
id: workspace-hub#1344
title: "create atomic capture-wrk.sh to fix /work add bootstrap errors"
status: pending
priority: high
complexity: medium
created_at: 2026-03-24T09:24:17Z
parent:
target_repos:
  - workspace-hub
commit:
spec_ref:
related: []
blocked_by: []
synced_to: []
plan_reviewed: false
plan_approved: false
percent_complete: 0
computer: ace-linux-2
execution_workstations: [ace-linux-2]
plan_workstations: [ace-linux-2]
provider: claude
provider_alt:
stage_evidence_ref: .claude/work-queue/assets/WRK-1344/evidence/stage-evidence.yaml
subcategory: work-queue
category: harness
github_issue_ref: https://github.com/vamseeachanta/workspace-hub/issues/1344
---
# Create Atomic capture-wrk.sh to Fix /work add Bootstrap Errors

## Mission
The `/work add` capture flow currently hits a chicken-and-egg problem: hooks demand stage-evidence.yaml before allowing writes, but start_stage.py demands the pending file before creating evidence. This causes 5+ sequential errors for a simple capture operation.

Create a single `capture-wrk.sh` script that atomically bootstraps a new WRK item through the entire Stage 1 capture flow.

## Context — Error Chain Observed (2026-03-24)
1. enforce-active-stage.sh blocks Write tool (no stage-evidence for new item)
2. start_stage.py fails (pending file doesn't exist yet)
3. enforce-no-bash-evidence.sh blocks cat > to evidence dir
4. exit_stage.py fails (missing user-review-capture.yaml)
5. exit_stage.py fails (checklist-01.yaml incomplete)
6. exit_stage.py hangs (wait-for-approval.sh polling offline GitHub issue)

## Acceptance Criteria
- [ ] New script: scripts/work-queue/capture-wrk.sh that accepts title + optional fields
- [ ] Calls gh-next-id.sh for ID allocation
- [ ] Writes pending/WRK-NNN.md with valid frontmatter
- [ ] Creates evidence dir + stage-evidence via start_stage.py
- [ ] Writes checklist-01.yaml and user-review-capture.yaml
- [ ] Exits stage 1 cleanly (skip GitHub gate when offline)
- [ ] Whitelisted in enforce-active-stage.sh hook
- [ ] Works on all machines (Linux + Windows WSL)
- [ ] /work add skill updated to call capture-wrk.sh instead of manual Write
