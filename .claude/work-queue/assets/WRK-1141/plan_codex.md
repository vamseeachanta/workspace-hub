# Codex Cross-Review — WRK-1141 Plan

## Verdict: REQUEST_CHANGES

### Issues Found

1. **`post-commit` guard coverage incomplete** — missing rebase, cherry-pick, amend/reword states where auto-pushing rewritten commits is risky
2. **Tests don't cover `start-wrk.sh`** — no tests for simple/medium/complex routing, branch-already-exists, invalid/missing WRK metadata, or submodule guard
3. **Installer rollout too narrow** — `verify-setup.sh` and `setup-hooks.sh` hard-code hook lists; plan should update these or explicitly scope them out
4. **`start-wrk.sh` routing inputs underspecified** — no canonical source for session count, no defined behavior for already-on-feature-branch or branch-already-exists

### Suggestions

- Add guards for rebase-in-progress (`.git/rebase-merge`, `.git/rebase-apply`), cherry-pick (`.git/CHERRY_PICK_HEAD`), merge-conflict, amend detection via `GIT_REFLOG_ACTION`
- Add dedicated `start-wrk.sh` test file with hermetic fixtures
- Update `scripts/setup/verify-setup.sh` to include `post-commit`
- Define routing precedence: `compound=true` overrides complexity; specify branch-already-exists behavior
