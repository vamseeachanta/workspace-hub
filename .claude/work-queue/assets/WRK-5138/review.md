# WRK-5138 Review

## Fix Summary
Replaced `ls` glob with `find ... || true` in `count_wrk_codex_reviews()` to prevent crash under `set -euo pipefail` when no prior Codex reviews exist.

## Verification
- Syntax check: PASS (`bash -n`)
- No-match case: returns 0, no crash
- Has-match case: correctly counts reviews, excludes opus-fallback
- Single copy across ecosystem

## Result: PASS
