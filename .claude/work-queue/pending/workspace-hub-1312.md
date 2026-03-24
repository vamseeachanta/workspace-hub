---
id: workspace-hub#1312
title: "Phase 1 manual entry for ship dimensions template"
type: standard
status: pending
priority: medium
complexity: moderate
route: A
created_at: 2026-03-23
target_repos: [workspace-hub]
computer: dev-primary
orchestrator: codex
plan_workstations: [dev-primary]
execution_workstations: [dev-primary]
category: document-intelligence
subcategory: manual-curation
parent: WRK-1380
blocked_by: []
github_issue_ref: https://github.com/vamseeachanta/workspace-hub/issues/1312
---

## Mission

Execute a bounded first pass of `WRK-1380` against the recovered
`ship-dimensions.yaml` template so manual curation starts with the highest-value
vessels and reaches a verifiable milestone.

## What

1. Start from `data/doc-intelligence/ship-dimensions.yaml`
2. Fill in capital ships first:
   - battleships (`BB`)
   - aircraft carriers (`CV`, `CVL`, `CVE`, `ACV`)
   - heavy/large cruisers (`CA`, `CB`, `ACR`)
3. Cross-reference at least 5 vessels against Jane's Fighting Ships 2009-2010
4. Mark verified entries with the appropriate `entry_status`
5. Leave lower-priority destroyers and auxiliaries for later phases

## Acceptance Criteria

1. A meaningful Phase 1 subset is complete in `ship-dimensions.yaml`
2. All capital-ship entries present in the generated template are reviewed
3. At least 5 entries are cross-referenced against Jane's
4. `WRK-1380` can report concrete progress instead of remaining only a pending
   umbrella item

## Notes

This child item exists to break the manual ship-dimension effort into an
executable milestone now that the template artifact has been recovered and
generated locally.
