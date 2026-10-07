---
name: stage-prompt-drift-guard
description: Audit historical stage-prompt artifact drift from Claude logs, generate a package index, and enforce only newly introduced drift in CI and local pre-push hooks.
version: 1.0.0
tags: [claude, work-queue, drift, enforcement, ci, pre-push, audit]
related_skills: [session-corpus-audit, workflow-compliance-audit, overnight-parallel-agent-prompts]
---

# Stage Prompt Drift Guard

Use when Claude/work-queue history references `.claude/work-queue/assets/<work-item>/stage-*-prompt.md` files that no longer exist, and you need to make that drift visible without failing on all historical debt.

## When to use
- Claude session log audit shows many missing `stage-*-prompt.md` reads
- You want an auditable index of prompt packages and surviving evidence files
- You need a CI/local guard that blocks only newly introduced drift, not legacy repo drift

## Core approach

### 1. Extend the audit before enforcing
Build or update an audit script that:
- parses Claude post-hook log records
- detects prompt-like reads and stage prompt reads
- groups them by work item (`WRK-123`, `workspace-hub-456`)
- emits a `stage_prompt_packages` structure with:
  - `work_item`
  - `stages`
  - `prompt_files` with `path`, `exists`, `reads`
  - `evidence_files`

Important: scan both
- historical prompt reads from logs, and
- current asset directories under `.claude/work-queue/assets/*`
so packages with surviving evidence but no prompt files are still represented.

### 2. Generate a human-auditable report
Write markdown/JSON report artifacts under `docs/reports/`.
The markdown should include a “Stage prompt package index” section that lists for each package:
- stages seen
- prompt file count
- missing prompt artifact count
- evidence file count

This turns missing prompt drift into a visible artifact instead of a hidden log-only problem.

### 3. Detect real drift issues
A drift issue is:
- one or more missing stage prompt files, and
- no replacement evidence for that package

Useful replacement evidence:
- `.claude/work-queue/assets/<work-item>/evidence/*`
- explicit report/index paths if you intentionally replaced prompt artifacts with generated summaries

### 4. Enforce only newly introduced drift
Do NOT fail on the full historical backlog.
Add `--base-ref` / `--head-ref` support and compute:
```bash
git diff --name-status <base>...<head>
```
Then only fail when:
- a missing prompt path is in the deleted set for the current diff, and
- the same diff does not add replacement evidence or an approved report/index replacement

This is the key practical finding: strict enforcement on total historical drift is unusable; diff-scoped enforcement works.

### 5. Wire the guard into CI
Best home: an existing enforcement workflow for PRs.
Pattern:
- checkout with full history
- setup Python + uv
- run the drift checker with `--base-ref origin/main --head-ref HEAD --fail-on-issues`
- always append the markdown report to `$GITHUB_STEP_SUMMARY`

Expected result:
- historical repo drift remains visible in reports
- PRs only fail when they introduce new drift

### 6. Wire the same guard into local pre-push
Create a wrapper shell script, e.g. `scripts/enforcement/require-stage-prompt-drift.sh`, that:
- defaults to `origin/main...HEAD`
- skips cleanly if base ref is unavailable locally
- supports strict/advisory modes via env vars
- calls the Python drift checker with `--fail-on-issues`
- passes `--write-evidence-stubs` by default unless explicitly disabled
- writes JSONL audit events to `logs/hooks/stage-prompt-drift-events.jsonl`

Recommended env vars:
- `STAGE_PROMPT_DRIFT_BASE_REF`
- `STAGE_PROMPT_DRIFT_HEAD_REF`
- `STAGE_PROMPT_DRIFT_STRICT`
- `STAGE_PROMPT_DRIFT_SCRIPT`
- `STAGE_PROMPT_DRIFT_WRITE_STUBS`
- `STAGE_PROMPT_DRIFT_LOG`
- `DISABLE_ENFORCEMENT`

Behavior that proved useful:
- log `pass`, `warning`, `fail`, and `skip` verdicts
- print remediation guidance on warning/fail
- if strict mode is off, warn but allow push

Then wire it into `.git/hooks/pre-push` via the repo’s hook installer rather than editing hooks manually every time.

### 7. Add a local doctor/status command
Add `scripts/enforcement/stage-prompt-drift-status.sh` that reports:
- whether `scripts/enforcement/require-stage-prompt-drift.sh` exists
- whether `.git/hooks/pre-push` exists
- whether the hook references `require-stage-prompt-drift.sh`
- overall state: `ACTIVE` or `INACTIVE`

Recommended behavior:
- exit 0 only when all three conditions are satisfied
- print remediation: `bash scripts/enforcement/install-hooks.sh`

### 8. Surface drift activity in the compliance dashboard
Update `scripts/enforcement/compliance-dashboard.sh` to summarize `logs/hooks/stage-prompt-drift-events.jsonl`.
Include:
- whether the log file exists
- total event count
- counts by verdict (`pass`, `warning`, `fail`, `skip`, `unknown`)
- latest event summary

Important finding:
- do not let the dashboard fail merely because there were zero commits in the window; handle the no-commit case separately and still print drift-event status.

### 9. Auto-generate non-destructive evidence stubs for blocked work items
Extend the Python checker with `--write-evidence-stubs` support.
Useful pattern:
- detect whether the work item is blocked by checking `.claude/work-queue/{blocked,pending,working,done}` records
- if blocked and no replacement evidence exists, create:
  - `.claude/work-queue/assets/<work-item>/evidence/stage-prompt-drift-summary.stub.md`
- never overwrite an existing stub
- if a stub already exists, reuse/report it instead of replacing it

Stub content should include:
- work item id
- missing prompt paths
- blocked context / blocker lines from the work item record
- next actions telling the user to replace the stub with a human-authored summary

## Test strategy

Write tests before or with the implementation.

### Audit/report tests
Verify:
- `stage_prompt_packages` is emitted
- package entries include evidence files
- markdown includes the stage prompt package index

### Drift checker tests
Verify:
- missing prompt + no evidence => flagged
- missing prompt + evidence => not flagged
- diff filtering only flags deleted prompt files in current change set
- added evidence in same diff suppresses the failure
- CLI returns nonzero with `--fail-on-issues`

### Hook installer tests
Verify:
- installer appends the drift guard to `.git/hooks/pre-push`
- dry-run does not modify the hook

## Verification commands
```bash
uv run pytest tests/analysis/test_claude_session_ecosystem_audit.py \
  tests/analysis/test_stage_prompt_drift_check.py \
  tests/enforcement/test_require_stage_prompt_drift.py \
  tests/enforcement/test_install_hooks_stage_prompt_drift.py -q

uv run python scripts/analysis/stage_prompt_drift_check.py \
  --base-ref origin/main \
  --head-ref HEAD \
  --fail-on-issues

bash scripts/enforcement/install-hooks.sh --dry-run
bash scripts/enforcement/require-stage-prompt-drift.sh
```

## Pitfalls
- Do not gate on total historical drift; it will fail immediately in legacy repos
- `origin/main` may not exist in shallow/local-only clones; skip cleanly instead of hard failing
- A surviving evidence package with no prompt files is not necessarily drift; treat evidence as a valid replacement path when intended
- Use full-history checkout in CI (`fetch-depth: 0`) so `origin/main...HEAD` diffing works reliably
- Keep the markdown summary human-readable; reviewers need to see exactly which work item and prompt paths caused the failure

## Reusable outcome
This pattern works for any repo with ephemeral/generated prompt assets:
1. audit historical references
2. generate package index
3. define valid replacement evidence
4. fail only on newly introduced drift in CI and pre-push
