# WRK-1161 Review — Suppress CLI stderr noise

## Route A Self-Review

Codex cross-review not required for Route A simple items per SKILL.md §Complexity Routing.
Route A: single cross-review pass (codex hard gate waived for simple items).

### Changes Reviewed
1. `exit_stage.py` — ImportError silently caught; no functional change
2. `stage_dispatch.py` — severity prefixes added to D-item messages
3. `archive-item.sh` — HTML gen errors logged to file instead of /dev/null
4. `claim-item.sh` — quota warning redirected to stderr

### Verdict
APPROVE — minimal, targeted fixes with no architectural impact. 6 TDD tests pass.
