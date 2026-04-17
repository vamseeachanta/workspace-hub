# Runbook: Oversized state-file recovery

> **Issue:** [#2070](https://github.com/vamseeachanta/workspace-hub/issues/2070)
> **Plan:**  `docs/plans/2026-04-16-issue-2070-state-size-guard.md`

This runbook covers the recovery path when a tracked file under
`.claude/state/` blows past GitHub's 100 MB push limit despite the size guards.
Use it when a `git push` is rejected with:

```
remote: error: File <path> is XXX MB; this exceeds GitHub's file size limit of 100.00 MB
```

---

## Prevention is wired (you should rarely need this runbook)

Two hooks installed by `scripts/enforcement/install-hooks.sh` should catch the
oversized blob *before* it reaches GitHub:

| Hook | Phase | What it checks |
|------|-------|----------------|
| `.claude/hooks/check-state-file-size-precommit.sh` | pre-commit | staged blob size via `git cat-file -s :0:<file>` |
| `.claude/hooks/check-state-file-size-prepush.sh`  | pre-push   | every blob in the to-be-pushed commit range |

Thresholds (env-overridable):
- `STATE_SIZE_WARN_MB`  = 50 (emits stderr warning)
- `STATE_SIZE_BLOCK_MB` = 75 (exit 1)

Watch path: `.claude/state/session-signals/`. Adjust with `STATE_SIZE_WATCH_PATH`.

If you reach this runbook anyway, one of these happened:
1. The hook is not installed on the machine that pushed (run `bash scripts/enforcement/install-hooks.sh`).
2. The file lives outside the watch path (extend the watch path or generalise the hook).
3. A single commit added enough delta to cross the threshold between pre-commit and pre-push checks (very unlikely with 25 MB headroom).

---

## Recovery: the file is in HEAD and the push fails

### Step 1 — diagnose

```bash
# Identify the offending blob path and its size
git rev-list --objects @{u}..HEAD \
  | git cat-file --batch-check='%(objecttype) %(objectsize) %(rest)' \
  | awk '$1=="blob" && $2 > 100000000 { print }'
```

### Step 2 — pick a recovery path

There are three options, in order of preference. **Always work on a branch.**

#### Option A — Rotate, then amend

If the offender is `cost-tracking.jsonl` (or another file the rotation script
knows about), this is fastest:

```bash
# 1. Reset the working tree to the parent of the bad commit
git reset HEAD^ -- .claude/state/session-signals/cost-tracking.jsonl

# 2. Run the rotation
bash scripts/state/rotate-cost-tracking.sh

# 3. Re-commit with the truncated live file + .gz archive
#    (the rotation script prints the exact commands)

# 4. Force-push the branch (only the local commit you authored)
git push --force-with-lease
```

#### Option B — Filter-repo to drop the blob from history

If the file is a one-off binary that was committed by mistake (not a state
signal we want to keep), excise it from the branch's history:

```bash
# Requires git-filter-repo: pip install git-filter-repo
git filter-repo --path .claude/state/session-signals/<offender> --invert-paths --force
git push --force-with-lease
```

> ⚠️ Only run `filter-repo` on a branch you own. **Never on `main`** without a
> coordinated team rebase plan.

#### Option C — Worktree reconstruction (the original ad-hoc fix)

When the branch history is contaminated and you'd rather start clean:

```bash
# 1. Stash any uncommitted work
git stash -u

# 2. Create a fresh worktree from the last good commit
LAST_GOOD=$(git log --before="$(date -d '1 day ago')" -n1 --format=%H)
git worktree add ../workspace-hub-clean "$LAST_GOOD"

# 3. Cherry-pick only the commits you want, skipping the one that introduced the bloat
cd ../workspace-hub-clean
git cherry-pick <good-sha-1> <good-sha-2> ...

# 4. Push the clean branch, then move back
git push -u origin main
cd -
```

---

## Consumer Compatibility (why rotation is gated)

Rotating `cost-tracking.jsonl` produces:
```
.claude/state/session-signals/cost-tracking.jsonl                 (truncated to 0 bytes)
.claude/state/session-signals/archive/cost-tracking-YYYY-MM-DD.jsonl.gz
```

If a consumer reads only the live `.jsonl`, it loses every record in the
archive after rotation. Three adversarial reviewers (Claude, Codex, Gemini)
called this out as a P1 risk.

The pre-implementation gate is:

```bash
bash scripts/state/verify-consumer-compat.sh
```

This script synthesizes a fixture (1 live record + 2 records in a gzipped
archive) and runs each known consumer against it. **If exit ≠ 0, the rotation
script refuses to run.**

### Known consumers
| Path | Behavior |
|------|----------|
| `scripts/ai/wrk_cost_report.py` | Updated in #2070 to glob `<dir>/archive/<stem>-*.jsonl.gz` and read transparently via `gzip.open`. |

### Adding a new consumer
When code starts reading `cost-tracking.jsonl` from a new place:
1. Make it use `wrk_cost_report.load_records(path)` if possible (it handles archives).
2. Otherwise, mirror the `_iter_sources()` pattern in `scripts/ai/wrk_cost_report.py`.
3. Add a new check block to `scripts/state/verify-consumer-compat.sh`.
4. Run `bash scripts/state/verify-consumer-compat.sh` — must exit 0.

---

## LFS-vs-gzip decision (deferred)

The plan considered Git LFS for `cost-tracking.jsonl` and rejected it for now:

- **Adopted:** gzip-in-tree under `archive/`. Compresses ~10× (45 MB JSONL → ~4–5 MB).
- **Rejected (for now):** Git LFS — adds a setup dependency on every machine,
  contradicting the "git-track everything" philosophy of #1782 (zero-loss
  agent learnings).

### When to revisit
Move to LFS if any of these occur:
- Total `archive/` size exceeds **500 MB** (clones become slow).
- A single consumer needs random-access reads on archived history (gzip is
  stream-only).
- More than three independent consumers need rotation-aware reads (LFS makes
  the file name single-source).

The weekly cron (`scripts/cron/state-size-report.sh`) reports archive size in
the YELLOW/RED summary; that's the trigger to revisit this runbook.

---

## Sanity checks (post-recovery)

After any of the recovery options above, confirm:

```bash
# 1. The hooks would catch a regression
bash .claude/hooks/check-state-file-size-precommit.sh   # exits 0 with no staged offenders

# 2. Consumer is still readable
uv run --no-project python scripts/ai/wrk_cost_report.py --csv | head -5

# 3. Verifier still passes
bash scripts/state/verify-consumer-compat.sh

# 4. Re-push and confirm GitHub accepts
git push
```

If anything fails here, stop and re-open #2070 with the diagnostic output —
that's a guard regression that needs a fix on top of the existing plan.
