# Resource Pack: WRK-682

## Problem Context
Users working across multiple terminals and workstations experience "stale" work queue views. When one terminal updates the queue (e.g., claiming a task), other terminals don't see the change until a manual `git pull` or periodic sync occurs. WRK-682 aims to automate this sync using a file-system watcher.

## Relevant Documents/Data
- `scripts/repository_sync`: The core tool for auto-committing and pulling changes.
- `scripts/repository_sync-auto`: Helper providing `auto_sync_all`.
- `.claude/statusline-command.sh`: Terminal status line script for workspace-hub.
- `.claude/work-queue/INDEX.md`: Source of truth for queue status and top priorities.

## Constraints
- Must use standard Linux tools (`inotify-tools`) where possible.
- Must avoid recursive sync loops (ignore log directories).
- Must include a debounce mechanism to handle batch file updates.

## Assumptions
- `inotifywait` is available on the target workstation (dev-primary).
- The user has configured git remotes correctly for all submodules.

## Open Questions
- How does the daemon handle network latency during `git push/pull`?
- Should the status line polling frequency be adjusted if the queue updates very rapidly?

## Domain Notes
- This is a workflow automation task designed to improve developer/agent ergonomics in multi-seat environments.
