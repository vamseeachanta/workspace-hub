# WRK-1114 Plan — Machine-Partitioned WRK ID Ranges

## Mission
Partition WRK ID space by machine so concurrent captures on different machines never collide.

## Route
Route A (Simple)

## Partition Table

| Machine | Floor | Ceiling | Notes |
|---------|-------|---------|-------|
| dev-primary | 1 | 4999 | Primary; current IDs ~1114 |
| licensed-win-1 | 5000 | 9999 | Windows / orcaflex |
| dev-secondary | 10000 | 14999 | Reserved |
| gali-linux-compute-1 | 15000 | 19999 | Reserved |

## Implementation Steps

1. Create `config/work-queue/machine-ranges.yaml` with the canonical partition table
2. Update `scripts/work-queue/next-id.sh`: after computing `MAX_ID`, read floor for `$HOSTNAME`
   via awk; if `MAX_ID < floor` → `NEXT_ID = floor`, else `NEXT_ID = MAX_ID + 1`
3. Add header comment to `next-id.sh` documenting convention + re-allocation policy
4. Add `machine_ranges_ref` comment to `.claude/work-queue/state.yaml`
5. Update work-queue `SKILL.md` §Workstation Routing with the ID range table
6. Write bash unit tests (5 scenarios): simulate each machine, assert non-overlapping output

## Test Strategy
- 5 bash unit tests in `tests/work-queue/test-machine-id-ranges.sh`
- Test scenarios: dev-primary empty queue, licensed-win-1 empty queue,
  dev-primary above floor, licensed-win-1 above floor, ceiling < floor assertion

## Acceptance Criteria
- `config/work-queue/machine-ranges.yaml` defines canonical partition table
- `next-id.sh` reads table and enforces floor for current machine
- `state.yaml` gains `machine_ranges_ref` comment
- SKILL.md §Workstation Routing documents ID ranges
- 5 tests: all PASS, 0 FAIL
- No existing WRK IDs renumbered
