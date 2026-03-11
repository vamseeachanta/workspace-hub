# WRK-1125 Plan

Route A inline plan.

## Changes to scripts/work-queue/whats-next.sh

1. `declare -A WRK_NOTES WRK_NOT_BEFORE` — associative maps for note/not_before fields
2. `WORKING_PARKED` array for working items with non-empty note
3. `process_file()`: read note/not_before into maps; route working items with note to PARKED
4. `print_section()`: print dim annotation lines after each local row
5. Render PARKED section after WORKING; update summary line with parked count

## Acceptance Criteria
- AC1: note annotation in WORKING/PARKED sections
- AC2: not_before annotation in all sections
- AC3: working items with note in PARKED sub-section
- AC4: smoke-test PASS
