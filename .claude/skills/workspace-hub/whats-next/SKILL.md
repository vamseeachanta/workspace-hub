---
name: whats-next
description: >
  Refreshes and displays the prioritised "run now" work list for the WRK queue.
  Use when the user types /whats-next, asks "what's next", "what can I run now",
  "refresh the todo list", "what's ready to start", "show me the queue", or wants
  to know which items are unblocked. Resolves blocker status by checking the archive,
  separates working/high/newly-unblocked/medium/externally-blocked, and highlights
  parallel execution opportunities. Defaults to harness category; supports --all and
  --category flags. Always invoke this skill for work queue status requests — do not
  try to reconstruct the list from memory.
version: 1.0.0
category: workspace-hub
type: skill
trigger: manual
---

# What's Next

Runs `scripts/work-queue/whats-next.sh` and presents the output. This is the
canonical way to refresh the prioritised work list — it resolves blockers against
the archive, so items whose deps have been completed are correctly shown as ready.

## Steps

1. Run the script:
   ```bash
   bash scripts/work-queue/whats-next.sh
   ```

2. Present the output verbatim — the script handles all formatting and categorisation.

3. If the user wants a different scope, re-run with flags:
   - `--all` — show all categories (not just harness)
   - `--category <name>` — filter to a specific category (e.g. `engineering`, `data`)
   - `--limit N` — show N medium-priority items (default 20)

4. After presenting, offer to start the top unblocked item or answer questions about
   specific WRKs in the list.

## Output sections

| Section | Meaning |
|---|---|
| ▶ WORKING | Currently active in working/ |
| ⚠ IN-PROGRESS UNCLAIMED | Pending items with session-lock < 2h old (not yet claimed) |
| ★ HIGH PRIORITY | High-priority, no blockers, ready to start |
| ↑ NEWLY UNBLOCKED | Had WRK blockers that are now all archived |
| · MEDIUM | Medium-priority, no blockers |
| ✗ EXTERNALLY BLOCKED | status=blocked for a non-WRK reason |

## Flags

```
--all              Show all categories (default: harness)
--category <name>  Filter to one category
--limit N          Cap the medium section at N rows (default 20)
```

## Notes

- Use `bash scripts/work-queue/active-sessions.sh` for a full session audit including
  claimed items. The ⚠ IN-PROGRESS UNCLAIMED section in whats-next shows only pending
  items — active-sessions.sh shows both claimed and unclaimed in one view.
- "Newly unblocked" means the item previously had `blocked_by: [WRK-NNN]` entries
  that are now in the archive — these are the highest-leverage next items since their
  infrastructure is now ready.
- "Externally blocked" means `status: blocked` in the blocked/ directory but with no
  active WRK deps — needs manual investigation of the block reason.
- Parallel hints are based on `computer:` field differences; always verify
  `target_repos` before actually running in parallel.
