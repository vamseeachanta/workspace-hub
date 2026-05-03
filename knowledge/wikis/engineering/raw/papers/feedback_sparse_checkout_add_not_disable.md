> Git-tracked snapshot from Claude auto-memory. Captured: 2026-05-02
> Source: /home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/feedback_sparse_checkout_add_not_disable.md

---
name: Sparse-checkout: use `add`, never `disable`
description: When a file shows on GitHub but is missing locally in acma-projects, use `git sparse-checkout add <path>`; never `disable` (it tries to materialize ~329K files and hangs)
type: feedback
originSessionId: bb9781d7-842a-4188-b499-ec16a8d2881f
---
When a path is visible on the GitHub web UI but missing from the local working tree, the canonical cause is sparse-checkout. The fix is `git sparse-checkout add <path>` — not `disable`.

**Why:**
- `acma-projects` is the only repo in `/mnt/local-analysis/workspace-hub/` with sparse-checkout enabled (verified 2026-04-30 via per-repo `core.sparseCheckout` survey across all sibling repos).
- The repo has 368,433 tracked files; only ~22,048 (6%) are materialized by design. The 89% gap is not accidental — it's the workspace-hub overlay design noted in `~/.claude/CLAUDE.md` ("Sparse overlay | `~/workspace-hub` may be overlay").
- Running `git sparse-checkout disable` on this repo hung for 22+ minutes in I/O-wait state on 2026-04-30, holding `.git/index.lock` and blocking every other git operation including queued `git status` calls. The disable triggers materialization of ~329K skipped files, which the `/mnt/local-analysis/` filesystem cannot handle quickly.
- A parallel Codex session ran the same `disable` concurrently — second confirmation that the wrong-tool reflex is easy to fall into across providers.

**How to apply:**
1. **Detect**: `git status` will print "You are in a sparse checkout with N% of tracked files present" — that's the siren. A wide gap (≤10%) means most files are unmaterialized. Don't assume "missing locally" = "missing from repo".
2. **Confirm path exists on remote**: `git ls-tree --name-only origin/main <path>` (cheap, no checkout).
3. **Materialize the subtree**: `git sparse-checkout add <path>` — O(files-in-path), seconds for typical paths.
4. **Inspect cone**: `git sparse-checkout list` shows what's currently allowlisted.
5. **Never run `git sparse-checkout disable` on acma-projects** without explicit user opt-in for a 30+ min materialization. If interrupted: SIGINT is safe, releases `index.lock` cleanly, leaves prior `add` operations intact.
6. **Avoid `git status -uall`** on this repo — workspace CLAUDE.md flags it explicitly as a memory-pressure hazard.
7. **Other repos**: 20+ sibling repos in workspace-hub are full (non-sparse) checkouts — the missing-file symptom there has a different root cause; do not reach for sparse-checkout commands.

**Pilot incident**: 2026-04-30 — user reported `B1528/` invisible locally but present on GitHub. `git sparse-checkout add B1528` resolved in seconds; subsequent `disable` attempt hung 22 min, was SIGINT'd, no harm done.
