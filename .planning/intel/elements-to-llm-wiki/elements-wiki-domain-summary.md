# Elements → LLM Wiki Metadata Index Summary

Generated: `2026-04-28 19:23 UTC`

## Policy

- Raw bulk files remain in `/mnt/ace` parent targets.
- Retained `_from_elements/` staging paths are provenance/retention artifacts only.
- Wiki pages are metadata-first source/catalog pages; deep extraction is deferred to #2536.
- Cleanup/deletion remains governed by #2534.

## Totals

- Buckets: 8
- Files represented: 41,561
- Bytes represented: 1,919,268,701,423

## Bucket summary

| Order | Bucket | Wiki | Parent target | Files | Bytes | Priority | Verification |
|---:|---|---|---|---:|---:|---|---|
| 1 | `digitalmodel-suction-pile-sizing` | `marine-engineering` | `/mnt/ace/digitalmodel/references/suction-pile-sizing` | 4 | 235,464 | high | missing=0, size_mismatch=0, not_hardlinked=0 |
| 2 | `assethold-casa-grande-77017` | `asset-management` | `/mnt/ace/assethold/casa-grande-77017` | 3 | 16,703,705 | low | missing=0, size_mismatch=0, not_hardlinked=0 |
| 3 | `digitalmodel-qgis` | `engineering` | `/mnt/ace/digitalmodel/tools/qgis` | 3 | 398,492,107 | high | missing=0, size_mismatch=0, not_hardlinked=0 |
| 4 | `digitalmodel-riser-toolbox` | `marine-engineering` | `/mnt/ace/digitalmodel/references/riser-toolbox` | 8 | 510,241,677 | high | missing=0, size_mismatch=0, not_hardlinked=0 |
| 5 | `doris-62092-sesa` | `lng-projects` | `/mnt/ace/doris/62092_sesa` | 418 | 1,465,267,463 | medium | missing=0, size_mismatch=0, not_hardlinked=0 |
| 6 | `doris-university` | `engineering` | `/mnt/ace/doris/training` | 564 | 11,060,962,662 | medium | missing=0, size_mismatch=0, not_hardlinked=0 |
| 7 | `doris-codes-specs` | `engineering-standards` | `/mnt/ace/doris/codes` | 35,197 | 26,411,658,490 | metadata-only | missing=0, size_mismatch=0, not_hardlinked=0 |
| 8 | `acma-projects-31522-woodfibre` | `lng-projects` | `/mnt/ace/acma-projects/31522-woodfibre-lng` | 5,364 | 1,879,405,139,855 | metadata-only | missing=0, size_mismatch=0, not_hardlinked=0 |

## Per-wiki batch files

| Wiki | Batch file | Records |
|---|---|---:|
| `asset-management` | `.planning/intel/elements-to-llm-wiki/batches/asset-management.jsonl` | 1 |
| `engineering` | `.planning/intel/elements-to-llm-wiki/batches/engineering.jsonl` | 2 |
| `engineering-standards` | `.planning/intel/elements-to-llm-wiki/batches/engineering-standards.jsonl` | 1 |
| `lng-projects` | `.planning/intel/elements-to-llm-wiki/batches/lng-projects.jsonl` | 2 |
| `marine-engineering` | `.planning/intel/elements-to-llm-wiki/batches/marine-engineering.jsonl` | 2 |

## Deep extraction queue

Extractable high/medium-priority candidates written to `.planning/intel/elements-to-llm-wiki/deep-extraction-candidates.tsv`: 671 records.

Recommended first pass: suction pile sizing, riser toolbox, QGIS, then SESA/Woodfibre selected LNG project files.
