# AC Test Matrix: WRK-1064

| AC | Test | Status |
|----|------|--------|
| pre-push.sh runs changed-repo tests + quality checks | TestChangedOnly::test_changed_repo_subset_is_run | PASS |
| Blocks push on unexpected test failure or ruff error | TestFailureBlocks::test_failing_check_all_blocks_push | PASS |
| Blocks push on test failure | TestFailureBlocks::test_failing_run_tests_blocks_push | PASS |
| --changed-only default; --all full suite option | TestAllMode::test_all_flag_runs_every_repo | PASS |
| --no-verify / GIT_PRE_PUSH_SKIP usage logged | TestSkipBypass::test_skip_writes_jsonl_record | PASS |
| GIT_PRE_PUSH_SKIP exits 0 | TestSkipBypass::test_skip_exits_zero | PASS |
| Skip does not run checks | TestSkipBypass::test_skip_does_not_run_checks | PASS |
| New-branch push (remote zeros) falls back to all-repos | TestNewBranchFallback::test_new_branch_runs_all_repos | PASS |
| Delete-branch push skipped safely | TestNewBranchFallback::test_delete_branch_skipped | PASS |
| Hook completes / syntax valid | TestSmokeHelp::test_help_exits_zero | PASS |

**Total: 10 PASS, 0 FAIL**

Run: `uv run --no-project python -m pytest tests/hooks/test_pre_push.py -v` (0.52s)
