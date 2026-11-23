# WRK-1072 Plan: Fast-Forward to Close

## Context

WRK-1072 (release management — SemVer + CHANGELOG) was **already implemented** in commit `94ad72bb`. All 5 ACs are met. The WRK lifecycle stalled at Stage 4. User chose fast-forward to close.

## Plan

1. **TDD verification** — run existing scripts in dry-run mode to confirm they work
2. **Write gate evidence** — `gate-evidence-summary.{md,json}` documenting all ACs pass
3. **Close + archive** — `close-item.sh` + `archive-item.sh`

### Key files (already exist)
- `scripts/release/cut-release.sh` (113 lines)
- `scripts/release/generate-changelog.sh` (92 lines)
- `config/releases/release-manifest.yaml`

### Verification
```bash
bash scripts/release/cut-release.sh assetutilities 0.1.1 --dry-run
```

### Future work: digitalmodel version mismatch (CHANGELOG says v2.0.0, pyproject.toml says 0.1.0)
