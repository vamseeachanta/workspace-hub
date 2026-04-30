# Legal/privacy and semantic-count validation — issue #2554 public matrix

Date: 2026-04-30
Scope:
- `docs/plans/2026-04-29-issue-2554-vessel-contractor-outreach-matrix.md`
- `docs/reports/gtm/2026-04-29-vessel-contractor-outreach-matrix-scaffold.md`
- `docs/plans/overnight-prompts/2026-04-29-weekly-gtm-targets/results/issue-2554-summary.md`

## Why this exists

The r1 post-fill review found that `scripts/legal/legal-sanity-scan.sh --diff-only` can false-pass once the matrix files are already committed. This artifact records a targeted committed-file scan and a semantic target count, so #2554 promotion does not depend on an empty diff.

## Results

- Legal deny-list fixed-string hits: 0
- Contact-pattern hits (email, phone-like, individual LinkedIn URL): 0
- Semantic live/countable vessel/operator target count: 20
- High-priority row count: 12

## Legal deny-list hits

- none

## Contact-pattern hits

- none

## Semantic target inventory (visual rows are contiguous; original target heading preserved)

| Row | Target heading | Title | Priority | Count status |
|---:|---:|---|---|---|
| 1 | 1 | Subsea7 | High | counted |
| 2 | 2 | TechnipFMC (Subsea) | High | counted |
| 3 | 3 | Saipem | High | counted |
| 4 | 4 | McDermott International | High | counted |
| 5 | 5 | Allseas | High | counted |
| 6 | 6 | Heerema Marine Contractors | High | counted |
| 7 | 7 | Boskalis (Subsea Services) | High | counted |
| 8 | 8 | Van Oord | Medium | counted |
| 9 | 9 | DEME Offshore | Medium | counted |
| 10 | 10 | DOF Group (DOF Subsea + Solstad merger) | High | counted |
| 11 | 11 | Bourbon Offshore | Medium | counted |
| 12 | 12 | Sapura Energy | High | counted |
| 13 | 13 | Seaway7 (Subsea7 Renewables) | Medium | counted |
| 14 | 14 | Cadeler | Defer | defer |
| 15 | 15 | Helix Energy Solutions | High | counted |
| 16 | 16 | DeepOcean Group | Medium | counted |
| 17 | 17 | Jan De Nul | Medium | counted |
| 18 | 18 | Eidesvik Offshore | Low | counted |
| 19 | 19 | Acteon Group | Medium | explicit non-counted partner-shape |
| 20 | 20 | Otto Candies LLC | Low | counted |
| 21 | 23 | Hornbeck Offshore Services | High | counted |
| 22 | 24 | Edison Chouest Offshore | High | counted |
| 23 | 21 | Solstad Offshore (legacy, now DOF) | Defer | legacy/deprecated, defer |
| 24 | 22 | EMAS / Ezra Holdings (legacy) | Defer | legacy/deprecated, defer |

## Promotion note

This scan does not authorize outreach or send. It only supports the #2554 plan-review promotion gate by proving that the public matrix artifacts contain no deny-list/contact-pattern hits and that the scaffold has at least 20 live/countable vessel/operator rows after excluding legacy/deprecated, `Defer`, and explicitly non-counted partner-shape rows.
