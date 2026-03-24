---
wrk_id: WRK-5138
reviewed: true
approved: true
route: A
---

# Plan: Fix cross-review.sh Codex dispatch crash

## Problem
`count_wrk_codex_reviews()` uses `ls` glob which exits non-zero when no files match, crashing the script under `set -euo pipefail`.

## Fix
Replace `ls` with `find ... || true` to safely return 0 on no match.

## Scope
Single function in `scripts/review/cross-review.sh` line 206.

confirmed_by: vamsee
confirmed_at: 2026-03-24
decision: passed
