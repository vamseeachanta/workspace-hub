---
name: ntfs-fuse-git-stalls-local-analysis
description: "/mnt/local-analysis (NTFS fuseblk) intermittently stalls git porcelain, worktree add, and pytest plugin discovery — plumbing commits + shallow sparse clones on local disk are the workarounds"
metadata: 
  node_type: memory
  type: reference
  originSessionId: ace6a28d-6121-4899-8589-aaef66f300bd
---

`/mnt/local-analysis` is an NTFS FUSE mount (`fuseblk /dev/sdc1`) that intermittently
stalls filesystem-heavy operations for minutes (observed 2026-07-10 in aceengineer-strategy
and digitalmodel; same mount hosts all repos, so applies everywhere).

Symptoms and workarounds:

1. **`git commit` (porcelain) hangs indefinitely** even with `--no-verify`, no hooks, no
   gpgsign, no index.lock — it stalls after "read cache" (worktree re-stat). `git add`
   usually works (sometimes needs retries/long timeout). Workaround: commit via plumbing —
   `TREE=$(git write-tree); COMMIT=$(git commit-tree $TREE -p HEAD -m "msg"); git update-ref refs/heads/<branch> $COMMIT`
   (never touches the worktree). Full-tree `git status` / `git diff --cached` also hang;
   pathspec-scoped `git status -- <dir>` is fine.
2. **`git worktree add` hangs >17 min mid-checkout**. Workaround: kill + `git worktree prune`
   (also delete the stale local branch), then use a **shallow sparse clone placed on fast
   LOCAL disk** (e.g. the session scratchpad) instead:
   `git clone --depth 1 https://github.com/<owner>/<repo> <local-dir>`; the FUSE checkout's
   `.venv` interpreter can still be used from the clone.
3. **pytest hangs at plugin discovery** (even `pytest --version`) when the venv lives on the
   FUSE mount. Workaround: `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1` locally; CI unaffected.

General: wrap all git commands in `timeout`, run long chains via run_in_background so the
2-minute foreground wall doesn't kill them, and remember exit 143/124 chains may be
PARTIALLY applied — verify state (`git log -1`, scoped status) before retrying.
Push/fetch can also be slow (network + FUSE); background them.
