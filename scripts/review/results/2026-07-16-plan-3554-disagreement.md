# Disagreement report — plan #3554 (2026-07-16)

## Verdicts

| Provider | Verdict |
|---|---|
| claude | UNAVAILABLE (claude CLI failed, rc=1: no stderr captured) |
| codex | MAJOR |
| codex-r1 | MAJOR |
| disagreement-r1 | | Provider | Verdict | |
| gemini | UNAVAILABLE (gemini CLI failed, rc=1: no non-interactive gemini auth configured (GEMINI_API_KEY/GOOGLE_API_KEY/~/.gemini/oauth_creds.json) ) |

## Findings unique to each provider

A finding is 'unique to X' if its text appears in X's artifact but not
verbatim in any other provider's artifact.

### claude

(no findings unique to this provider)

### codex

- Plan Acceptance Criteria line `bash -n scripts/readiness/publish-equality.sh scripts/readiness/equality-matrix-cron.sh` is a false verification gate. Bash checks only the first script argument; the second argument is treated as `$1`. I verified this by running `bash -n scripts/readiness/publish-equality.sh scripts/readiness/definitely-missing-for-bash-n-check.sh`, which returned `status=0` even though the second path does not exist. This means `docs/plans/2026-07-16-issue-3554-windows-equality-publisher.md:176` does not actually syntax-check `scripts/readiness/equality-matrix-cron.sh`.
- The canonical Codex review artifact named by the plan is currently unusable. `docs/plans/2026-07-16-issue-3554-windows-equality-publisher.md:10` points to `scripts/review/results/2026-07-16-plan-3554-codex.md`, but that file is zero bytes in the working tree, and `git diff` shows the prior MAJOR review content deleted. The preserved content exists only in `scripts/review/results/2026-07-16-plan-3554-codex-r1.md`, while the plan’s summary at line 187 still says “re-review pending.”
- The plan cites `docs/standards/CONTROL_PLANE_CONTRACT.md` for a stronger claim than the file supports. `docs/plans/2026-07-16-issue-3554-windows-equality-publisher.md:26` says the standard requires that “a Windows-scheduled Bash path cannot depend silently on a Linux-only executable,” but `docs/standards/CONTROL_PLANE_CONTRACT.md` is about `AGENTS.md`, provider adapters, legacy paths, and reading order. The Windows scheduling evidence is in `config/scheduled-tasks/schedule-tasks.yaml:31-50`, not that standard.
- The plan acknowledges a correctness race and leaves it outside scope without a gating test. `docs/plans/2026-07-16-issue-3554-windows-equality-publisher.md:198` says `collect-equality.sh` writes YAML directly while the publisher reads it. Current code confirms direct write at `scripts/readiness/collect-equality.sh:486` and `scripts/readiness/collect-equality.sh:495`, while the publisher accepts a file based on `generated_at` only at `scripts/readiness/publish-equality.sh:61` and loops over local equality YAML at `scripts/readiness/publish-equality.sh:77`. The proposed tests cover publisher/publisher races, but not collector/publisher partial-read behavior.
- Acceptance Criteria line 177 includes “the targeted security scan” without naming a command, file, or expected output. `docs/plans/2026-07-16-issue-3554-windows-equality-publisher.md:177` names `bash scripts/legal/legal-sanity-scan.sh --diff-only` concretely, then adds an undefined scan that cannot be executed or reviewed.

### codex-r1

(no findings unique to this provider)

### disagreement-r1

- A finding is 'unique to X' if its text appears in X's artifact but not
- verbatim in any other provider's artifact.
- ### claude
- (no findings unique to this provider)
- ### codex
- ### gemini
- (no findings unique to this provider)

### gemini

(no findings unique to this provider)

