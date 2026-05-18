# Plan for #2738: Harden ace-linux-1 Telegram gateway as dispatch coordinator

> **Status:** draft
> **Complexity:** T2
> **Date:** 2026-05-18
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2738
> **Review artifacts:** pending

---

## Resource Intelligence Summary

### Existing repo code
- Found: `scripts/readiness/telegram_hermes_readiness.py` — collects host readiness from `config/workstations/registry.yaml`, fails closed on unsafe `GATEWAY_ALLOW_ALL_USERS`, missing Telegram allowlist/token env vars, dirty/ahead/behind git state, missing data roots, and missing remote evidence.
- Found: `scripts/readiness/telegram-hermes-readiness.sh` — CLI wrapper for the readiness collector.
- Found: `tests/readiness/test_telegram_hermes_readiness.py` — TDD coverage exists for allow-all-user rejection, remote evidence loading, host-local evidence generation, and redaction.
- Gap: No committed coordinator hardening verification script currently proves `hermes-gateway` has the durable systemd drop-in, env-file loading, compatible `TimeoutStopSec`, and no duplicate Telegram polling instances.

### Standards
- Not applicable — operational/Hermes control-surface hardening, not an engineering-calculation standards issue.

### LLM Wiki pages consulted
- No relevant wiki pages required; this is repo/runbook/control-plane operational work.

### Documents consulted
- Issue #2738 — scopes `ace-linux-1` as coordinator hardening target.
- `config/workstations/registry.yaml` — `dev-primary` maps to hostname `ace-linux-1`, `telegram_mode: coordinator`, `dispatch_enabled: true`, env pointers `TELEGRAM_BOT_TOKEN` and `TELEGRAM_ALLOWED_USERS`.
- `docs/ops/telegram-hermes-multimachine-control-plane.md` — recommends one coordinator bot on `dev-primary`, fail-closed dispatch gates, and minimum safe enablement path.
- `docs/runbooks/telegram-hermes-mobile.md` — documents token hygiene, systemd `EnvironmentFile=/home/vamsee/.hermes/.env`, `TimeoutStopSec=210`, approval guardrails, and destructive-action canary expectations.
- `operations/telegram-hermes-bot` skill — requires allowlist enforcement, no token exposure, approval gates for shell/file/destructive actions, and rollback/verification steps.

### Gaps identified
- Need coordinator preflight/hardening that can be run without printing secrets.
- Need durable systemd override verification: env file loaded fail-closed and stop timeout aligned with Hermes drain.
- Need duplicate Telegram polling detection; current logs have previously shown `getUpdates` conflicts.
- Need clean git/workspace gate before dispatch can be declared ready.
- Need a documented operator handoff for any secret/manual edits because bot tokens and allowlists cannot be committed or pasted into chat.

### Evidence (embedded verification)

**Issue statuses** (verified 2026-05-18T09:17:25Z via `gh issue view`):
- `#2738` — OPEN — `feat(hermes): harden ace-linux-1 Telegram gateway as dispatch coordinator`; labels include `status:needs-plan`.
- Parent `#2737` — OPEN — Linux/approved-machine dispatch umbrella; labels include `status:needs-plan`.

**Live readiness reproduction** (verified 2026-05-18T09:17:25Z):
```text
$ bash scripts/readiness/telegram-hermes-readiness.sh --host ace-linux-1
hosts.dev-primary.status = fail
hosts.dev-primary.dispatchable = false
failures:
- TELEGRAM_ALLOWED_USERS allowlist must be configured
- TELEGRAM_BOT_TOKEN bot token env var must be configured
- workspace_root has uncommitted or untracked git changes
```

**Live coordinator/service probe** (verified 2026-05-18T09:17:25Z; values redacted by key-presence only):
```text
Hermes Agent v0.14.0 (2026.5.16)
hermes-gateway: active, enabled
systemctl show hermes-gateway: TimeoutStopUSec=1min, MainPID=2104716
env_perms=600 vamsee:vamsee /home/vamsee/.hermes/.env
TELEGRAM_BOT_TOKEN_present=true
TELEGRAM_ALLOWED_USERS_present=true
GATEWAY_ALLOW_ALL_USERS_present=true
TELEGRAM_HERMES_BOT_TOKEN_present=false
TELEGRAM_HERMES_ALLOWED_USER_IDS_present=false
journalctl warning: Stale systemd unit detected: TimeoutStopSec=60s but drain_timeout=180s (expected >=210s)
```

**Line excerpts:**
```text
config/workstations/registry.yaml:34-40
telegram_hermes:
  dispatch_enabled: true
  telegram_mode: coordinator
  hermes_profile: default
  bot_token_env: TELEGRAM_BOT_TOKEN
  allowed_user_ids_env: TELEGRAM_ALLOWED_USERS
  sync_policy: pull-before-work-push-after-work
```

```text
docs/ops/telegram-hermes-multimachine-control-plane.md:149-153
Coordinator (`dev-primary`):
- Remove or unset `GATEWAY_ALLOW_ALL_USERS` from the local Hermes env store.
- Ensure `TELEGRAM_BOT_TOKEN` and `TELEGRAM_ALLOWED_USERS` are present only in the local secret store.
- Install/verify the systemd drop-in loads the env file and sets a gateway stop timeout compatible with Hermes restart drain.
- Clean or explicitly preserve/stash workspace-hub dirty state before dispatch.
```

**Reproduction proofs:**
- Reproduced at: 2026-05-18T09:17:25Z
- Failure mode observed matches issue claim: YES — coordinator exists and runs, but fails dispatch readiness due env exposure contract/systemd/worktree gates.

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-05-18-issue-2738-ace-linux-1-telegram-dispatch-coordinator.md` |
| Existing tests | `tests/readiness/test_telegram_hermes_readiness.py` |
| Implementation | `scripts/readiness/telegram_hermes_readiness.py`, optional new `scripts/operations/verify-hermes-gateway-coordinator.sh` |
| Docs/runbook | `docs/runbooks/telegram-hermes-mobile.md`, `docs/ops/telegram-hermes-multimachine-control-plane.md` |
| Local-only secret file | `/home/vamsee/.hermes/.env` — do not commit or print |
| Systemd drop-in | `/etc/systemd/system/hermes-gateway.service.d/override.conf` — local host config, verify only in repo unless user approves host edit |

---

## Deliverable

`ace-linux-1` is a safe **control-surface and notification coordinator** for the Linux orchestration MVP: local cron/GitHub issue labels drive work assignment, Hermes/Telegram provides status and approval-aware interaction, and direct Telegram-to-machine dispatch is explicitly deferred until the cron-backed workflow proves stable.

### Scope correction from live user guidance

Direct chat-driven dispatch is a far-shot target because it creates translation loss and too many safety hoops. This issue should harden `ace-linux-1` for:

1. daily priority/routing review on the control surface,
2. GitHub issue metadata assignment (`machine:*`, `agent:*`, priority/status labels),
3. local cron pollers that pick up only approved/eligible work,
4. progress comments back to GitHub,
5. Telegram status/notification only, not raw direct dispatch.

### Plan-review hardening: coordinator safety boundaries

- Coordinator hardening must enforce singleton behavior: exactly one active `hermes-gateway` Telegram polling instance after restart; duplicate `getUpdates` conflicts are a blocker, not a warning.
- Dirty shared checkout state is a hard blocker for automated work. The coordinator may report dirty state, but execution must use clean disposable per-issue worktrees or fail closed.
- Systemd changes require an explicit apply/verify sequence: write drop-in, `daemon-reload`, restart, verify loaded `EnvironmentFile`, verify `TimeoutStopSec>=210`, verify one active PID, and verify no recent duplicate-polling conflicts.
- Verification output must never dump raw env, raw `Environment=` values, full secret-bearing command lines, or unredacted journal excerpts.
- Direct Telegram task execution is disabled/deferred; mobile/Telegram is status and notification for the cron/GitHub-label orchestration MVP.

---

## Pseudocode

```text
function verify_coordinator():
    load registry dev-primary
    assert hostname/aliases resolve to local host
    inspect /home/vamsee/.hermes/.env metadata only
    assert TELEGRAM_BOT_TOKEN key exists and TELEGRAM_ALLOWED_USERS key exists
    assert GATEWAY_ALLOW_ALL_USERS is absent or false
    assert env file mode == 0600 and owner == vamsee:vamsee
    inspect hermes-gateway unit without printing env values
    assert EnvironmentFile=/home/vamsee/.hermes/.env is loaded
    assert TimeoutStopSec >= 210 seconds
    assert exactly one active hermes-gateway polling instance
    scan redacted recent journal for duplicate Telegram polling/getUpdates conflicts
    assert shared checkout clean, or execution path is disposable clean worktree only
    run readiness script for ace-linux-1
    require status pass for coordinator readiness
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create/modify | `tests/readiness/test_telegram_hermes_readiness.py` | Add regression coverage for coordinator env pointer behavior if missing. |
| Create | `scripts/operations/verify-hermes-gateway-coordinator.sh` | Secret-safe host-side coordinator verification; no token/allowlist values printed. |
| Modify | `docs/runbooks/telegram-hermes-mobile.md` | Add exact coordinator verification command/output contract if gaps are found. |
| Modify | `docs/ops/telegram-hermes-multimachine-control-plane.md` | Record coordinator readiness evidence contract if script shape changes. |
| Local/manual | `/home/vamsee/.hermes/.env` | Remove `GATEWAY_ALLOW_ALL_USERS=true` and confirm required keys are present; do not commit/print values. |
| Local/manual | `/etc/systemd/system/hermes-gateway.service.d/override.conf` | Ensure fail-closed env file and `TimeoutStopSec=210`; requires sudo/user-approved host edit. |

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_allow_all_users_is_readiness_failure` | Unsafe `GATEWAY_ALLOW_ALL_USERS=true` blocks dispatch | env has allow-all true | readiness `status=fail`, no secret values in output |
| `test_registry_env_pointer_names_are_honored` | Registry env pointer names drive checks | registry points to `TELEGRAM_BOT_TOKEN` / `TELEGRAM_ALLOWED_USERS` | missing/present checks use those exact names |
| `test_coordinator_verifier_redacts_env_values` | Host verifier prints key presence only | env file with token-like value | output does not contain token-like value |
| `test_coordinator_verifier_requires_timeout_stop_210` | Stale systemd timeout is detected | simulated `TimeoutStopUSec=1min` | verifier fails with actionable message |
| `test_coordinator_verifier_detects_duplicate_polling_conflict` | getUpdates conflict is surfaced | journal excerpt with conflict | verifier fails with duplicate-polling finding |
| `test_coordinator_verifier_requires_single_gateway_pid` | overlapping gateway/polling instances fail closed | two active gateway-like PIDs | verifier fails with singleton finding |
| `test_coordinator_verifier_does_not_dump_raw_journal_or_env` | verifier output is redacted and bounded | env/journal with token-like strings | output contains `[REDACTED]`, no raw values |

---

## Acceptance Criteria

- [ ] TDD added or existing readiness tests explicitly cover env pointer names, allow-all failure, redaction, and host-local evidence behavior.
- [ ] `uv run pytest tests/readiness/test_telegram_hermes_readiness.py -v` passes.
- [ ] Host verification confirms `/home/vamsee/.hermes/.env` mode `600`, owner `vamsee:vamsee`, and only key-presence output is emitted.
- [ ] `GATEWAY_ALLOW_ALL_USERS` is false/unset on `ace-linux-1`.
- [ ] `hermes-gateway` systemd configuration loads `/home/vamsee/.hermes/.env` fail-closed and has `TimeoutStopSec>=210`.
- [ ] Recent gateway logs show no duplicate polling/getUpdates conflicts after restart.
- [ ] `bash scripts/readiness/telegram-hermes-readiness.sh --host ace-linux-1` reports `status=pass` for coordinator readiness.
- [ ] Workspace-hub on `ace-linux-1` is clean and synced before cron/control-surface enablement is declared.
- [ ] Coordinator verification proves exactly one active gateway/polling PID after restart.
- [ ] Any automated execution uses a clean disposable per-issue worktree or fails closed; dirty shared checkout is never used.
- [ ] Systemd rollout procedure includes `daemon-reload`, restart, loaded-property verification, singleton PID verification, and redacted log check.
- [ ] `ace-linux-1` has a documented daily control-surface routine for ranking issues and applying `machine:*` / `agent:*` labels.
- [ ] Direct Telegram-to-machine dispatch remains disabled/deferred until cron/GitHub-label orchestration is separately proven and approved.

---

## Adversarial Review Summary

Initial review found MINOR issues: singleton polling prevention, dirty checkout policy, systemd rollout verification, and redaction scope needed to be explicit. The plan was hardened to require one active gateway/polling PID, clean disposable worktrees or fail-closed behavior, redacted verification output, and a concrete systemd apply/verify sequence.

Follow-up ops/security review: **APPROVE** for plan-review readiness.

---

## Risks and Open Questions

- **Risk:** Editing `/home/vamsee/.hermes/.env` or systemd requires host-side side effects; do not perform without explicit user approval and token-handling discipline.
- **Risk:** Current gateway may already be usable for chat but not safe for dispatch because readiness loads environment from the current process while systemd may be using a different env source.
- **Risk:** Duplicate Telegram polling can make bot behavior flaky even if readiness metadata passes.
- **Open:** Should the coordinator verification script be repo-owned shell, Python, or `hermes gateway doctor` upstream contribution? Recommended: repo-owned shell wrapper now, upstream later if reused.

---

## Complexity: T2

**T2** — operational host hardening plus TDD/readiness script coverage; limited implementation surface, but requires secret hygiene and systemd verification.
