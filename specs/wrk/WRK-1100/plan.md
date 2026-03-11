# WRK-1100 Plan

## Route A — Simple

1. Add `standing+cadence` guard in `whats-next.sh process_file()` after working/blocked early-returns
2. Scope to `loc == "pending"` only — working/ and blocked/ items always display
3. Logic: if `standing == true && cadence != ""` → return (skip from priority buckets)
4. Verify: WRK-235 excluded, WRK-234 retained, no other items affected
