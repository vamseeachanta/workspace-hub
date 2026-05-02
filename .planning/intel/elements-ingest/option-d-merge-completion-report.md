# Elements Option D merge completion report

Approved scope: Option D — all 8 staged buckets.

Execution method: hardlink-preserving rsync from `_from_elements/` staging into parent targets using `--ignore-existing --link-dest=<stage>`.

No `/mnt/elements` source data or `_from_elements/` staging folders were deleted.


## Result table

| Order | Bucket | Parent target | Staging retained | Files verified | Bytes | Missing | Size mismatches | Not hardlinked | Status |
|---:|---|---|---|---:|---:|---:|---:|---:|---|
| 1 | `digitalmodel-suction-pile-sizing` | `/mnt/ace/digitalmodel/references/suction-pile-sizing` | `/mnt/ace/digitalmodel/references/suction-pile-sizing/_from_elements` | 4 | 235,464 | 0 | 0 | 0 | PASS |
| 2 | `assethold-casa-grande-77017` | `/mnt/ace/assethold/casa-grande-77017` | `/mnt/ace/assethold/casa-grande-77017/_from_elements` | 3 | 16,703,705 | 0 | 0 | 0 | PASS |
| 3 | `digitalmodel-qgis` | `/mnt/ace/digitalmodel/tools/qgis` | `/mnt/ace/digitalmodel/tools/qgis/_from_elements` | 3 | 398,492,107 | 0 | 0 | 0 | PASS |
| 4 | `digitalmodel-riser-toolbox` | `/mnt/ace/digitalmodel/references/riser-toolbox` | `/mnt/ace/digitalmodel/references/riser-toolbox/_from_elements` | 8 | 510,241,677 | 0 | 0 | 0 | PASS |
| 5 | `doris-62092-sesa` | `/mnt/ace/doris/62092_sesa` | `/mnt/ace/doris/62092_sesa/_from_elements` | 418 | 1,465,267,463 | 0 | 0 | 0 | PASS |
| 6 | `doris-university` | `/mnt/ace/doris/training` | `/mnt/ace/doris/training/_from_elements` | 564 | 11,060,962,662 | 0 | 0 | 0 | PASS |
| 7 | `doris-codes-specs` | `/mnt/ace/doris/codes` | `/mnt/ace/doris/codes/_from_elements/codes-doris` | 35,197 | 26,411,658,490 | 0 | 0 | 0 | PASS |
| 8 | `acma-projects-31522-woodfibre` | `/mnt/ace/acma-projects/31522-woodfibre-lng` | `/mnt/ace/acma-projects/31522-woodfibre-lng/_from_elements` | 5,364 | 1,879,405,139,855 | 0 | 0 | 0 | PASS |

## Verification artifacts

- `/mnt/local-analysis/workspace-hub/.planning/intel/elements-ingest/option-d-preflight-filesystem.txt`
- `/mnt/local-analysis/workspace-hub/.planning/intel/elements-ingest/option-d-merge-summary.tsv`
- `/mnt/local-analysis/workspace-hub/.planning/intel/elements-ingest/option-d-merge-verification-summary.tsv`
- `/mnt/local-analysis/workspace-hub/.planning/intel/elements-ingest/option-d-merge-verification-report.md`
- `/mnt/local-analysis/workspace-hub/.planning/intel/elements-ingest/option-d-post-merge-mount-disk-state.txt`
- `/mnt/local-analysis/workspace-hub/.planning/intel/elements-ingest/option-d-move-log-update-paths.txt`

## Retention / cleanup guardrail

- Keep `/mnt/elements` source for the agreed minimum retention period.
- Keep `_from_elements/` staging folders until an explicit source/staging cleanup issue or command is approved.
- `Codes & Regulations` remains skipped/verify-only against `/mnt/ace/acma-codes/`.
