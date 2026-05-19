# Multi-machine Telegram/Hermes readiness audit pattern

Use this reference when the user asks whether Telegram + Hermes can connect to all available machines, or what work remains to make multi-machine dispatch operational.

## Scope boundary

Do not equate "Hermes status says Telegram configured" with multi-machine dispatch readiness. Treat dispatch readiness as a stricter, fail-closed contract that must verify:

- the canonical workstation registry (`config/workstations/registry.yaml`), not an ad hoc host list;
- coordinator bot env gates and allowlist posture;
- gateway process health and single-poller ownership;
- systemd env-file loading and stop timeout posture;
- clean git/workspace state on dispatch-enabled hosts;
- host-local readiness evidence for remote dispatch workers;
- explicit status-only/not-onboarded classification for machines that are not dispatch targets.

## Readiness triage sequence

1. Load the Hermes and Telegram-Hermes skills/runbooks before answering.
2. Read the canonical registry and classify each host:
   - `dispatch_enabled: true` = must pass readiness before claiming dispatch works.
   - `dispatch_enabled: false` + `telegram_mode: desktop-status-only` = status/manual only, not a dispatch blocker.
   - `workspace_root: null` / `telegram_mode: disabled` = not onboarded.
3. Run the Telegram/Hermes readiness command from the repo, normally:
   - `scripts/readiness/telegram-hermes-readiness.sh`
   - and targeted `--host <host-id-or-hostname>` checks as needed.
4. Check local coordinator service health:
   - Hermes version/status;
   - `hermes-gateway.service` active state;
   - systemd unit/drop-in loads the env file;
   - `TimeoutStopSec` is compatible with gateway drain timeout;
   - logs do not show repeated Telegram `getUpdates` conflicts.
5. Inspect secret state only by key presence and file metadata:
   - verify env file mode/owner;
   - never print raw values;
   - report missing/unsafe key names only.
6. For remote dispatch workers, gather host-local evidence from that machine rather than reusing the coordinator's local env/workspace checks.
7. Report machine-by-machine status with four buckets: working, blocked dispatch, status-only, not onboarded.

## Common blockers to call out explicitly

- `GATEWAY_ALLOW_ALL_USERS=true` is a hard fail for mobile/dispatch readiness unless a separate approved multi-user security plan exists.
- Readiness-specific env names may differ from generic Hermes Telegram env names. If the readiness contract expects `TELEGRAM_HERMES_BOT_TOKEN` and `TELEGRAM_HERMES_ALLOWED_USER_IDS`, a generic `TELEGRAM_BOT_TOKEN` alone is not sufficient unless the code/runbook was intentionally updated to accept it.
- Multiple Telegram polling processes can cause `terminated by other getUpdates request`; resolve single-poller ownership before declaring the bot stable.
- `systemctl is-active hermes-gateway` is not enough. If `systemctl show hermes-gateway -p EnvironmentFiles` is empty or the drop-in is missing, report the gateway as active-but-not-hardened; do not infer durable token loading from process liveness.
- `TimeoutStopSec` below the Hermes gateway drain requirement is a hardening blocker even when the service is currently active, because restart/update paths can fail or hang under load. `systemctl show` may return human durations such as `1min` or `3min 30s`; parse those explicitly instead of treating non-numeric `TimeoutStopUSec` values as unavailable.
- Historical Telegram `getUpdates` conflicts can linger in `journalctl -n 200` on quiet services. Scope duplicate-poller checks to a recent window (for example `journalctl --since "30 minutes ago"`) so stale conflicts do not mask current single-poller readiness.
- A dirty worktree on a dispatch-enabled host is a readiness failure, not a cosmetic warning, because dispatch/sync must not start from ambiguous state.
- A remote worker should not be marked ready from coordinator-side checks alone; require fresh host-local evidence within the registry freshness threshold. If the remote workspace is stale or missing the readiness script, classify the host as blocked pending sync/install rather than guessing from SSH reachability.
- Registry entries that are `dispatch_enabled: false`, manual, or desktop-status-only are not failed dispatch hosts; classify them as status-only unless the user explicitly asks to promote them into dispatch targets.
- Closed implementation issues or passing unit tests do not prove live operational readiness.

## Recommended operator response shape

When reporting readiness, keep it short and evidence-oriented:

1. Current state: yes/no for multi-machine readiness.
2. Evidence: readiness command, registry classification, gateway/process observations.
3. Machine table: coordinator, workers, status-only hosts, not-onboarded hosts.
4. Blockers: ordered P0/P1/P2.
5. Recommended next action: fix coordinator safety first, then worker evidence, then optional onboarding.

## Safe remediation order

1. Harden the coordinator: remove allow-all, configure allowlist env gates, refresh systemd drop-in, clear stale timeout warning, ensure only one poller.
2. Clean/stash/commit the coordinator workspace and rerun targeted readiness.
3. Prepare each remote dispatch worker: update Hermes if needed, clean workspace, configure safe approval posture, generate host-local readiness evidence.
4. Rerun full readiness with evidence directory.
5. Only then perform Telegram mobile smoke tests and destructive-action canary tests.

Do not send test Telegram messages, rotate tokens, edit secrets, or kill gateway-like processes until the current process/service state is understood and the action scope is clear.