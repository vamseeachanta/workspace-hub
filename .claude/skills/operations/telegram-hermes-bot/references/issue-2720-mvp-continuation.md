# Issue #2720 multi-machine Telegram/Hermes MVP continuation note

Session-specific reference for the first multi-machine Telegram + Hermes dispatch/sync MVP. Use this only as historical implementation context; keep the class-level rules in `references/multi-machine-dispatch.md` authoritative.

## Proven useful implementation slice

A small, reviewable MVP can be split into these side-effect-separated artifacts:

- `scripts/telegram_dispatch/policy.py` — pure dispatch decision logic from request + gate evidence + host readiness + repo/lease state.
- `scripts/telegram_dispatch/redaction.py` — centralized public-output redaction before Telegram/GitHub/log/handoff surfaces.
- `scripts/readiness/telegram_hermes_readiness.py` — JSON readiness collector backed by the existing workstation registry.
- `scripts/readiness/telegram-hermes-readiness.sh` — thin wrapper that calls the Python collector through the repo's standard runner.
- `tests/telegram_dispatch/test_dispatch_policy.py`
- `tests/telegram_dispatch/test_redaction.py`
- `tests/readiness/test_telegram_hermes_readiness.py`

The workstation registry extension should live in `config/workstations/registry.yaml`; do not add a second Telegram host registry. Useful per-host metadata includes `telegram_hermes.dispatch_enabled`, `telegram_mode`, `hermes_profile`, `sync_policy`, `data_access_profile`, and readiness freshness thresholds.

## Documentation artifacts that complete the MVP

Do not call the code slice done until the durable operator docs/config examples exist or are explicitly deferred in the GitHub issue with approval:

- `docs/ops/telegram-hermes-multimachine-control-plane.md`
- `config/agents/hermes/telegram-multihost.example.yaml`
- `docs/ops/telegram-hermes-desktop-smoke-checklist.md`
- A pointer/update in the Telegram-Hermes skill/runbook so future operators discover the multi-machine reference.

## Continuation guardrail after tool-limit or context compaction

If a session stops mid-implementation, resume by revalidating the live repo state before writing more:

1. Check the issue gate/status and approval marker.
2. Inspect dirty/untracked files in the worktree.
3. Compare existing artifacts against the approved plan's artifact map.
4. Treat task-list state like `e3 in_progress` as provisional, not proof of completion.
5. Finish missing docs/config/skill pointers before validation.
6. Only then run targeted tests, legal/security scan, adversarial review, pathspec-limited commit, push, issue evidence comment, and closeout.

This prevents the common failure mode where a pure policy/readiness implementation is mistaken for the full Telegram multi-machine control-plane deliverable.

## Adversarial review handoff after interruption

If the interruption happens during code/artifact review, do **not** infer the review gate from earlier passing tests or from the mere existence of review files. Resume with a review-evidence inventory:

1. Re-open the current review artifacts and extract the final verdicts/findings, especially the tail of large provider outputs.
2. Treat provider outputs that contain only agent/config/loading errors as `UNAVAILABLE`, not as a successful review. Document the provider failure in the closeout trail if proceeding with a degraded review set.
3. Reconcile each review artifact against the live tracked diff. Stale artifacts may include files no longer modified in the current worktree; do not fix findings against an old diff without verifying applicability.
4. If a substantive review reports `MAJOR`, patch with TDD, rerun targeted tests, rerun legal/security scan, and refresh the review evidence before committing.
5. Keep generated `.planning/quick/*` review prompts/outputs untracked unless the issue plan explicitly requires them as durable artifacts.
6. If the tool-call/context limit fires before verdict synthesis, the final response must explicitly say the issue is **not closed**, name the incomplete gate, and provide the exact next command/checkpoint rather than implying closeout readiness.
