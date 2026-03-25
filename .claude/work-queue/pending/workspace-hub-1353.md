---
id: workspace-hub#1353
title: "Deep extraction & table promotion for ace_standards + workspace_spec (deferred from WRK-1288)"
status: pending
priority: medium
complexity: medium
route: B
created_at: "2026-03-24"
target_repos:
  - workspace-hub
category: engineering
subcategory: data-extraction
parent: WRK-1245
blocked_by: []
tags: [doc-intelligence, extraction, table-promotion, deep-extraction]
github_issue_ref: https://github.com/vamseeachanta/workspace-hub/issues/1353
---
## Mission

Run deep extraction on machine-readable standard PDFs from ace_standards and workspace_spec,
then promote extracted tables to `data/standards/promoted/`. This was deferred from WRK-1288
(acceptance criterion #3) which completed the LLM classification batch.

## Context

WRK-1288 completed Phase B classification for 57,368 docs (ace_standards 99.9%, workspace_spec 100%).
Table promotion was out of scope for that batch classification run but is needed for downstream
data consumers that rely on structured table data.

## Scope

1. Identify machine-readable PDFs with extractable tables from ace_standards + workspace_spec
2. Run deep extraction (tables, constants, equations) on identified PDFs
3. Promote extracted tables to `data/standards/promoted/`
4. Quality-check promoted tables (coordinate with WRK-1295 curation pipeline)

## Acceptance Criteria

1. [ ] Deep extraction run on machine-readable standard PDFs from both sources
2. [ ] Extracted tables promoted to `data/standards/promoted/`
3. [ ] Quality report on promoted tables (row count, numeric column %, usability score)
