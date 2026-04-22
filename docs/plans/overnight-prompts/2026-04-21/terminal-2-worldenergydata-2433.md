Work in `/mnt/local-analysis/worktrees/worldenergydata-2433`.

Mission: execute workspace-hub issue #2433 against live `worldenergydata` main. Do a verification-first pass before editing, because some CI softening already appears to have landed (`continue-on-error` is already present in `.github/workflows/ci.yml`). Then implement only the missing remainder of the approved plan, validate, push to `main`, post evidence, and close only if acceptance is met.

Hard rules:
- Use `uv run` for Python.
- Do NOT ask the user any questions.
- Final landing target is `origin/main`; this worktree branch is just the isolation boundary.
- Respect the approved plan, but do not blindly replay stale steps if main already moved.
- Keep scope limited to #2433: CI collection/lint unblock for main.

Owned paths:
- `tests/conftest.py`
- `.github/workflows/ci.yml`
- the specific test files reformatted by black/isort under `tests/`

Read-only context:
- `/mnt/local-analysis/workspace-hub/docs/plans/2026-04-21-issue-2433-worldenergydata-ci.md`
- `/mnt/local-analysis/workspace-hub/docs/handoffs/2026-04-22-ecosystem-ci-queue-execution.md`
- `pytest.ini`
- repo AGENTS.md

Forbidden paths:
- `src/` implementation code unless absolutely required by formatter/import-order validation on touched test files
- docs/plans or workspace-hub repo files
- unrelated cleanup beyond #2433 acceptance

Required workflow:
1. Post a start comment on workspace-hub issue `#2433` noting you are doing a live already-done precheck before implementing.
2. Precheck live state:
   - inspect `git log --oneline -8`
   - inspect current `tests/conftest.py` skip logic
   - inspect `.github/workflows/ci.yml`
   - run targeted collection proof matching the plan as closely as practical
   - run black/isort checks to identify the actual remaining lint blockers
   - inspect recent GitHub Actions runs for `vamseeachanta/worldenergydata`
   - decide explicitly: `already done`, `not done`, or `partially done`
3. If not/partially done, implement only the missing delta needed for the approved acceptance target:
   - complete the 22-path skip coverage in `tests/conftest.py` if incomplete
   - keep or refine the `continue-on-error` softening only if still needed and still consistent with the plan
   - run black/isort on the exact files needed to get lint green
4. Validation gates:
   - exact or near-exact collection command proving the collection errors are gone
   - black --check / isort --check-only for `src/ tests/`
   - any additional targeted test/CI proxy check justified by the plan
5. Commit only the bounded #2433 change.
6. Rebase if needed, then push to `origin/main` via `git push origin HEAD:main`.
7. Monitor the resulting CI run and capture concrete evidence for `test`, `lint`, and any remaining non-blocking `type-check` status.
8. Post an evidence-rich comment on `#2433` and a concise parent update on `#2424`.
9. Close `#2433` only if the accepted main-branch unblock actually landed. Otherwise leave it open with the precise residual blocker.

Required closeout block on `#2433`:
- Result: landed-and-closed OR landed-but-still-blocked
- What changed
- Collection/lint validation commands + results
- CI run id / URL / relevant job outcomes
- Commit hash pushed
- Residual blocker or follow-on issue need

Do not end with only local edits or only a commit. Finish push + comment + close/no-close decision.
