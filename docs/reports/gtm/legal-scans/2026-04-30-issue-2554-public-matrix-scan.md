# Legal/privacy and semantic-count validation — issue #2554 public matrix

Status: **PASS**
Date: 2026-04-30
Generator: `uv run python scripts/validation/validate_gtm_2554_matrix.py --write-artifact`
Scope:
- `docs/plans/2026-04-29-issue-2554-vessel-contractor-outreach-matrix.md`
- `docs/reports/gtm/2026-04-29-vessel-contractor-outreach-matrix-scaffold.md`
- `docs/plans/overnight-prompts/2026-04-29-weekly-gtm-targets/results/issue-2554-summary.md`

## Why this exists

The r1 post-fill review found that `scripts/legal/legal-sanity-scan.sh --diff-only` can false-pass once the matrix files are already committed. This artifact is generated from the scaffold and targeted committed files so #2554 promotion does not depend on an empty diff or hand-counted rows.

## Results

- Legal deny-list fixed-string hits: 0
- Contact-pattern hits (email, phone-like, individual LinkedIn URL, simple named-person-with-title pattern): 0
- Semantic live/countable vessel/operator target count: 20
- High-priority row count: 12

## Validation errors

- none

## Legal deny-list hits

- none

## Contact-pattern hits

- none

## Semantic target inventory (visual rows are contiguous; original target heading preserved)

| Row | Target heading | Title | Priority | Count status | Missing required fields |
|---:|---:|---|---|---|---|
| 1 | 1 | Subsea7 | High | counted | none |
| 2 | 2 | TechnipFMC (Subsea) | High | counted | none |
| 3 | 3 | Saipem | High | counted | none |
| 4 | 4 | McDermott International | High | counted | none |
| 5 | 5 | Allseas | High | counted | none |
| 6 | 6 | Heerema Marine Contractors | High | counted | none |
| 7 | 7 | Boskalis (Subsea Services) | High | counted | none |
| 8 | 8 | Van Oord | Medium | counted | none |
| 9 | 9 | DEME Offshore | Medium | counted | none |
| 10 | 10 | DOF Group (DOF Subsea + Solstad merger) | High | counted | none |
| 11 | 11 | Bourbon Offshore | Medium | counted | none |
| 12 | 12 | Sapura Energy | High | counted | none |
| 13 | 13 | Seaway7 (Subsea7 Renewables) | Medium | counted | none |
| 14 | 14 | Cadeler | Defer | defer | none |
| 15 | 15 | Helix Energy Solutions | High | counted | none |
| 16 | 16 | DeepOcean Group | Medium | counted | none |
| 17 | 17 | Jan De Nul | Medium | counted | none |
| 18 | 18 | Eidesvik Offshore | Low | counted | none |
| 19 | 19 | Acteon Group | Medium | explicit non-counted partner-shape | none |
| 20 | 20 | Otto Candies LLC | Low | counted | none |
| 21 | 23 | Hornbeck Offshore Services | High | counted | none |
| 22 | 24 | Edison Chouest Offshore | High | counted | none |
| 23 | 21 | Solstad Offshore (legacy, now DOF) | Defer | legacy/deprecated, defer | none |
| 24 | 22 | EMAS / Ezra Holdings (legacy) | Defer | legacy/deprecated, defer | none |

## Promotion note

This scan does not authorize outreach or send. It supports the #2554 plan-review promotion gate by parsing the scaffold, deriving live/countable and High-priority counts, checking required row fields, rejecting disallowed evidence URL hosts, comparing count claims across artifacts, and screening direct contact leakage patterns. Manual public/private boundary review remains required for semantic named-person leakage that no regex can prove exhaustively.
