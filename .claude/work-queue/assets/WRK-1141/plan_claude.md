# WRK-1141 Plan: Post-Commit Auto-Push + Trunk-Based Routing (v2 — post cross-review)

## Route B — Inline Plan

### Cross-Review Response

| Finding | Source | Resolution |
|---------|--------|------------|
| Missing rebase/cherry-pick/amend guards | Codex | Added — detect via `.git/rebase-merge`, `.git/rebase-apply`, `.git/CHERRY_PICK_HEAD`, `GIT_REFLOG_ACTION` |
| Synchronous push blocks terminal | Gemini | Background push: `(git push origin HEAD > /tmp/post-commit-push.log 2>&1 &)` |
| Amend → non-fast-forward rejection | Gemini | Guard: detect `GIT_REFLOG_ACTION=reword\|amend` → skip push |
| Tests don't cover start-wrk.sh | Codex | Added dedicated test section for routing |
| verify-setup.sh hard-codes hook list | Codex | Update verify-setup.sh to include post-commit |
| Frontmatter parsing fragile | Gemini | Use `grep -m1 "^field:"` pattern — safe for our controlled YAML format |
| Branch-already-exists behavior | Codex | Print warning + exit 0 (don't fail, let user handle) |

### Steps

1. **Write `scripts/hooks/post-commit`**

   Guards (exit 0 silently unless noted):
   - `SKIP_PUSH=1` → skip
   - `CI=true` / `GITHUB_ACTIONS` → skip
   - Detached HEAD (`git symbolic-ref HEAD` fails) → skip
   - No upstream configured (`git rev-parse @{u}` fails) → warn + skip
   - Submodule context (`git rev-parse --show-superproject-working-tree` non-empty) → skip
   - Rebase in progress (`.git/rebase-merge` or `.git/rebase-apply` exists) → skip
   - Cherry-pick in progress (`.git/CHERRY_PICK_HEAD` exists) → skip
   - Amend/reword (`GIT_REFLOG_ACTION` contains "amend" or "reword") → skip
   - Merge conflict (`.git/MERGE_HEAD` exists) → skip

   On pass: background push with log:
   ```bash
   (git push origin HEAD > /tmp/post-commit-push.log 2>&1 &)
   ```

2. **Write `scripts/work-queue/start-wrk.sh WRK-NNN`**

   Routing precedence:
   1. `compound: true` → feature branch regardless of complexity
   2. `complexity: simple` → print "Commit to main directly"
   3. `complexity: medium` or `complexity: complex` → `git checkout -b feature/WRK-NNN-<slug>`

   Branch-already-exists: print warning, exit 0 (let user handle)
   Frontmatter parsing: `grep -m1 "^field:" file.md | sed 's/^field: *//'`
   Slug: lowercase title, first 5 words, hyphenated

3. **Update `scripts/setup/verify-setup.sh`**
   - Add `post-commit` to the verified hooks list

4. **Write `tests/scripts/test_post_commit_push.sh`** — ≥8 tests:
   - `SKIP_PUSH=1` guard
   - `CI=true` guard
   - Detached HEAD guard
   - No upstream guard
   - Submodule guard
   - Rebase-in-progress guard
   - Amend guard (`GIT_REFLOG_ACTION=amend`)
   - Normal path: push fires in background

   **Write `tests/scripts/test_start_wrk.sh`** — ≥5 tests:
   - simple → main message
   - medium → branch creation
   - complex → branch creation
   - compound=true → branch regardless of complexity
   - Branch-already-exists → warning, exit 0

5. **Commit + push**

### Acceptance Criteria
- [ ] `scripts/hooks/post-commit` exists with 9 guards
- [ ] Push runs in background (terminal not blocked)
- [ ] `SKIP_PUSH=1 git commit` skips push (tested)
- [ ] `CI=true git commit` skips push (tested)
- [ ] Rebase/cherry-pick/amend/merge-conflict guards (tested)
- [ ] `scripts/work-queue/start-wrk.sh` routes simple/medium/complex/compound correctly (tested)
- [ ] `scripts/setup/verify-setup.sh` includes `post-commit`
- [ ] Tests: ≥8 PASS in test_post_commit_push.sh, ≥5 PASS in test_start_wrk.sh, 0 FAIL
