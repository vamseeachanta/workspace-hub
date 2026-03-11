# WRK-1125 AC Test Matrix

| AC | Description | Test | Result |
|----|-------------|------|--------|
| AC1 | WORKING section shows note: as dim annotation | WRK-1125 in WORKING — annotation code present; any working item with note shows annotation | PASS |
| AC2 | UNCLAIMED shows not_before: date when present | WRK-1109 (UNCLAIMED) shows "↳ not before: 2026-04-10" | PASS |
| AC3 | Working items with note go to ⏸ PARKED sub-section | WRK-1022 moved from WORKING to PARKED with note annotation | PASS |
| AC4 | smoke-test: whats-next.sh runs, WRK-1022 note shown, WRK-1109 not_before shown | bash scripts/work-queue/whats-next.sh → PARKED shows WRK-1022 note; UNCLAIMED shows WRK-1109 note+not_before | PASS |

## Additional observations
- WRK-1125 itself shows in WORKING (no note) — confirms pending items with note unaffected ✓
- Annotation code runs for all sections (WORKING, PARKED, UNCLAIMED, HIGH, MEDIUM) for local rows
- Remote-collapsed rows do not show annotations (known limitation, as per Codex scope boundary)
