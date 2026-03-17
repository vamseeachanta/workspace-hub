---
name: work-queue-work-item-format
description: 'Sub-skill of work-queue: Work Item Format.'
version: 1.8.0
category: coordination
type: reference
scripts_exempt: true
---

# Work Item Format

## Work Item Format


Required frontmatter fields: `id`, `title`, `status` (pending|working|blocked|done), `priority` (high|medium|low), `complexity` (simple|medium|complex), `created_at`, `target_repos`, `computer`, `plan_workstations`, `execution_workstations`, `category`, `subcategory`. Route C also requires `spec_ref`. Body: `## Mission` (one-sentence scope boundary) + `## What / Why / Acceptance Criteria`.

Optional field: `onet_category` — O*NET SOC code + label (e.g. `"15-1251.00 — Computer Programmers"`). Tag with `uv run --no-project python scripts/ai/tag_onet.py WRK-NNN`. Used by `observed_exposure_report.py --by-onet` to benchmark automation rates against Anthropic's occupational exposure data.
