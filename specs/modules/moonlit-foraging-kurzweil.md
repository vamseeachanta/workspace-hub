# WRK-1151 Plan — Naval Architecture Resource Collection

## Context

Build an offline naval architecture reference library to support digitalmodel engineering work. 7 seed URLs provided. Downloads and catalogue already completed in prior stages — remaining work is verification, gap-fill web search, and document-index regeneration.

## Current State (Already Done)

- **138 PDFs downloaded** to `/mnt/ace/docs/_standards/SNAME/` (textbooks/, hydrostatics-stability/, ship-plans/)
- **Download script** exists: `scripts/data/naval-architecture/download-naval-arch-docs.sh` (uses `scripts/lib/download-helpers.sh`)
- **Catalogue** written: `knowledge/seeds/naval-architecture-resources.yaml` (6 textbooks, 3 hydrostatics, 107 ship plans, 5 online portals, 3 pending-manual)
- **Download log**: `.claude/work-queue/assets/WRK-1151/download.log`

## Remaining Steps

### Step 1: Verify AC Coverage
- Confirm all 7 seed URLs were fetched and linked PDFs extracted (AC1)
- Cross-check catalogue entries against actual files on disk

### Step 2: Web Search for Additional Resources (AC2)
- Search for additional freely-available naval architecture PDFs (MIT OCW, IMO, RINA, ClassNK)
- Add any new finds to download script and catalogue
- Run download script for new entries only (skip-if-exists logic built in)

### Step 3: Regenerate Document Index (AC5)
- Run: `uv run --no-project python scripts/data/document-index/phase-a-index.py --source ace_standards`
- Verify SNAME PDFs appear in `data/document-index/index.jsonl`
- Test query: `bash scripts/readiness/query-docs.sh --source ace_standards --keyword "SNAME"`

### Step 4: Final AC Verification
- [ ] AC1: All 7 seed URLs fetched ✓ (verify)
- [ ] AC2: Web search performed (execute)
- [ ] AC3: PDFs saved to /mnt/ace/docs/_standards/SNAME/ ✓ (verify count)
- [ ] AC4: Catalogue YAML at knowledge/seeds/naval-architecture-resources.yaml ✓ (verify)
- [ ] AC5: Document index regenerated (execute)
- [ ] AC6: No paywalled/DRM content (verify pending_manual section documents blocked items)

## Key Files

| File | Role |
|------|------|
| `scripts/data/naval-architecture/download-naval-arch-docs.sh` | Download orchestrator |
| `scripts/lib/download-helpers.sh` | Shared wget wrapper |
| `knowledge/seeds/naval-architecture-resources.yaml` | Resource catalogue |
| `scripts/data/document-index/phase-a-index.py` | Index scanner |
| `scripts/data/document-index/config.yaml` | Index config (ace_standards source) |

## Verification

1. `ls /mnt/ace/docs/_standards/SNAME/**/*.pdf | wc -l` — should be ≥138
2. `bash scripts/readiness/query-docs.sh --source ace_standards --keyword "naval"` — returns results
3. All catalogue entries have local_path that resolves to an existing file
