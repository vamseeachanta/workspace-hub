# WRK-5048: Uniform Box-Drawing Table Format for whats-next.sh

## Context

`scripts/work-queue/whats-next.sh` (377 lines) renders 8 section types using hand-crafted `printf %-Ns` alignment. Column widths vary by section, titles get truncated inconsistently, and the output is hard to scan. The user wants uniform box-drawing tables with emoji status icons across all sections.

## Approach

Replace the rendering layer (lines 236–377) with a reusable `draw_table()` function and per-section wrappers. Data-gathering logic (lines 1–235) stays unchanged.

### Column Design — Adaptive Layout

**Default (single machine):** 3 columns — Icon, WRK, Priority, Title
**Mixed machines:** 4 columns — adds MACHINE column
**WORKING/PARKED/UNCLAIMED:** separate STAGE and PID columns always shown

Per-section column specs:

| Section | Columns |
|---------|---------|
| WORKING / PARKED / UNCLAIMED | Icon │ WRK │ Priority │ Stage │ PID │ Title |
| COORDINATING | Icon │ WRK │ Priority │ Title │ Child Progress |
| HIGH / UNBLOCKED / MEDIUM | Icon │ WRK │ Priority │ [Machine*] │ Title |
| BLOCKED | Icon │ WRK │ Subcategory │ Blocked By |

*Machine column appears only when rows span multiple machines.

### Column Widths (target 120 chars)

| Col | Width |
|-----|-------|
| Icon | 4 |
| WRK | 10 |
| Priority | 10 |
| Stage | 9 |
| PID | 11 |
| Machine | 15 |
| Subcategory | 26 |
| Title | remainder (flexible) |

### Emoji Map

| Section | Emoji |
|---------|-------|
| COORDINATING | ◈ |
| WORKING | 🔄 |
| PARKED | ⏸ |
| UNCLAIMED | ⚠ |
| HIGH PRIORITY | ★ |
| NEWLY UNBLOCKED | ↑ |
| MEDIUM | · |
| BLOCKED | ✗ |

### Box-Drawing Table Function

New function `draw_table()` inside whats-next.sh:
- Input: section_label, colour, emoji, column_widths array, header_labels array, rows array, notes associative array
- Renders: `┌─┬─┐` top, `│` cells, `├─┼─┤` after header, `└─┴─┘` bottom
- Section header: coloured full-width row above the column headers
- Note annotations (`↳ ...`): full-width merged row below parent, dimmed
- Remote machine collapse: `│  [other machines: WRK-601 WRK-602]  │` as merged row
- `[this machine: hostname]` sub-header as merged row when mixed machines

### Summary + Parallel Hints

Keep current format (not tabularized) — compact single-line outputs.

## Files to Modify

| File | Change |
|------|--------|
| `scripts/work-queue/whats-next.sh` | Replace lines 236–377 rendering layer |
| `tests/work-queue/test_whats_next.bats` | Add 3+ tests for box-drawing output |

## Implementation Steps

1. **TDD**: Write 3 new BATS tests — assert box-drawing chars (┌│└) in output, emoji presence, and adaptive machine column
2. **Add `draw_table()` function** (~50 lines) after line 235
3. **Add `render_section()` wrapper** that builds column specs per section type and calls `draw_table()`
4. **Replace `print_section()`** with `render_section()` calls
5. **Replace inline COORDINATING renderer** (lines 313–322) with `render_section()`
6. **Replace inline BLOCKED renderer** (lines 339–349) with `render_section()`
7. **Run all BATS tests** — existing 9 + new 3 must pass
8. **Visual check** with `--all`, `--category`, `--subcategory` flags

## Verification

```bash
bats tests/work-queue/test_whats_next.bats
bash scripts/work-queue/whats-next.sh --all
bash scripts/work-queue/whats-next.sh --category harness
bash scripts/work-queue/whats-next.sh --subcategory work-queue
```
