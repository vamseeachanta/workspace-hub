# Retention cleanup readiness check — workspace-hub#2534

Run time: `2026-04-28T14:02:20-05:00`

Retention not-before date: `2026-05-28`

Retention elapsed: **False**

Elements mount state: `/mnt/elements /dev/sdi1 fuseblk ro,relatime,user_id=0,group_id=0,default_permissions,allow_other,blksize=4096`


No files were deleted, moved, unmounted, or modified by this check.


## Cleanup candidate / verification table

| Order | Bucket | Parent target | Retained staging | Files | Bytes | Missing | Size mismatches | Not hardlinked | Status |
|---:|---|---|---|---:|---:|---:|---:|---:|---|
| 1 | `digitalmodel-suction-pile-sizing` | `/mnt/ace/digitalmodel/references/suction-pile-sizing` | `/mnt/ace/digitalmodel/references/suction-pile-sizing/_from_elements` | 4 | 235,464 | 0 | 0 | 0 | READY_AFTER_RETENTION |
| 2 | `assethold-casa-grande-77017` | `/mnt/ace/assethold/casa-grande-77017` | `/mnt/ace/assethold/casa-grande-77017/_from_elements` | 3 | 16,703,705 | 0 | 0 | 0 | READY_AFTER_RETENTION |
| 3 | `digitalmodel-qgis` | `/mnt/ace/digitalmodel/tools/qgis` | `/mnt/ace/digitalmodel/tools/qgis/_from_elements` | 3 | 398,492,107 | 0 | 0 | 0 | READY_AFTER_RETENTION |
| 4 | `digitalmodel-riser-toolbox` | `/mnt/ace/digitalmodel/references/riser-toolbox` | `/mnt/ace/digitalmodel/references/riser-toolbox/_from_elements` | 8 | 510,241,677 | 0 | 0 | 0 | READY_AFTER_RETENTION |
| 5 | `doris-62092-sesa` | `/mnt/ace/doris/62092_sesa` | `/mnt/ace/doris/62092_sesa/_from_elements` | 418 | 1,465,267,463 | 0 | 0 | 0 | READY_AFTER_RETENTION |
| 6 | `doris-university` | `/mnt/ace/doris/training` | `/mnt/ace/doris/training/_from_elements` | 564 | 11,060,962,662 | 0 | 0 | 0 | READY_AFTER_RETENTION |
| 7 | `doris-codes-specs` | `/mnt/ace/doris/codes` | `/mnt/ace/doris/codes/_from_elements/codes-doris` | 35,197 | 26,411,658,490 | 0 | 0 | 0 | READY_AFTER_RETENTION |
| 8 | `acma-projects-31522-woodfibre` | `/mnt/ace/acma-projects/31522-woodfibre-lng` | `/mnt/ace/acma-projects/31522-woodfibre-lng/_from_elements` | 5,364 | 1,879,405,139,855 | 0 | 0 | 0 | READY_AFTER_RETENTION |

## Decision

Verification passes, but retention window has **not** elapsed. Cleanup deletion/release remains blocked until 2026-05-28 unless the user explicitly overrides the retention policy.

## Artifacts

- Summary TSV: `/mnt/local-analysis/workspace-hub/.planning/intel/elements-ingest/retention-cleanup-readiness-2534.tsv`
- Failure TSV: `/mnt/local-analysis/workspace-hub/.planning/intel/elements-ingest/retention-cleanup-readiness-2534-failures.tsv`
