# AC Test Matrix — WRK-1141

| AC | Test | File | Result |
|----|------|------|--------|
| post-commit exists with all guards | test 1-7 verify each guard exits cleanly | test_post_commit_push.sh | PASS |
| SKIP_PUSH=1 skips push | SKIP_PUSH=1-skips-push | test_post_commit_push.sh | PASS |
| CI=true skips push | CI=true-skips-push | test_post_commit_push.sh | PASS |
| Rebase/cherry-pick/amend guards | rebase-in-progress, amend-GIT_REFLOG_ACTION | test_post_commit_push.sh | PASS |
| No upstream warns and skips | no-upstream-warns-and-skips | test_post_commit_push.sh | PASS |
| Normal path push fires in background | normal-path-push-fires | test_post_commit_push.sh | PASS |
| start-wrk.sh routes simple→main | simple-commits-to-main | test_start_wrk.sh | PASS |
| start-wrk.sh routes medium→branch | medium-creates-branch | test_start_wrk.sh | PASS |
| start-wrk.sh routes complex→branch | complex-creates-branch | test_start_wrk.sh | PASS |
| compound=true→branch override | compound-true-creates-branch-even-for-simple | test_start_wrk.sh | PASS |
| Branch-already-exists exits 0 | branch-already-exists-exits-0 | test_start_wrk.sh | PASS |
| verify-setup.sh includes post-commit | grep test | scripts/setup/verify-setup.sh | PASS |
| install-all-hooks.sh picks up post-commit | installed: post-commit | install-all-hooks.sh output | PASS |

**Total: 13 PASS, 0 FAIL**
