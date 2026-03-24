---
id: workspace-hub#1329
title: "Fix Gemini cross-review NO_OUTPUT — CLI returns exit 0 with invalid JSON"
status: done
priority: medium
complexity: medium
route: B
created_at: "2026-03-24"
target_repos:
  - workspace-hub
category: engineering
subcategory: infrastructure
computer: dev-primary
plan_workstations:
  - dev-primary
execution_workstations:
  - dev-primary
blocked_by: []
tags: [cross-review, gemini, bug-fix]
github_issue_ref: https://github.com/vamseeachanta/workspace-hub/issues/1329
plan_reviewed: true
plan_approved: true
stage_evidence_ref: .claude/work-queue/assets/WRK-5139/evidence/stage-evidence.yaml
---

## Mission

Fix the Gemini cross-review pipeline where the Gemini CLI returns exit 0 but produces invalid/empty JSON output. The renderer (render-structured-review.py) fails to extract valid structure, and the validator rejects it as NO_OUTPUT. Investigate whether the issue is credential/mode misconfiguration (YOLO mode), prompt formatting, or output parsing.

## Acceptance Criteria

1. [ ] Diagnose root cause: credential state, YOLO mode, or output format mismatch
2. [ ] submit-to-gemini.sh handles malformed CLI output gracefully (retry or clear error)
3. [ ] Gemini cross-review produces valid structured output for a test WRK
4. [ ] Fallback mechanism works when Gemini genuinely unavailable (not silent NO_OUTPUT)
