---
name: slim-git-history
description: Diagnose and reduce git repository bloat — multi-GB .git, slow git status/fetch/clone caused by large binaries committed to history. Consolidates packs and enables the untracked-cache (always-safe wins), then plans an operator-gated history rewrite that strips only large already-deleted blobs. Use when a repo's .git is multiple GB, git ops are slow, or the user mentions "repo bloat", "shrink/slim .git", "git filter-repo", "repo health", or large binaries in git history. Safe to point at any workspace-hub repo.
---

# Slim Git History

Reclaim space and speed up git when a repo's `.git` has grown to multiple GB (the
digitalmodel #1142 pattern). Works per-repo; repeat across repos.

## Safety rules (READ FIRST — these are non-negotiable)

- **The agent NEVER force-pushes** — it is auto-denied, and history rewrite needs
  one. The agent does analysis + planning; the **operator** runs the rewrite + push.
- **NEVER strip a currently-tracked path** without explicit per-file confirmation.
  Stripping removes it from the working tree entirely — committed deliverables
  (client reports, datasets) are often deliberately version-controlled. The
  TRACKED-vs-GONE classification in step 1 exists to prevent this.
- **Always back up before any rewrite** (mirror clone or `git bundle`).
- The **non-rewrite wins (step 2) are always safe** — do them regardless, even if
  the rewrite is deferred.

## Step 1 — Measure & classify (read-only)

```
bash scripts/analyze-repo-bloat.sh [repo-path] [top-N]
```
Reports `.git` size, pack/loose-object counts, and the largest blob paths in
history, each tagged **TRACKED** (still in current tree — keep) or **GONE**
(already deleted — safe to strip). The reclaim estimate is the sum of GONE bytes.
If `.git` is small or all big blobs are TRACKED, stop — a rewrite isn't warranted.

## Step 2 — Safe non-rewrite wins (no force-push, do always)

```
git gc                                # 14 packs -> 1-2, prune loose objects
git config core.untrackedCache true   # stop git status re-stat'ing the whole tree
git update-index --untracked-cache
```
- Skip `feature.manyFiles` — it flips `index.skipHash`/index v4, which can break
  cron/auto-sync tooling on a shared store.
- `gc` consolidates and re-deltas (faster object access) but does **not** shrink
  reclaimable history — reachable blobs stay. That needs step 3.
- Run `git gc` only when no auto-sync / concurrent git op is mid-flight.

## Step 3 — Plan the rewrite (target only GONE blobs)

Pick the narrowest filter that hits the GONE bytes. Common forms:
```
# by size (strips every blob over the threshold, from all history):
git filter-repo --strip-blobs-bigger-than 10M --analyze   # dry-run report first
git filter-repo --strip-blobs-bigger-than 10M

# by path (preferred when GONE bytes are concentrated in known dirs):
git filter-repo --path path/to/old-junk/ --invert-paths
```
Build an explicit keep-list from the TRACKED rows. Prefer `--path` over a blanket
size strip when a size threshold would also catch a TRACKED deliverable.

## Step 4 — Operator executes (STOP and hand off)

The agent stops here and hands the operator this sequence:
```
git clone --mirror <repo> ../<repo>-backup.git     # 1. backup
git filter-repo <planned args>                      # 2. rewrite (in a fresh clone)
git push --force --all && git push --force --tags    # 3. force-push (OPERATOR)
git gc --prune=now --aggressive                      # 4. reclaim locally
```

## Step 5 — Coordination (shared-repo hazards)

- **Pause the cron auto-sync** first — it does `git reset --hard origin/main` and
  will fight the rewrite or clobber it.
- After force-push, **every clone, worktree, and CI runner must re-clone or hard
  reset** to the rewritten history.
- **Open PRs are invalidated** (their commit SHAs no longer exist) and must be
  recreated from the rewritten base.

## Step 6 — Verify

```
du -sh .git              # confirm shrink
git fsck --full          # integrity
git clone <remote> /tmp/smoke && cd /tmp/smoke && git log --oneline -1   # fresh-clone smoke test
```

See [scripts/analyze-repo-bloat.sh](scripts/analyze-repo-bloat.sh) for the analysis details.
