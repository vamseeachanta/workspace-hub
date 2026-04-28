# Elements dedupe-merge assessment report

Non-mutating scan only. No files were copied, moved, merged, overwritten, or deleted.


## Target table

| Order | Bucket | Source folder | Parent target | Staging location | Notes |
|---:|---|---|---|---|---|
| 1 | `digitalmodel-suction-pile-sizing` | `Suction Pile Sizing` | `/mnt/ace/digitalmodel/references/suction-pile-sizing` | `/mnt/ace/digitalmodel/references/suction-pile-sizing/_from_elements` | smallest / lowest-risk first |
| 2 | `assethold-casa-grande-77017` | `casa_grande_77017` | `/mnt/ace/assethold/casa-grande-77017` | `/mnt/ace/assethold/casa-grande-77017/_from_elements` | small real-estate/asset bucket |
| 3 | `digitalmodel-qgis` | `qgis` | `/mnt/ace/digitalmodel/tools/qgis` | `/mnt/ace/digitalmodel/tools/qgis/_from_elements` | reusable workflow/data |
| 4 | `digitalmodel-riser-toolbox` | `Riser Toolbox` | `/mnt/ace/digitalmodel/references/riser-toolbox` | `/mnt/ace/digitalmodel/references/riser-toolbox/_from_elements` | engineering reference |
| 5 | `doris-62092-sesa` | `62092  SESA FLNG Terminal Project` | `/mnt/ace/doris/62092_sesa` | `/mnt/ace/doris/62092_sesa/_from_elements` | likely overlap; review carefully |
| 6 | `doris-university` | `Doris University` | `/mnt/ace/doris/training` | `/mnt/ace/doris/training/_from_elements` | training material |
| 7 | `doris-codes-specs` | `Codes and Specs` | `/mnt/ace/doris/codes` | `/mnt/ace/doris/codes/_from_elements/codes-doris` | high file-count overlap risk |
| 8 | `acma-projects-31522-woodfibre` | `Woodfibre` | `/mnt/ace/acma-projects/31522-woodfibre-lng` | `/mnt/ace/acma-projects/31522-woodfibre-lng/_from_elements` | very large; treat as separate reviewed merge |

## Assessment summary

| Order | Bucket | Parent files excl. staging | Stage files | Same path + same size | Same path + different size | Stage-only files | Parent-only files | Recommended next action |
|---:|---|---:|---:|---:|---:|---:|---:|---|
| 1 | `digitalmodel-suction-pile-sizing` | 1 | 4 | 0 | 0 | 4 | 1 | Dry-run rsync --ignore-existing; all staged files appear new by relative path. |
| 2 | `assethold-casa-grande-77017` | 1 | 3 | 0 | 0 | 3 | 1 | Dry-run rsync --ignore-existing; all staged files appear new by relative path. |
| 3 | `digitalmodel-qgis` | 1 | 3 | 0 | 0 | 3 | 1 | Dry-run rsync --ignore-existing; all staged files appear new by relative path. |
| 4 | `digitalmodel-riser-toolbox` | 1 | 8 | 0 | 0 | 8 | 1 | Dry-run rsync --ignore-existing; all staged files appear new by relative path. |
| 5 | `doris-62092-sesa` | 53 | 418 | 0 | 0 | 418 | 53 | Dry-run rsync --ignore-existing; all staged files appear new by relative path. |
| 6 | `doris-university` | 1 | 564 | 0 | 0 | 564 | 1 | Dry-run rsync --ignore-existing; all staged files appear new by relative path. |
| 7 | `doris-codes-specs` | 5 | 35,197 | 0 | 0 | 35,197 | 5 | Dry-run rsync --ignore-existing; all staged files appear new by relative path. |
| 8 | `acma-projects-31522-woodfibre` | 1 | 5,364 | 0 | 0 | 5,364 | 1 | Dry-run rsync --ignore-existing; all staged files appear new by relative path. |

## Dry-run merge simulation summary

Command pattern used for each bucket:

```bash
rsync -aHAXn --ignore-existing --itemize-changes --stats "$STAGE/" "$PARENT/"
```

This is a dry run only (`-n`). It did not copy, move, overwrite, or delete files.

| Order | Bucket | Regular files that would be created | Bytes that would transfer | Dry-run log |
|---:|---|---:|---:|---|
| 1 | `digitalmodel-suction-pile-sizing` | 4 | 235,464 | `dedupe-merge-assessment/01-digitalmodel-suction-pile-sizing.rsync-ignore-existing-dry-run.log` |
| 2 | `assethold-casa-grande-77017` | 3 | 16,703,705 | `dedupe-merge-assessment/02-assethold-casa-grande-77017.rsync-ignore-existing-dry-run.log` |
| 3 | `digitalmodel-qgis` | 3 | 398,492,107 | `dedupe-merge-assessment/03-digitalmodel-qgis.rsync-ignore-existing-dry-run.log` |
| 4 | `digitalmodel-riser-toolbox` | 8 | 510,241,677 | `dedupe-merge-assessment/04-digitalmodel-riser-toolbox.rsync-ignore-existing-dry-run.log` |
| 5 | `doris-62092-sesa` | 418 | 1,465,267,463 | `dedupe-merge-assessment/05-doris-62092-sesa.rsync-ignore-existing-dry-run.log` |
| 6 | `doris-university` | 564 | 11,060,962,662 | `dedupe-merge-assessment/06-doris-university.rsync-ignore-existing-dry-run.log` |
| 7 | `doris-codes-specs` | 35,197 | 26,411,658,490 | `dedupe-merge-assessment/07-doris-codes-specs.rsync-ignore-existing-dry-run.log` |
| 8 | `acma-projects-31522-woodfibre` | 5,364 | 1,879,405,139,855 | `dedupe-merge-assessment/08-acma-projects-31522-woodfibre.rsync-ignore-existing-dry-run.log` |

## Detail files

- Assessment summary TSV: `/mnt/local-analysis/workspace-hub/.planning/intel/elements-ingest/dedupe-merge-assessment-summary.tsv`
- Rsync dry-run summary TSV: `/mnt/local-analysis/workspace-hub/.planning/intel/elements-ingest/dedupe-merge-rsync-dry-run-summary.tsv`
- Detail directory: `/mnt/local-analysis/workspace-hub/.planning/intel/elements-ingest/dedupe-merge-assessment`
- Per bucket files: `*.stage-only.tsv`, `*.same-path-same-size.tsv`, `*.same-path-different-size.tsv`, `*.parent-only.tsv`, `*.rsync-ignore-existing-dry-run.log`

## Guardrail

This report is an assessment artifact only. Do not merge any bucket until the bucket's conflict table is reviewed and an explicit merge command is approved.
