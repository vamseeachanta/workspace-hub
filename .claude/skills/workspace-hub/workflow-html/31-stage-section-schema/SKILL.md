---
name: workflow-html-31-stage-section-schema
description: 'Sub-skill of workflow-html: 3.1 Stage Section Schema (+1).'
version: 2.3.0
category: workspace-hub
type: reference
scripts_exempt: true
---

# 3.1 Stage Section Schema (+1)

## 3.1 Stage Section Schema


Each stage is `<section class="stage-section" id="sN">` with `.stage-header onclick=toggle()`,
`.stage-title` (num + name + badge), and `.stage-body`. Gate stages (5, 7, 17) get a `b-gate`
badge. Done/active stages start expanded; pending/na start collapsed (`stage-body collapsed`).

Stage 7 gate-checker fields must appear at line-start (no HTML wrapping) so
`check_plan_confirmation()` can parse `confirmed_by:`, `confirmed_at:`, `decision:`.


## 3.2 Stage Evidence Sources


| Stages | Evidence file(s) |
|--------|-----------------|
| 1 | WRK frontmatter |
| 2 | `evidence/resource-intelligence.yaml` |
| 3 | frontmatter `complexity` + `route` |
| 4 | `## Plan` in WRK body |
| 5 | `evidence/user-review-plan-draft.yaml` |
| 6 | `evidence/cross-review*.md` |
| 7 | `evidence/user-review-plan-final.yaml` |
| 8–9 | `evidence/claim.yaml` |
| 10 | `evidence/execute.yaml` |
| 11, 14 | `evidence/gate-evidence-summary.json` |
| 12 | `evidence/test-results.yaml` |
| 13 | `evidence/cross-review-impl.md` |
| 15 | `evidence/future-work.yaml` |
| 16 | `evidence/resource-intelligence-update.yaml` |
| 17 | `evidence/user-review-close.yaml` |
| 18 | `evidence/reclaim.yaml` (or `na`) |
| 19 | frontmatter `status: done` |
| 20 | WRK file in `archive/` |

---
