# Plan: WRK-682 — Cross-Terminal Queue Sync

## Goal
Implement automatic, git-aware synchronization of the work queue across all terminal sessions and workstations.

## Proposed Changes

### 1. New Sync Daemon
- Create `scripts/work-queue/auto-sync-queue.sh`.
- Use `inotifywait` to monitor `.claude/work-queue/` for `modify,move,create,delete`.
- Implement a 5-second debounce logic to prevent rapid-fire syncs during batch operations.
- Trigger `scripts/repository_sync auto` on detection of changes.
- Log activities to `logs/work-queue-sync.log`.

### 2. Status Line Enhancement
- Update `.claude/statusline-command.sh` to extract the top-priority task from `INDEX.md`.
- Display the task ID and a truncated title in the terminal status bar.

## Verification Plan

### Automated Tests
- None (script is a wrapper around existing git tools).

### Smoke Tests (Variation Tests)
1. **Manual Modification**: Touch a file in `.claude/work-queue/pending/` and verify that `repository_sync auto` is triggered in the logs.
2. **Debounce Test**: Perform multiple rapid modifications and verify only one sync occurs within the 5-second window.
3. **Status Line Test**: Verify that the top-priority item from `INDEX.md` appears correctly in the shell status bar.

## Acceptance Criteria
- [ ] Daemon monitors queue directory and triggers git sync.
- [ ] Status line shows the current top priority task.
- [ ] No recursive sync loops observed.
