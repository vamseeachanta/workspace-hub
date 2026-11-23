# 2026-06-14 Email Queue Attention Exit Handoff

## Current state

Workspace-hub `main` contains the #2026 follow-up work for two-account email queue hygiene and assist-only attention routing.

Pushed commits:

- `bb4a801d895a761139f21ed37ee7f63daeaefd52` — `feat(email): emit attention route notifications`
- `1165bc33e551456ccfdb84e82607443c581e5067` — `docs(skills): preserve coordination fallback references`

Latest observed `origin/main` when this handoff was written:

- `bb1ced70a503da493ffac78e7bbd7d3a73ed1718` — `docs(plans): harden issue 1579 closeout criteria`

Issue comment posted for the #2026 follow-up:

- https://github.com/vamseeachanta/workspace-hub/issues/2026#issuecomment-4701529891

## What changed

- Added `scripts/email/email-queue-state.py notify-attention`.
- Added `scripts/email/state/notifications.py` to convert `pending_work_report()["attention_routes"]` into PII-safe `scripts/notify.sh` events.
- Added dev-primary schedule task `email-queue-attention-notify` at 05:57 UTC.
- Updated `docs/ops/scheduled-tasks.md`.
- Preserved two coordination skill reference docs that were previously untracked:
  - `.claude/skills/coordination/gh-work-planning-checklist/references/scope-guarded-repo-planning-fallback.md`
  - `.claude/skills/coordination/subagent-sandbox-limitations/references/gated-issue-batch-parallel-recon.md`

## Verification

For commit `bb4a801d8` after rebase:

- `UV_PROJECT_ENVIRONMENT=/tmp/codex-issue-2026-email-notify-venv uv run pytest tests/email/test_email_queue_state.py tests/email/test_email_queue_interfaces.py tests/email/test_email_queue_contract_artifacts.py tests/email/test_email_queue_operations.py -q` -> 47 passed
- `UV_PROJECT_ENVIRONMENT=/tmp/codex-issue-2026-email-notify-venv uv run python scripts/cron/validate-schedule.py` -> OK, 53 tasks
- `UV_PROJECT_ENVIRONMENT=/tmp/codex-issue-2026-email-notify-venv uv run python -m py_compile ...` -> pass
- `bash scripts/legal/legal-sanity-scan.sh --diff-only` -> pass
- `bash scripts/enforcement/check-no-abs-paths.sh <changed files>` -> pass
- `git diff --check` -> pass

For commit `1165bc33e`:

- `git diff --cached --check` -> pass
- `bash scripts/legal/legal-sanity-scan.sh --diff-only` -> pass
- `bash scripts/enforcement/check-no-abs-paths.sh <two reference docs>` -> pass

## Boundaries

- No Gmail archive/delete behavior was added.
- No live Telegram send was added.
- The new task writes local `logs/notifications/YYYY-MM-DD.jsonl` events through `scripts/notify.sh`.
- `skestates` remains assist-only/read-assisted with `keep_forever` retention.

## Known residue

The canonical `workspace-hub` checkout was observed on branch `parity/config-flip-3051` with unrelated dirty provider/config state after this work. Do not sweep or revert it as part of #2026 closeout.

Observed dirty files there:

- `.claude/state/session-signals/2026-06-12.jsonl`
- `.claude/state/session-signals/network-mounts.jsonl`
- `.claude/state/skill-scores.yaml`
- `config/agents/behavior-contract.yaml`
- `config/agents/model-registry.yaml`
- `config/agents/provider-capabilities.yaml`
- `scripts/ai/overnight-batch-planner.py`
- `scripts/ai/session-params.py`

Observed sibling worktree residue:

- `agent-worktrees/deckhand-206-family`

Task-local residue removed:

- `agent-worktrees/workspace-hub-2026-email-attention-notify`
- `/tmp/codex-issue-2026-email-notify-venv`
- recent pytest temp dirs created by the focused test run

## Next checkpoint

The next logical follow-up is not more Gmail mutation. It is the notification consumer path:

- [workspace-hub #1408](https://github.com/vamseeachanta/workspace-hub/issues/1408) — wire notification consumer so `logs/notifications` can surface to `/today`, desktop, or the Telegram/Hermes notification layer.

Start #1408 with discovery first. Confirm whether the latest `logs/notifications` consumer contract still says "no consumer" before implementing, and keep live Telegram delivery behind the venue/deckhand safety model.

## Suggested skills

- `github:github` — issue/repo orientation before starting #1408.
- `tdd` — any consumer implementation should add tests before code.
- `github:gh-fix-ci` — only if post-push checks fail.
- `handoff` and `coordination/pre-completion-cleanup-audit` — when preparing the next exit.
