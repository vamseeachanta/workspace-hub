# Telegram Hermes Mobile Access Handoff — 2026-04-30

Generated: 2026-04-30 12:11 CDT  
Repo issue: https://github.com/vamseeachanta/workspace-hub/issues/2563  
Bot: `@AceEngineerBot` / https://t.me/AceEngineerBot

## Executive summary

Telegram-based mobile/desktop access to Hermes is functional on ace-linux-1.

Confirmed working:
- Telegram Desktop installed and running from `/home/vamsee/.local/share/Telegram/Telegram`.
- Hermes gateway systemd service is running as `vamsee`.
- Telegram platform is connected in polling mode.
- Single-user Telegram allowlist is configured via `TELEGRAM_ALLOWED_USERS` in `/home/vamsee/.hermes/.env`.
- `/help` command responded successfully.
- Direct bot delivery test succeeded.
- Inbound natural-language Telegram messages reached Hermes and received responses.

Do **not** paste, commit, or preserve token values. The initial BotFather token was exposed in chat and must still be rotated.

## Evidence captured

### Telegram Desktop

Process was running:

```text
2049078 /home/vamsee/.local/share/Telegram/Telegram
```

Executable verified:

```text
/home/vamsee/.local/share/Telegram/Telegram
```

Installer script created and executed:

```text
/home/vamsee/Downloads/install-telegram-desktop.sh
```

### Hermes gateway

Service status evidence:

```text
hermes-gateway.service active (running)
Main command: /home/vamsee/.hermes/hermes-agent/.venv/bin/python -m hermes_cli.main gateway run --replace
Configured to run as: vamsee
System service starts at boot without requiring systemd linger
```

Known warning still present:

```text
⚠ Installed gateway service definition is outdated
Run: sudo hermes gateway restart --system
```

Sudo was not available non-interactively earlier, so systemd unit refresh was not completed.

### Telegram bot/gateway logs

Connection evidence:

```text
[Telegram] Connected to Telegram (polling mode)
✓ telegram connected
```

`/help` smoke test evidence:

```text
[Telegram] Sending response (4181 chars) to <allowlisted Telegram ID>
```

Desktop delivery test evidence:

```json
{
  "ok": true,
  "message_id": 6,
  "chat_type": "private"
}
```

Inbound desktop/mobile workflow evidence:

```text
inbound message: platform=telegram user=Vamsee Achanta chat=<allowlisted Telegram ID> msg='desktop received'
response ready: platform=telegram chat=<allowlisted Telegram ID> time=92.4s api_calls=1 response=9 chars
[Telegram] Sending response (9 chars) to <allowlisted Telegram ID>
```

Later natural-language orchestration prompts also reached Hermes and received responses:

```text
msg='How can we coordinate or orchestrate work from here?'
response=3895 chars

msg='A'
response=5613 chars

msg='B1'
response=3917 chars

msg='1 then 2'
response=2297 chars

msg='Continue with recommendations'
response=3146 chars
```

## Current task-list state

Completed:
- `tg-01` — selected Telegram bot via BotFather as interaction mode.
- `tg-03` — selected private single-user bot access mode.
- `tg-04` — configured Telegram gateway token, discovered user ID, configured `TELEGRAM_ALLOWED_USERS`, restarted/reconnected gateway.
- `tg-08` core smoke tests are effectively passing: `/help`, direct delivery, inbound natural-language prompts, and desktop confirmation all worked.

Pending / needs follow-up:
- `tg-02a` — rotate/revoke the exposed BotFather token and update `/home/vamsee/.hermes/.env` with the new token.
- `tg-05` — explicitly review mobile toolset exposure and approval mode.
- `tg-06` / `tg-07` — refresh outdated systemd gateway unit with sudo and ensure durable environment loading.
- `tg-09` — document guardrails: allowed-users only, no secrets over Telegram, manual/smart approvals, quick kill/restart commands.
- `tg-10` — create compact mobile command sheet.
- `tg-11` / `tg-12` — optional voice and group/topic workflows.

## Immediate next steps for the next session

1. **Rotate the Telegram bot token**
   - In Telegram: open `@BotFather`.
   - Run `/revoke` for `@AceEngineerBot`.
   - Store the new token only in `/home/vamsee/.hermes/.env` as `TELEGRAM_BOT_TOKEN=...`.
   - Never paste the token into chat or GitHub.

2. **Restart Hermes gateway after token rotation**
   - Preferred if sudo is available:
     ```bash
     sudo hermes gateway restart --system
     ```
   - Fallback already proven if sudo unavailable:
     ```bash
     pid=$(pgrep -u vamsee -f 'hermes_cli.main gateway run' | head -1)
     kill -TERM "$pid"
     sleep 35
     hermes gateway status
     ```

3. **Refresh outdated systemd unit**
   - Run:
     ```bash
     sudo hermes gateway restart --system
     ```
   - Verify whether `/etc/systemd/system/hermes-gateway.service` loads `/home/vamsee/.hermes/.env` or whether Hermes gateway reads that file independently.

4. **Create a mobile command sheet**
   - Include commands for: status, GitHub issue links, pausing/killing jobs, requesting handoff, approving plan batches, adding follow-up tasks.

5. **Harden approval/tool exposure**
   - Confirm Telegram sessions keep dangerous actions approval-gated.
   - Keep allowlist-only access; do not enable `GATEWAY_ALLOW_ALL_USERS` or `TELEGRAM_ALLOW_ALL_USERS`.

## Useful commands

Check gateway:

```bash
hermes gateway status
hermes status --all
```

Check Telegram logs without leaking token:

```bash
tail -n 200 /home/vamsee/.hermes/logs/gateway.log \
  | grep -iE 'telegram|Sending response|inbound message|response ready|unauthorized|denied|error|exception' \
  | sed -E 's/[0-9]{8,}:[A-Za-z0-9_-]{20,}/[REDACTED_TOKEN]/g'
```

Run Telegram Desktop:

```bash
/home/vamsee/.local/share/Telegram/Telegram &
```

Installer script:

```bash
/home/vamsee/Downloads/install-telegram-desktop.sh
```

## Git/repo state at exit

At handoff creation, `/mnt/local-analysis/workspace-hub` was behind `origin/main` by 3 commits and had many unrelated modified/untracked files from concurrent provider/autofeed lanes. This handoff artifact is intentionally docs-only and narrow.

Do not clean/reset the dirty main checkout. Reconcile/salvage concurrent work first if continuing repo operations.

## Security notes

- Initial BotFather token was exposed in chat; treat as compromised until rotated.
- Token exists locally in `/home/vamsee/.hermes/.env`; do not print it.
- `TELEGRAM_ALLOWED_USERS` is configured to the controlling Telegram user ID, but this handoff intentionally redacts the numeric ID.
- Telegram is currently private-DM allowlist mode; keep it that way until group/topic workflow is explicitly needed.
