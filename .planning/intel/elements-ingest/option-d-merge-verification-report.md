# Option D merge verification report

Every staged file was checked for a corresponding parent file with same relative path, same size, and same device+inode hardlink identity.


| Order | Bucket | Stage files | Missing in parent | Size mismatches | Not hardlinked | Status |
|---:|---|---:|---:|---:|---:|---|
| 1 | `digitalmodel-suction-pile-sizing` | 4 | 0 | 0 | 0 | PASS |
| 2 | `assethold-casa-grande-77017` | 3 | 0 | 0 | 0 | PASS |
| 3 | `digitalmodel-qgis` | 3 | 0 | 0 | 0 | PASS |
| 4 | `digitalmodel-riser-toolbox` | 8 | 0 | 0 | 0 | PASS |
| 5 | `doris-62092-sesa` | 418 | 0 | 0 | 0 | PASS |
| 6 | `doris-university` | 564 | 0 | 0 | 0 | PASS |
| 7 | `doris-codes-specs` | 35,197 | 0 | 0 | 0 | PASS |
| 8 | `acma-projects-31522-woodfibre` | 5,364 | 0 | 0 | 0 | PASS |

## Artifacts

- Summary TSV: `/mnt/local-analysis/workspace-hub/.planning/intel/elements-ingest/option-d-merge-verification-summary.tsv`
- Failure detail TSVs: `/mnt/local-analysis/workspace-hub/.planning/intel/elements-ingest/dedupe-merge-assessment`

## Retention guardrail

No `_from_elements/` staging folders or `/mnt/elements` source data were deleted by this verification.
