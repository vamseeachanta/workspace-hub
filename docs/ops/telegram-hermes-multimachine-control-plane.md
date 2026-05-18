# Telegram + Hermes multi-machine control plane

> Issue: [#2720](https://github.com/vamseeachanta/workspace-hub/issues/2720)
> Status: MVP contract and runbook. Telegram is the command/notification plane only; GitHub, git refs, and repo artifacts remain canonical state.

## Recommendation

Use **one coordinator Telegram bot on `dev-primary` (`ace-linux-1`) for the MVP**. It will read `config/workstations/registry.yaml`, report per-host readiness, and dispatch only when GitHub issue gates and git synchronization gates pass.

Linux cron/GitHub-label orchestration is the MVP for unattended Linux background work. Telegram/Hermes is status and notification surface for this phase; direct Telegram-to-machine dispatch remains deferred until separately planned, reviewed, and approved.

Ranked options:

1. **Coordinator bot on `dev-primary` — recommended MVP**
   - Lowest operator confusion: one chat, one allowlist, one command surface.
   - Keeps lease creation centralized while still allowing worker hosts through registry routing.
   - Blast radius is controlled by allowlist, fail-closed readiness, host disable flags, and token rotation.
2. **Per-host bot profiles**
   - Better isolation after MVP, but creates more token rotation and chat routing overhead.
   - Use only after host readiness and lease semantics are proven.
3. **Telegram Desktop manual status on every machine**
   - Useful for Windows/macOS operator visibility.
   - Not acceptable as an unattended dispatch mechanism because it is not canonical state.

## Canonical state model

| Surface | Role | Canonical? |
|---|---|---|
| Telegram chat | Operator command input and short status notifications | No |
| GitHub issue labels/comments | Workflow gate and human-visible lease mirror | Yes for issue state; comments mirror lease evidence |
| Git remote ref `refs/heads/dispatch/leases/<issue>-<mode>` | Atomic dispatch lease | Yes |
| `config/workstations/registry.yaml` | Machine identity, capabilities, dispatch posture, data-access profile | Yes |
| `.planning/plan-approved/<issue>.md` | Local user-approval marker paired with GitHub `status:plan-approved` | Yes |
| Local JSONL/job logs | Audit/cache only | No |

## Supported commands

### `/status [--host host|auto]`

Reports registry-derived readiness without exposing secrets.

Required output fields:

- `host_id`, hostname, role, OS, workspace root.
- Telegram/Hermes posture: coordinator, worker, desktop-status-only, disabled.
- Dispatchability: pass/warn/fail/status-only/not-onboarded.
- Git/repo state: dirty, ahead, behind, missing root, missing `AGENTS.md`.
- Data access: repos, storage roots, remote mounts, freshness thresholds.
- Security: allowlist configured, `GATEWAY_ALLOW_ALL_USERS` false/unset, token values redacted.

### `/dispatch <issue> [--mode plan|implementation] [--host host|auto]`

Translates a Telegram request into a gated GitHub/repo-backed job decision.

Fail-closed gates:

1. Resolve issue through `gh`/GitHub. No GitHub authority means no dispatch.
2. For `--mode implementation`, require both:
   - GitHub label `status:plan-approved`.
   - Local marker `.planning/plan-approved/<issue>.md`.
3. For `--mode plan`, allow only `status:needs-plan` or `status:plan-review` issues.
4. Select host from `config/workstations/registry.yaml`; status-only hosts cannot execute.
5. Block dirty worktrees, ahead/behind branches, missing data access, stale readiness, unreachable hosts, or unsafe gateway config.
6. Create or renew the Git remote-ref lease. The non-forced push result is the atomic winner/loser arbiter.

Lease rules:

```text
lease_ref = refs/heads/dispatch/leases/<issue>-<mode>
idempotency_key = <issue>:<mode>:<host_id>
```

- New lease: create an empty lease commit parented to current `origin/main`; push without force to `lease_ref`.
- Expired lease renewal: create a successor empty lease commit parented to the current lease-ref tip; push without force. Rejection means another host won.
- GitHub issue comments mirror the winning lease and job/log pointers for humans; comments are not the lock.

### `/jobs`

Lists active dispatch leases and recent job evidence:

- Lease ref.
- Issue URL.
- Host ID.
- Mode.
- Job/log artifact path.
- Age/expiry status.

### `/sync [--host host|auto]`

Runs non-destructive synchronization discovery first.

Rules:

1. Verify host identity and repo root match `config/workstations/registry.yaml`.
2. Run fetch/status discovery.
3. If dirty, ahead, behind with conflicts, or missing upstream: stop and report blocker.
4. If clean: `git pull --ff-only` only.
5. Refresh repo-backed Hermes/skill/config paths.
6. Re-run readiness smoke and report evidence.

## Host dispatch posture

| Host ID | MVP posture | Reason |
|---|---|---|
| `dev-primary` | Coordinator + dispatchable | Primary Linux control plane, workspace-hub source of truth, broad data access. |
| `dev-secondary` | Worker dispatchable after readiness | Linux OSS simulation worker with reachable SSH and repo-backed sync. |
| `licensed-win-1` | Desktop/status-only | Licensed solver host; no unattended dispatch until Windows Hermes/gateway parity is proven. |
| `licensed-win-2` | Desktop/status-only | Same as `licensed-win-1`. |
| `macbook-portable` | Manual/status-only | Portable/manual machine, no unattended Linux cron/control-plane dependency. |
| `gali-linux-compute-1` | Not onboarded | GPU node lacks workspace/repo/Hermes setup. |

## Security and token handling

- Store Telegram bot tokens and gateway credentials only in local secret stores such as `~/.hermes/.env`; never commit them.
- Dispatch-enabled host records must point to the local secret env var names via `telegram_hermes.bot_token_env` and `telegram_hermes.allowed_user_ids_env`; the committed registry stores names only, never values.
- For the current MVP, `dev-primary` and `dev-secondary` use the existing Hermes Telegram env names: `TELEGRAM_BOT_TOKEN` and `TELEGRAM_ALLOWED_USERS`.
- `GATEWAY_ALLOW_ALL_USERS=true` is a readiness failure for this MVP.
- Missing allowlist evidence is a readiness failure for dispatch.
- Status/log output must redact token-like values, API keys, password fields, and credential fields.
- A compromised host can be disabled by setting `telegram_hermes.dispatch_enabled: false` in `config/workstations/registry.yaml`, committing/pushing the change, and rotating the relevant local token.

## Token rotation

1. Disable the affected host in `config/workstations/registry.yaml` if there is any risk of active compromise.
2. Rotate the bot token with BotFather or the gateway provider.
3. Update only the local secret store (`~/.hermes/.env` or host-specific secret manager).
4. Restart Hermes/gateway on the coordinator host.
5. On the target machine, generate host-local readiness evidence into a shared/synced evidence directory, then run the coordinator check with that directory:
   ```bash
   scripts/readiness/telegram-hermes-readiness.sh --host <host_id> --evidence-dir <evidence_dir>
   ```
   Without `--evidence-dir`, remote dispatch hosts intentionally fail closed with `host-local-readiness-evidence` missing.
6. Re-enable dispatch only after readiness is `pass` and the worktree is clean/synced; `warn` is status-only and is not dispatch-eligible.

## Rollback

Fast rollback for unsafe behavior:

```text
1. Stop the Telegram gateway/Hermes listener on the affected host.
2. Set telegram_hermes.dispatch_enabled=false for that host.
3. Commit and push the registry change.
4. Revoke or rotate the bot token if command spoofing or leakage is suspected.
5. Leave existing Git lease refs intact as evidence; do not force-delete them during incident triage.
```

## Minimum safe enablement path

Current MVP target is **dispatch only on `dev-primary` and `dev-secondary`**. Windows/macOS machines remain status-only until a separate approved plan proves host-local Hermes gateway parity, approval posture, and safe job execution.

1. Coordinator (`dev-primary`):
   - Remove or unset `GATEWAY_ALLOW_ALL_USERS` from the local Hermes env store.
   - Ensure `TELEGRAM_BOT_TOKEN` and `TELEGRAM_ALLOWED_USERS` are present only in the local secret store.
   - Install/verify the systemd drop-in loads the env file and sets a gateway stop timeout compatible with Hermes restart drain.
   - Run `scripts/operations/verify-hermes-gateway-coordinator.sh` on the coordinator; it must pass without printing token or allowlist values.
   - Clean or explicitly preserve/stash workspace-hub dirty state before dispatch.
2. Worker (`dev-secondary`):
   - Sync workspace-hub to a revision that includes `scripts/readiness/telegram-hermes-readiness.sh` and this runbook.
   - Install Hermes CLI/gateway if missing; keep approval mode safe (`manual` or reviewed `smart`, never unguarded destructive execution).
   - Configure the same env-name contract locally (`TELEGRAM_BOT_TOKEN`, `TELEGRAM_ALLOWED_USERS`) without committing values.
   - Generate host-local readiness evidence and make it available to the coordinator via `--evidence-dir`.
3. Status-only machines (`licensed-win-1`, `licensed-win-2`, `macbook-portable`):
   - Keep `dispatch_enabled: false`.
   - Use Telegram Desktop/manual smoke checks only; do not route unattended work there until a Windows/macOS dispatch plan is approved.
4. Not-onboarded machines (`gali-linux-compute-1`):
   - Add workspace root, repo sync, Hermes install, network reachability, and host-local readiness before considering Telegram/Hermes connection.

Full dispatch readiness is declared only when `scripts/readiness/telegram-hermes-readiness.sh --evidence-dir <dir>` reports `pass` for every `dispatch_enabled: true` host.

## Manual desktop smoke checks

Telegram Desktop UX across Linux, Windows, and macOS is manual evidence for MVP. Use:

- `docs/ops/telegram-hermes-desktop-smoke-checklist.md`

## Existing dispatch infrastructure stance

- `scripts/ai/provider-dispatch-loop.py` has useful leader/lease/idempotency patterns, but provider routing is not the Telegram machine dispatcher.
- `scripts/ai/task-dispatcher.py` can inform capability/provider scoring, but it is not a job launcher.
- `scripts/operations/workstation-dispatch.sh` and `scripts/coordination/routing/lib/agent_dispatcher.sh` remain local dispatch helpers.
- Dated `scripts/dispatch/overnight-*` lane scripts are historical execution artifacts and must not become the Telegram command API.
