# 2026-05-01 — acma-projects sparse-checkout B1528 visibility

## Trigger

User: "git pull and sync this repo" → "I can not see these files: https://github.com/vamseeachanta/acma-projects/tree/main/B1528" → "ensure this does not happen for any repos and sync happens" → "what is sparse-checked-out?"

## Outcome

- ✅ `acma-projects` synced — already up to date with `origin/main` at `f5cc50c5` (no commits behind/ahead)
- ✅ `B1528/` materialized via `git sparse-checkout add B1528` — both subtrees (`excel_to_py/`, `ref/`) now visible
- ✅ Sibling-repo sparse survey: `acma-projects` is the **only** repo in `/mnt/local-analysis/workspace-hub/` with `core.sparseCheckout=true`. All other ~20 sibling repos are full checkouts.
- ✅ Memory entry written: `feedback_sparse_checkout_add_not_disable.md` + index pointer in `MEMORY.md`

## Repo profile (acma-projects)

| Metric | Value |
|---|---|
| Tracked files | 368,433 |
| Materialized on disk | 22,048 (~6%) |
| Skipped (lazy) | 328,958 (~89%) |
| Sparse-checkout | enabled (intentional, by design) |

## Anti-pattern observed and corrected

`git sparse-checkout disable` hung for 22+ minutes in I/O-wait state holding `.git/index.lock`. Root cause: disable triggers materialization of all ~329K skipped files, which the `/mnt/local-analysis/` filesystem cannot service quickly. SIGINT cleaned up safely (no index corruption, B1528 stayed materialized via the prior `add`).

A parallel Codex session (`CODEX_COMPANION_SESSION_ID=a1995a22-...`) ran the same `disable` concurrently — confirmation that the wrong-tool reflex is cross-provider. Both interrupted.

## Durable pattern (recorded in memory)

When a path is visible on GitHub but missing locally:
1. **Detect**: `git status` prints `"You are in a sparse checkout with N% of tracked files present"` — the warning siren.
2. **Confirm path on remote**: `git ls-tree --name-only origin/main <path>` (cheap, no checkout).
3. **Materialize**: `git sparse-checkout add <path>` — O(files-in-path), not O(repo).
4. **Inspect cone**: `git sparse-checkout list`.
5. **Never**: `git sparse-checkout disable` on this repo without explicit user opt-in for a 30+ min materialization.
6. **Avoid**: `git status -uall` on this repo (workspace CLAUDE.md explicit hazard).

## Side observations

- A parallel session was running `git status -z -uall` on this repo — directly contradicts the workspace CLAUDE.md `"Never use the -uall flag"` directive. Not from this Claude session; left untouched (read-only).
- `git status` with default flags can take minutes on this repo because it stats all 368K tracked entries. Prefer cheap reads (`git ls-tree`, `git ls-files | head`, direct `ls`) when verifying state.

## Files touched

- `/home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/feedback_sparse_checkout_add_not_disable.md` (new)
- `/home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/MEMORY.md` (added one index line under Feedback section)
- `/mnt/local-analysis/workspace-hub/acma-projects/.git/info/sparse-checkout` (cone updated to include `B1528`)

## Related memory

- `feedback_sparse_checkout_add_not_disable.md` — full rule with Why/How-to-apply
- `~/.claude/CLAUDE.md` — references workspace-hub overlay design that motivates sparse-checkout
