# Disagreement report — plan #2550 (2026-05-01)

## Verdicts

| Provider | Verdict |
|---|---|
| codex | MAJOR |
| gemini | UNAVAILABLE (gemini CLI failed, rc=1: [WARN] Skipping unreadable directory: /tmp/snap-private-tmp (EACCES: permission denied, scandir '/tmp/snap-private-tmp') [WARN] Skipping unreadable directory: /tmp/systemd-private-384f6636782f40648bb07a1bce9c9cef-ModemManager.service-hqDDIK (EACCES: permission denied, scandir '/tmp/systemd-private-384f6636782f40648bb07a1bce9c9cef-ModemManager.service-hqDDIK') [WARN] Skipping unreadable directory: ) |

## Findings unique to each provider

A finding is 'unique to X' if its text appears in X's artifact but not
verbatim in any other provider's artifact.

### codex

- **MAJOR: The cited plan path does not match the inline review target.** The inline plan starts with status text `2026-04-30 reviewer blockers patched...` and includes `--check`, `jq`, `--post-comment`, archived repo reporting, and log-directory guards. The actual `docs/plans/2026-04-29-issue-2550-interaction-limit-renewal-scheduled-task.md` fetched from `main` still has older content: pseudocode only shows `renew-interaction-limits.sh [--dry-run]`, uses `gh repo list ... --paginate`, filters out archived repos entirely, and lacks the inline plan’s later acceptance criteria. This means the named artifact cannot be verified as the plan being reviewed.
- **MAJOR: The plan’s unset-limit handling is based on the wrong GitHub API behavior.** Plan §Acceptance Criteria says “Dry-run and verification GET calls handle GitHub `404 Not Found` as an explicit `unset` interaction-limit state.” Official GitHub REST docs for `GET /repos/{owner}/{repo}/interaction-limits` say that when there are no restrictions, “you will see an empty response” with `200 OK`, not a required 404. A Bash+jq implementation that only special-cases 404 can silently mishandle empty 200 output, especially under `set -euo pipefail`.
- **MAJOR: The scheduled task can pass config validation while lacking the authentication scope required by the GitHub API.** Plan §Acceptance Criteria requires `requires: [bash, gh, jq]`, but GitHub’s repository interaction-limit endpoints require Administration repository permission: read for GET and write for PUT. Neither §Files to Change nor §Acceptance Criteria specifies a required `GH_TOKEN`/auth preflight or token-scope verification before the scheduled job runs. A cron entry with `gh` installed but insufficient auth would fail at runtime.
- **MAJOR: The Bats test requirement introduces an untracked test runner dependency.** Plan §TDD Test List and §Acceptance Criteria require `bats tests/security/test_renew_interaction_limits.bats`. Repository search found no existing `.bats` tests, and `pyproject.toml` only declares pytest-related dev dependencies, not Bats. The plan adds a mandatory test command without adding installation, skip policy, or capability documentation for that runner.
- **MINOR: The plan still self-identifies as not approval-ready.** Plan front matter says “NOT approval-ready until fresh Codex/Gemini re-review returns no MAJOR or the user explicitly waives cross-provider evidence,” and §Adversarial Review Summary says latest Codex/Gemini final verdicts are MAJOR. This review can contribute one fresh review artifact, but it does not satisfy the plan’s own Gemini/no-MAJOR condition by itself.

### gemini

- (none)

