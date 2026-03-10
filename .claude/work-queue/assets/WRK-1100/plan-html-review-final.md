# WRK-1100 Plan — Final Review

## Plan (Route A)

1. Add `standing+cadence` guard in `whats-next.sh process_file()` — scope to `pending` only
2. Guard fires after `working`/`blocked` early-returns to avoid hiding active items
3. Logic: `[[ "$_standing" == "true" && -n "$_cadence" ]] && return`
4. Audit: WRK-235 excluded ✓, WRK-234 retained ✓, all others unaffected ✓

## Confirmation

User confirmed final plan: approved by vamsee 2026-03-10.
