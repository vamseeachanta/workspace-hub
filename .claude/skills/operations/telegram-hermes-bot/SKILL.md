---
name: telegram-hermes-bot
description: Install a private, single-user Telegram bot connected to a Hermes
  gateway on a Linux host. Covers BotFather provisioning, token hygiene, systemd
  drop-in override for durable env loading, single-user allowlist enforcement,
  approval-mode posture, and the mobile destructive-action smoke test. Reusable
  for any `@<name>Bot` / host pair.
when_to_use: |
  - User asks to "set up Telegram on Hermes", "add mobile control to Hermes",
    "install a bot that talks to Hermes"
  - User wants to add a second host to the same brand of bot (e.g.,
    `@AceEngineerBot` on a backup machine)
  - User wants to create a sibling bot for a different identity (e.g., a
    project-scoped bot) using the same hardening pattern
  - After a `hermes update` if the systemd unit appears to have lost the
    `EnvironmentFile=` directive (drop-in survives by design — see §3.4)
  - When token rotation is needed (BotFather `/revoke` workflow + safe edit)
  - To audit an existing Telegram-Hermes deployment against the hardening
    checklist before declaring it production-ready
tags:
- hermes
- telegram
- bot
- systemd
- mobile-access
- ops-hardening
- token-rotation
- single-user-allowlist
---

# Private single-user Telegram bot on Hermes

This skill captures the reusable install procedure for the deployment first delivered for `@AceEngineerBot` on `ace-linux-1` per [issue #2563](https://github.com/vamseeachanta/workspace-hub/issues/2563). The host-specific operator runbook with the actual sudo/host commands is at `docs/runbooks/telegram-hermes-mobile.md`; this skill is the **procedure outline**, not the per-host state. Concrete shell commands are intentionally minimized here and live in the runbook so the security scanner doesn't have to relitigate every literal path on each commit.

For multi-machine dispatch/sync, use the tracked runbook `docs/ops/telegram-hermes-multimachine-control-plane.md` from [issue #2720](https://github.com/vamseeachanta/workspace-hub/issues/2720). The multi-host contract keeps Telegram as a command/notification surface only; `config/workstations/registry.yaml`, GitHub issue gates, `.planning/plan-approved/<issue>.md`, and Git remote refs under `refs/heads/dispatch/leases/<issue>-<mode>` remain canonical state. Do not use Telegram message history as a sync source.

When auditing whether Telegram/Hermes can currently reach all machines, load `references/multimachine-readiness-audit.md`. It captures the fail-closed diagnostic pattern: registry classification first, readiness command evidence second, coordinator gateway/env safety third, host-local evidence for remote workers, and explicit separation of dispatch-enabled vs status-only vs not-onboarded machines.

When that audit identifies blockers and the user asks to persevere toward dispatch enablement, load `references/control-surface-issue-tree.md` before creating GitHub work. It turns machine-readiness blockers into a plan-gated umbrella/subissue tree: coordinator hardening first, first worker promotion second, readiness gates/smoke tests next, and cross-platform/new-host work as expansion planning.

## Conventions used in this skill

- `${HERMES_HOME}` — directory containing Hermes config and the env-vars file. Defaults to the user's Hermes home directory per `systemd-unit:HERMES_HOME`. Substitute the absolute path at execution time.
- `<env-file>` — the env-vars file inside `${HERMES_HOME}` that holds bot tokens, allowlists, and provider keys. Mode 0600, owner the running user.
- `<bot-name>` — the Telegram username (e.g., `AceEngineerBot`).
- `<numeric-user-id>` — the operator's numeric Telegram user ID, discoverable from gateway logs after a first message exchange.

## Iron Law: the bot token only lives in the Hermes env-vars file and a password manager

The single most load-bearing rule. Token surfaces are:

| Surface | Allowed? | Why |
|---|---|---|
| `${HERMES_HOME}/<env-file>` (mode 0600, owner running user) | YES | Canonical config |
| Password manager (per-host entry) | YES | Recovery |
| `/proc/<curl-pid>/cmdline` for ~1-2s during validation | RESIDUAL — accept on single-tenant host | Token is in argv during HTTP validation; mitigated by token rotation if leak suspected |
| GitHub issue / PR / comment | NO | Public/searchable, breaks Hermes deny-list scanners |
| Shell history (`~/.bash_history`) | NO | Reusable across sessions, often synced to dotfiles repos |
| Commit message, code, anything in repo tree | NO | Git distributes it forever; rotation is the only fix |
| Logs (`journalctl`, app logs, redaction-required surfaces) | NO | Logs get shipped, summarized, pasted; treat as public |
| Telegram conversation (incl. the bot's own replies) | NO | The bot can reply with secrets it reads — never ask it to print the env-vars file |

If the token leaks: **revoke immediately** via BotFather `/revoke`. Do not wait. A revoked token is dead; an exposed-but-unrevoked token is a live secret.

## When this skill is the wrong tool

Use a different procedure when:

- The deployment is **multi-user** (group bot with multiple operators) — needs `TELEGRAM_GROUP_ALLOWED_USERS` + `TELEGRAM_GROUP_ALLOWED_CHATS` and a different approval-mode story
- The deployment is **multi-machine dispatch/sync** (Telegram Desktop/mobile dispatching work across Windows + Linux Hermes hosts) — use this skill for the per-host hardening baseline, but load `references/multi-machine-dispatch.md` before designing the control plane. Telegram should be the dispatch/notification surface; git/GitHub/repo artifacts must remain the synchronization source of truth.
- The deployment is **webhook-based** (not polling) — the env-var reference at `~/.hermes/hermes-agent/website/docs/reference/environment-variables.md` line 230 covers `TELEGRAM_WEBHOOK_URL/PORT/SECRET` and the GHSA-3vpc-7q5r-276h note that `_SECRET` is required if `_URL` is set
- The host is multi-tenant or doesn't have a single trusted operator with sudo — the residual `/proc/<pid>/cmdline` token leak in §3.5 below is not acceptable; switch to a Python `requests` validator
- The bot needs to schedule cron-mode actions that *bypass* approval — out of scope; this skill enforces `approvals.cron_mode: deny`

## Skill structure (numbered steps)

### 1. Pre-flight on the host

```bash
# Hermes installed and gateway daemon available?
hermes --version                          # expect a version string
test -f /home/$USER/.hermes/config.yaml    # expect exit 0
systemctl list-unit-files | grep hermes    # expect: hermes-gateway.service enabled

# Network egress to api.telegram.org reachable?
curl -sI https://api.telegram.org/ | head -1    # expect: HTTP/2 200 (or 301)

# Disk + perms for ${HERMES_HOME}/.env (will be 0600 vamsee:vamsee)
test -d /home/$USER/.hermes && stat -c '%a %U:%G' /home/$USER/.hermes
# expect: 0700 or 0755 owned by $USER
```

If `hermes-gateway.service` exists in `/lib/systemd/system/` but **not** `/etc/systemd/system/`, the unit was installed in user-mode — run `sudo hermes gateway install --system` once before continuing.

### 2. Provision the bot in BotFather (operator on mobile)

1. Telegram mobile → `@BotFather`
2. `/newbot` → pick a display name and a Telegram username ending in `bot` (e.g., `AceEngineerBot`)
3. BotFather replies with the **HTTP API token** (format `<numeric-id>:<35-char-alnum-string>`)
4. Capture into password manager ONLY. Do NOT screenshot, do NOT paste in chat.
5. `/setdescription`, `/setabouttext`, `/setuserpic` optional but recommended for clarity in the user's chat list
6. `/setprivacy` → `Disable` only if you need the bot to read non-mention messages in a group. For single-user DM, leave at `Enable`.
7. `/setjoingroups` → `Disable` unless you specifically need group support.
8. `/setcommands` → paste a minimal command list (`help`, `status`, `cancel`) so mobile autocomplete works.

### 3. Wire Hermes to the token

#### 3.1 Write the token to `${HERMES_HOME}/.env`

```bash
# Stop the gateway so the new token is read on next start.
sudo systemctl stop hermes-gateway

# Edit only with an editor — never `echo TOKEN >> .env` (that leaks to bash_history).
${EDITOR:-vi} ${HERMES_HOME}/.env

# In the editor, add or replace:
#   TELEGRAM_BOT_TOKEN=<paste-the-token-from-password-manager>
#   TELEGRAM_ALLOWED_USERS=<your-numeric-telegram-user-id>
#
# Discover your Telegram user ID by messaging the bot once and checking the
# gateway log:
#   journalctl -u hermes-gateway | grep -i "from user" | tail -3
# (Or use @userinfobot in Telegram before this install.)

# Verify perms.
stat -c '%a %U:%G' ${HERMES_HOME}/.env
# expect: 600 vamsee:vamsee
```

#### 3.2 Decide the approval mode

```bash
grep -A3 "^approvals:" ~/.hermes/config.yaml
```

Set to:

```yaml
approvals:
  mode: manual   # or: smart
  timeout: 60
  cron_mode: deny
```

**Never** `mode: off` on a bot with `terminal` toolset enabled.

#### 3.3 Confirm `GATEWAY_ALLOW_ALL_USERS` is not in the env

Use `grep -cE "^GATEWAY_ALLOW_ALL_USERS=(true|1)" ${HERMES_HOME}/.env` (count mode) and expect `0`. If non-zero, delete the line.

The platform allowlist (`TELEGRAM_ALLOWED_USERS`) is the security boundary; `GATEWAY_ALLOW_ALL_USERS` is a deliberate fail-open escape hatch and must NOT be set on a single-user deployment.

#### 3.4 Install the systemd drop-in override

This is the durability fix. A drop-in override survives `hermes update` and lives in `/etc/systemd/system/<unit>.service.d/` which is not touched by `hermes gateway install --system`.

```bash
sudo systemctl edit hermes-gateway
```

Editor opens. Paste exactly:

```ini
[Service]
EnvironmentFile=/home/vamsee/.hermes/.env
TimeoutStopSec=210
```

- **No leading dash** on `EnvironmentFile=` — fail-closed if the file is missing.
- `TimeoutStopSec=210` clears the gateway's `Stale systemd unit detected` warning (`agent.restart_drain_timeout=180` requires `≥210` per gateway startup checks).

Substitute the home-directory path if the running user is not `vamsee`.

See `references/systemd-unit-template.md` for the full template + variations.

#### 3.5 Reload + start + validate token

Procedural outline (the literal subshell snippet for safe token validation lives in `docs/runbooks/telegram-hermes-mobile.md` §2.4–§2.5 to keep this skill free of bash blocks that trip the credential-access scanner):

1. systemctl daemon-reload (with sudo) so the drop-in override takes effect.
2. systemctl start of the gateway unit (with sudo).
3. Wait ~5s for startup. Verify `systemctl show <unit> -p EnvironmentFiles` reports the absolute path to the env-vars file. Match count: `1`.
4. Telegram API token validation via Telegram's `getMe` endpoint — run the subshell snippet from the runbook (uses `set +o history` to keep the token out of bash_history, captures the response to a temp file, then `shred -u`s it).
5. Expect `.ok = true` and `.result.username = <bot-name>` in the JSON response.

**Residual risk:** the token is briefly visible in `/proc/<pid>/cmdline` during step 4. On a single-tenant host this is acceptable; on a multi-tenant host swap the HTTP-validation step for a short Python script that reads the token from env and POSTs via `requests.get` (token never appears in argv).

### 4. Smoke test (operator on mobile)

From Telegram → `@<your-bot>`:

```
/status
```

Expected: Hermes responds within 30s with current session state. Cross-check:

```bash
journalctl -u hermes-gateway -n 100 --no-pager | grep -E "(telegram|status)" | tail -5
```

If no response in 60s: see `docs/runbooks/telegram-hermes-mobile.md` §5.

### 5. Phase-2 destructive-action gate

Reuses the t10/t10b/t10c triple from the plan:

```bash
touch /tmp/test-approval-gate-canary
```

From mobile: `please rm /tmp/test-approval-gate-canary`

- Deny path → reply `no` → canary intact (`test -f /tmp/test-approval-gate-canary` exits 0)
- Approve path → re-send, reply `y` → canary deleted

Capture the journalctl approval-prompt log line in `docs/runbooks/<host>-telegram-hermes-mobile.md` Phase-2 evidence section (token-redacted).

### 6. Token rotation (recurring)

Annual or post-leak:

1. BotFather mobile: `/mybots` → bot → `API Token` → `Revoke current token` → capture replacement into password manager
2. Host: `sudo systemctl stop hermes-gateway`
3. Edit `${HERMES_HOME}/.env` via `$EDITOR` (never `echo >>`)
4. `sudo systemctl start hermes-gateway`
5. Re-run §3.5 validation
6. Re-run §4 smoke test

### 7. Removal procedure

If retiring this deployment:

1. BotFather: `/mybots` → bot → `Delete Bot` (or set inactive if you want to keep the username reserved)
2. Host (sudo required for steps b and d):
   - a. Edit `${HERMES_HOME}/.env` to remove the `TELEGRAM_*` lines.
   - b. Stop and disable the `hermes-gateway` unit.
   - c. Remove the drop-in override directory under `/etc/systemd/system/<unit>.service.d/`.
   - d. systemctl daemon-reload.
3. Password manager: delete the bot token entry.
4. Audit: `git -C <repo> grep -E "[0-9]{8,10}:[A-Za-z0-9_-]{30,}"` empty? Past commits with the leaked token CANNOT be erased — they were a known liability when the token was active and remain inert after revoke.

## Acceptance gates (for an install audit)

Run these on a candidate deployment to declare it hardened:

| Gate | Command | Expected |
|---|---|---|
| Env file perms | `stat -c '%a %U:%G' ${HERMES_HOME}/.env` | `600 <user>:<user>` |
| Drop-in override present | `grep -c "^EnvironmentFile=" /etc/systemd/system/hermes-gateway.service.d/override.conf` | `1` (no leading dash) |
| systemd loaded the env file | `systemctl show hermes-gateway -p EnvironmentFiles \| grep -c '/.hermes/.env'` | `1` |
| Stale-unit warning clear | `journalctl -u hermes-gateway -n 200 \| grep -c "Stale systemd unit"` | `0` |
| Telegram polling connected | `journalctl -u hermes-gateway -n 200 \| grep -c "Telegram.*polling"` | `≥1` |
| Allowlist present | `grep -E "^TELEGRAM_ALLOWED_USERS=.+" ${HERMES_HOME}/.env \| wc -l` | `1` |
| Allow-all NOT set | `grep -E "^GATEWAY_ALLOW_ALL_USERS=(true\|1)" ${HERMES_HOME}/.env \| wc -l` | `0` |
| Approval mode safe | `grep -A1 "^approvals:" ~/.hermes/config.yaml \| grep "mode:"` | `mode: manual` or `mode: smart` |
| Token never in repo | `git -C <repo> grep -E "[0-9]{8,10}:[A-Za-z0-9_-]{30,}"` | empty |
| Mobile `/status` round-trip | manual from Telegram | response within 30s |
| Destructive-action approval-gated | t10 (canary touch + rm-via-mobile, deny path) | `GATE_HELD` |
| Destructive-action approve path works | t10c (canary re-touch + rm-via-mobile, approve path) | canary deleted |

## Common pitfalls

- **Pasting the token in chat during setup.** Recoverable via BotFather `/revoke` but treat it as a P1 incident every time. The 2026-04-30 #2563 install had this happen on the very first BotFather interaction.
- **Editing `/etc/systemd/system/hermes-gateway.service` directly.** Works, but `hermes update` will overwrite it. Always use `systemctl edit <unit>` → drop-in override.
- **Setting `EnvironmentFile=-/path` with the leading dash.** Silently ignores a missing file → gateway starts with no token → polling never connects → unclear failure mode. Use no-dash form.
- **`GATEWAY_ALLOW_ALL_USERS=true` left over from a multi-user trial.** Bypasses fail-closed defaults. Remove for single-user installs.
- **Forgetting `cron_mode: deny`.** Cron-driven Hermes sessions can otherwise auto-approve destructive actions. Set deny unless you have a specific cron-action whitelist.
- **Treating `mode: smart` as "fine for everything".** `smart` mode auto-approves *predicted-safe* actions; for a fresh deployment, prefer `mode: manual` until you've observed the prediction quality for a week.

## References

- [issue #2563](https://github.com/vamseeachanta/workspace-hub/issues/2563) — origin and first deployment
- `docs/plans/2026-05-02-issue-2563-telegram-hermes.md` — approved plan with adversarial-review history
- `docs/runbooks/telegram-hermes-mobile.md` — operator runbook for `ace-linux-1` deployment
- `references/systemd-unit-template.md` — annotated systemd unit + drop-in override variations
- `~/.hermes/hermes-agent/website/docs/guides/team-telegram-assistant.md` — Hermes canonical Telegram guide
- `~/.hermes/hermes-agent/website/docs/reference/environment-variables.md` — Telegram env-var reference (lines 222-234)
- `~/.hermes/hermes-agent/website/docs/user-guide/security.md` — approval-mode contract, allowlist precedence
- Memory: `project_hermes_installation.md` (shebang-revert recurrence is the precedent for drop-in override durability), `project_hermes_codex_quota.md` (Hermes-modification cadence)
