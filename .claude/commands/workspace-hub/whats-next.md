---
name: whats-next
description: Refresh and display the prioritised "run now" work list — resolves blockers, separates working/high/newly-unblocked/medium, shows parallel hints
version: 1.0.0
category: workspace-hub
argument-hint: "[--all | --category <name> | --limit N]"
---

# /whats-next $ARGUMENTS

Runs `scripts/work-queue/whats-next.sh` and presents the output.

## Steps

1. Run the script, forwarding any arguments:
   ```bash
   bash scripts/work-queue/whats-next.sh $ARGUMENTS
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
| ★ HIGH PRIORITY | High-priority, no blockers, ready to start |
| ↑ NEWLY UNBLOCKED | Had WRK blockers that are now all archived |
| · MEDIUM | Medium-priority, no blockers |
| ✗ EXTERNALLY BLOCKED | status=blocked for a non-WRK reason |

## Notes

- Default scope is `harness` category. Use `--all` for the full picture.
- "Newly unblocked" = highest-leverage items; their infrastructure is now ready.
- Parallel hints are based on `computer:` field; verify `target_repos` before running in parallel.
- Skill reference: `.claude/skills/workspace-hub/whats-next/SKILL.md`
