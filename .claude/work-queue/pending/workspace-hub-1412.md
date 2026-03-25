---
id: WRK-1412
title: "LLM-classify ambiguous riser-eng-job files (5k unknown doc types)"
repo: digitalmodel
type: task
complexity: B
priority: low
status: pending
created: 2026-03-25
depends_on: [WRK-1363]
github_issue: https://github.com/vamseeachanta/workspace-hub/issues/1412
github_issue_ref: https://github.com/vamseeachanta/workspace-hub/issues/1412
---

# WRK-1412: LLM-classify ambiguous riser-eng-job files (5k unknown doc types)

## Description

5,050 of 15,449 riser-eng-job literature files have unknown document types after filename pattern matching (67% coverage). Use Claude API to classify remaining files by extracting first 2 pages of PDF text and mapping to document type codes and domain tags.

## Related

- Parent: WRK-1363 (archived)
