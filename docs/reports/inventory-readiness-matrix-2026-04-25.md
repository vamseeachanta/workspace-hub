# Inventory Readiness Matrix

Generated from `config/knowledge/inventory-readiness.yaml` on 2026-04-25.

## Provider queue snapshot

Source: `docs/reports/provider-work-queue.md`
Snapshot generated at: `2026-04-25T09:20:15.784834Z`

These are observed queue values from the provider work queue, not acceptance thresholds.

| Count | Observed value |
|---|---:|
| codex_candidates | 4 |
| gemini_tasks | 1 |
| claude_reviews | 17 |

## Package readiness

| Package | Owner | Preferred next | Raw data | Inventory | LLM wiki | Calculation code | Parametric outputs | Website/GTM |
|---|---|---|---|---|---|---|---|---|
| inventory_readiness_spine | codex | codex | READY | READY | PARTIAL | PARTIAL | MISSING | PARTIAL |
| raw_data_scouting_backlog | gemini | gemini | READY | PARTIAL | MISSING | MISSING | MISSING | MISSING |
| plan_review_and_governance_backlog | claude | claude | READY | READY | PARTIAL | PARTIAL | MISSING | PARTIAL |

## Codex Dispatch

| Package | Rationale | Dependencies | Expected output |
|---|---|---|---|
| inventory_readiness_spine | Implement and maintain the readiness validator/report spine; downstream work remains separately issue-gated. | #2464, #2403, #2346, #2465, #2402, #2392 | `docs/reports/inventory-readiness-matrix-2026-04-25.md` |

## Gemini Dispatch

| Package | Rationale | Dependencies | Expected output |
|---|---|---|---|
| raw_data_scouting_backlog | Run an unexecuted scouting batch to identify source/wiki gaps and produce future package candidates. | #2392, #2403 | `null / provider task will create artifact` |

## Claude Dispatch

| Package | Rationale | Dependencies | Expected output |
|---|---|---|---|
| plan_review_and_governance_backlog | Review and harden downstream package plans before user approval and Codex/Gemini execution. | #2464, #2346, #2465, #2403 | `scripts/review/results/downstream-package-review.md` |

## Downstream issue references

| Package | Issue | Relation | Approval state | Produces stages | Implemented here? |
|---|---:|---|---|---|---|
| inventory_readiness_spine | #2481 | reference | plan-review | calculation_code | no — downstream/reference only |
| inventory_readiness_spine | #2464 | downstream_candidate | plan-approved | inventory | no — downstream/reference only |
| inventory_readiness_spine | #2403 | downstream_candidate | plan-approved | llm_wiki | no — downstream/reference only |
| inventory_readiness_spine | #2346 | downstream_candidate | plan-approved | website_gtm | no — downstream/reference only |
| inventory_readiness_spine | #2465 | downstream_candidate | plan-approved | inventory | no — downstream/reference only |
| inventory_readiness_spine | #2402 | downstream_candidate | plan-review | llm_wiki | no — downstream/reference only |
| inventory_readiness_spine | #2392 | downstream_candidate | open | llm_wiki | no — downstream/reference only |
| raw_data_scouting_backlog | #2392 | downstream_candidate | open | llm_wiki | no — downstream/reference only |
| raw_data_scouting_backlog | #2403 | downstream_candidate | plan-approved | llm_wiki | no — downstream/reference only |
| plan_review_and_governance_backlog | #2464 | downstream_candidate | plan-approved | inventory | no — downstream/reference only |
| plan_review_and_governance_backlog | #2346 | downstream_candidate | plan-approved | website_gtm | no — downstream/reference only |
| plan_review_and_governance_backlog | #2403 | downstream_candidate | plan-approved | llm_wiki | no — downstream/reference only |
| plan_review_and_governance_backlog | #2481 | reference | plan-review | calculation_code | no — downstream/reference only |

## Blocked / partial / missing evidence

| Package | Stage | Status | Evidence interpretation |
|---|---|---|---|
| inventory_readiness_spine | llm_wiki | PARTIAL | approved-plan evidence only; implemented artifact still required for READY (#2403, #2402, #2392) |
| inventory_readiness_spine | calculation_code | PARTIAL | approved-plan evidence only; implemented artifact still required for READY (#2481) |
| inventory_readiness_spine | parametric_outputs | MISSING | no usable evidence recorded for this stage |
| inventory_readiness_spine | website_gtm | PARTIAL | approved-plan evidence only; implemented artifact still required for READY (#2346) |
| raw_data_scouting_backlog | inventory | PARTIAL | approved-plan evidence only; implemented artifact still required for READY |
| raw_data_scouting_backlog | llm_wiki | MISSING | no usable evidence recorded for this stage |
| raw_data_scouting_backlog | calculation_code | MISSING | no usable evidence recorded for this stage |
| raw_data_scouting_backlog | parametric_outputs | MISSING | no usable evidence recorded for this stage |
| raw_data_scouting_backlog | website_gtm | MISSING | no usable evidence recorded for this stage |
| plan_review_and_governance_backlog | llm_wiki | PARTIAL | approved-plan evidence only; implemented artifact still required for READY (#2403) |
| plan_review_and_governance_backlog | calculation_code | PARTIAL | approved-plan evidence only; implemented artifact still required for READY (#2481) |
| plan_review_and_governance_backlog | parametric_outputs | MISSING | no usable evidence recorded for this stage |
| plan_review_and_governance_backlog | website_gtm | PARTIAL | approved-plan evidence only; implemented artifact still required for READY (#2346) |

## Evidence notes

- `READY` requires concrete implemented artifact evidence for the relevant stage.
- Approved plans and downstream issue references can justify `PARTIAL`, but not `READY`, without implemented artifacts.
- Downstream issues are candidates/dependencies only; #2487 does not execute them.
