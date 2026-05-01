# Disagreement report — plan #2550 (2026-04-29)

## Verdicts

| Provider | Verdict |
|---|---|
| claude | UNAVAILABLE (claude CLI failed, rc=124: SessionEnd hook [node \"${CLAUDE_PLUGIN_ROOT}/scripts/session-lifecycle-hook.mjs\" SessionEnd] failed: Hook cancelled ) |
| codex | UNAVAILABLE (codex CLI failed, rc=124: Reading additional input from stdin... OpenAI Codex v0.125.0 (research preview) -------- [1mworkdir:[0m /mnt/local-analysis/worktrees/nightly-immediate-batch2-20260430T034203Z [1mmodel:[0m gpt-5.5 [1mprovider:[0m openai [1mapproval:[0m never [1msandbox:[0m workspace-write [workdir, /tmp, $TMPDIR, /home/vamsee/.codex/memories] [1mreasoning effort:[0m medium [1mreasoning summaries:[0m ) |
| gemini | MAJOR |

## Findings unique to each provider

A finding is 'unique to X' if its text appears in X's artifact but not
verbatim in any other provider's artifact.

### claude

(no findings unique to this provider)

### codex

(no findings unique to this provider)

### gemini

- **Hallucinated Evidence Document**: In `§ Evidence (embedded verification)`, the plan claims `EXISTS: docs/handoffs/github-collaborator-only-lockdown-2026-04-29.md`. A workspace scan confirms this file does not exist anywhere. The plan relies on this nonexistent document to derive the Hermes cron job ID (`d9b2d1c2270d`) and the decommission strategy.
- **Archived Repositories (403 Forbidden)**: In `§ Pseudocode`, the plan requests `isArchived` from `gh repo list` but only filters by `isPrivate=false` (`filter isPrivate=false`). The GitHub API returns a 403 Forbidden when attempting to modify interaction limits on archived repositories. If any public repo is archived, the `PUT` request will fail.
- **Unset Limits (404 Not Found)**: In `§ Pseudocode`, the script calls `current = gh api repos/$OWNER/$repo/interaction-limits`. The GitHub API returns a `404 Not Found` if a repository has no interaction limit currently set. Because the script must adhere to the `secrets-scan.sh` pattern using `set -euo pipefail`, this GET request will exit non-zero on a 404, crashing the script instantly during a dry-run or verification phase.
- **Dead Code in Error Handling**: In `§ Pseudocode`, the script tracks failures using `FAIL_COUNT++`. However, because the script operates under `set -euo pipefail`, if the `gh api -X PUT` command fails due to API errors, permission issues, or network drops, the shell will terminate immediately. The `FAIL_COUNT` accumulation logic is dead code for these failure modes.
- **Technically Invalid Python Mocks**: In `§ TDD Test List`, the plan proposes a Python `pytest` suite that "mocks `gh` subprocess" to test the `renew-interaction-limits.sh` Bash script. Python's `unittest.mock` patches Python objects in memory, not shell commands executed by a child Bash process. Mocking a system executable for a Bash script requires stubbing it in the `$PATH`, which is what the proposed Bats tests already do. The Python test suite is technically unfeasible for unit-testing the Bash script internals as described.
- **Hallucinated Review Artifact**: In `§ Artifact Map`, the plan lists `scripts/review/results/2026-04-29-plan-2550-claude.md`. This file does not exist in the workspace.

