# WRK-1141 Plan: Post-Commit Auto-Push + Trunk-Based Routing

## Route B — Inline Plan

### Objective
Encode the trunk-based git policy mechanically via hooks and scripts, not prose.

### Steps

1. **Write `scripts/hooks/post-commit`**
   - Guards: `SKIP_PUSH=1`, `CI=true`/`GITHUB_ACTIONS`, detached HEAD, no upstream, submodule context
   - On guard hit: exit 0 silently (or warn for missing upstream)
   - On pass: `git push` to current branch's upstream
   - Pattern: mirrors `post-merge` / `post-checkout` style

2. **Write `scripts/work-queue/start-wrk.sh WRK-NNN`**
   - Parse WRK frontmatter `complexity` field (simple/medium/complex) and `compound` flag
   - simple/single-session → print routing message (commit to main)
   - medium/multi-session → `git checkout -b feature/WRK-NNN-<slug>`
   - complex/compound → same as medium + print worktree hint
   - Slug derived from WRK `title` field (lowercase, hyphenated, first 5 words)

3. **Update `scripts/setup/install-all-hooks.sh`**
   - No change needed — installer already copies all `scripts/hooks/*` automatically
   - Verify this in tests

4. **Write `tests/scripts/test_post_commit_push.sh`**
   - ≥5 tests: SKIP_PUSH guard, CI guard, detached HEAD guard, no-upstream guard, normal push
   - PASS_COUNT/FAIL_COUNT pattern matching existing hook tests

5. **Commit + push**

### Test Strategy
- Unit tests via shell (no git daemon needed — mock git commands with stubs)
- Test submodule detection via `git rev-parse --show-superproject-working-tree`
- All guards testable in isolation

### Acceptance Criteria
- [ ] `scripts/hooks/post-commit` exists with all guards
- [ ] `SKIP_PUSH=1 git commit` skips push
- [ ] `CI=true git commit` skips push
- [ ] `scripts/work-queue/start-wrk.sh` routes simple/medium/complex correctly
- [ ] `install-all-hooks.sh` picks up `post-commit` automatically
- [ ] Tests: ≥5 PASS, 0 FAIL
