# Elements staged-copy status report

- Issue: https://github.com/vamseeachanta/workspace-hub/issues/2526
- Generated: 2026-04-28
- Source mount during copy/verification: `/mnt/elements` mounted from `/dev/sdi1` as read-only (`fuseblk ro,...`).
- Scope: staged copy into `_from_elements/` directories only.
- Source deletion: none.
- Parent-folder dedupe/merge: not performed.
- `Codes & Regulations`: intentionally not copied; verify-only against `/mnt/ace/acma-codes/` unless missing content is proven.

## Verification result

Post-copy verifier output:

- `.planning/intel/elements-ingest/post-copy-verification-summary.tsv`
- `.planning/intel/elements-ingest/post-copy-verification-report.md`
- `.planning/intel/elements-ingest/post-copy-verification/*.tsv`

All staged buckets passed path+size comparison: 0 missing files, 0 size mismatches, 0 extra files.

| Bucket | Destination | Files | Bytes | Status |
|---|---|---:|---:|---:|
| `doris-62092-sesa` | `/mnt/ace/doris/62092_sesa/_from_elements` | 418 | 1,465,267,463 | PASS |
| `assethold-casa-grande-77017` | `/mnt/ace/assethold/casa-grande-77017/_from_elements` | 3 | 16,703,705 | PASS |
| `doris-codes-specs` | `/mnt/ace/doris/codes/_from_elements/codes-doris` | 35,197 | 26,411,658,490 | PASS |
| `doris-university` | `/mnt/ace/doris/training/_from_elements` | 564 | 11,060,962,662 | PASS |
| `digitalmodel-qgis` | `/mnt/ace/digitalmodel/tools/qgis/_from_elements` | 3 | 398,492,107 | PASS |
| `digitalmodel-riser-toolbox` | `/mnt/ace/digitalmodel/references/riser-toolbox/_from_elements` | 8 | 510,241,677 | PASS |
| `digitalmodel-suction-pile-sizing` | `/mnt/ace/digitalmodel/references/suction-pile-sizing/_from_elements` | 4 | 235,464 | PASS |
| `acma-projects-31522-woodfibre` | `/mnt/ace/acma-projects/31522-woodfibre-lng/_from_elements` | 5,364 | 1,879,405,139,855 | PASS |

## Rsync log check

All eight `rsync-copy-*.log` files include final `total size is ... speedup is 1.00` lines and no obvious rsync error lines (`rsync error`, failed, I/O error, permission denied, no space left, ERROR).

## MOVE-LOG coverage

MOVE-LOG files exist for each staged destination parent:

- `/mnt/ace/doris/62092_sesa/MOVE-LOG.md`
- `/mnt/ace/assethold/casa-grande-77017/MOVE-LOG.md`
- `/mnt/ace/doris/codes/_from_elements/MOVE-LOG.md`
- `/mnt/ace/doris/training/MOVE-LOG.md`
- `/mnt/ace/digitalmodel/tools/qgis/MOVE-LOG.md`
- `/mnt/ace/digitalmodel/references/riser-toolbox/MOVE-LOG.md`
- `/mnt/ace/digitalmodel/references/suction-pile-sizing/MOVE-LOG.md`
- `/mnt/ace/acma-projects/31522-woodfibre-lng/MOVE-LOG.md`

## Next step

Proceed to a separate dedupe-merge planning phase. Do not merge staged `_from_elements/` content into parent folders until each bucket has overlap/duplicate assessment, dry-run commands, and explicit approval for the merge action.
