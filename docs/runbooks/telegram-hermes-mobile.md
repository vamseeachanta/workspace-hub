# Telegram-Hermes mobile access — operator runbook

> **Audience:** the operator with sudo on `ace-linux-1` (or any host running the Hermes gateway).
> **Scope:** Phase 1 hardening (token rotation, systemd `EnvironmentFile=` drop-in), Phase 2 mobile guardrails (approvals + destructive-action smoke test), Phase 3 voice (deferred).
> **Source plan:** `docs/plans/2026-05-02-issue-2563-telegram-hermes.md` (`status:plan-approved`)
> **Source issue:** [vamseeachanta/workspace-hub#2563](https://github.com/vamseeachanta/workspace-hub/issues/2563)
> **Reusable skill:** `.claude/skills/operations/telegram-hermes-bot/SKILL.md`

This runbook is the **mobile command sheet** asked for by issue #2563 acceptance criteria and the verification log surface for Phase 2 guardrails.

---

## 0. Token hygiene contract — read first

**Do not paste the bot token into:**

- GitHub issues, PRs, or comments
- Any chat surface (Telegram, Slack, mail, AI-assistant conversation)
- Commit messages or code
- Logs that get shipped off-host

**Do paste the bot token into:**

- `~/.hermes/.env` only (mode 0600, owner `vamsee:vamsee`)
- A personal password manager entry, labelled `AceEngineerBot — Telegram BotFather token`

If the token leaks again (the original 2026-04-30 incident still has not been remediated as of this runbook's first version), the recovery procedure is in §6 below.

---

## 1. Daily mobile command sheet

From Telegram mobile to `@AceEngineerBot`. All commands assume single-user allowlist is enforced (see §3).

### 1.1 Status / health

| Intent | Send |
|---|---|
| "Are you alive?" | `/help` |
| Current Hermes session status | `/status` |
| List active threads / sessions | `/threads` (if enabled in `tools.toolsets`) |
| Show recent gateway log lines | `journalctl -u hermes-gateway -n 20` — but ask via Hermes, NOT a raw shell command on mobile |

### 1.2 Task-list / plan tweaks

| Intent | Send |
|---|---|
| Read a plan from the repo | `read docs/plans/2026-05-02-issue-2563-telegram-hermes.md` |
| Append a task to a plan | `in docs/plans/<plan>.md add a task: <task text>` |
| Pause Hermes routing | `pause routing` (asks gateway to drain in-flight work without scheduling new) |
| Resume routing | `resume routing` |

### 1.3 GitHub link / context grabs

| Intent | Send |
|---|---|
| Open a specific issue | `gh issue view 2563` |
| Show open priority:high issues | `gh issue list --label priority:high --state open --limit 10` |
| Post a comment | `gh issue comment 2563 --body "<text>"` (approval-gated) |

### 1.4 Approval / safety

| Intent | Action |
|---|---|
| The bot asks "approve action X?" | Reply `y` or `yes` to approve; anything else denies |
| The bot has stalled mid-task | `/cancel` |
| Kill an in-flight Hermes session | `/kill <session-id>` |
| Hard restart of the gateway | **Not from mobile.** Use `sudo systemctl restart hermes-gateway` from a host session |

### 1.5 What NOT to do from mobile

- Don't ask Hermes to run unbounded shell loops (`while true; ...`)
- Don't request the bot to print secrets (`cat ~/.hermes/.env`) — even via approval, the response goes through Telegram
- Don't run destructive ops on shared paths (`/etc/systemd/system/`) without a clear scope; prefer to plan on mobile, execute from host

---

## 2. Phase 1 hardening — host-side procedure (one-time)

Requires **sudo on `ace-linux-1`**.

### 2.1 Rotate the BotFather token

This step must happen on Vamsee's phone, not on the host.

1. Open Telegram → message `@BotFather`
2. Send `/mybots` → tap `@AceEngineerBot` → `API Token` → `Revoke current token`
3. Confirm. BotFather replies with the new token. **Do not screenshot, do not paste anywhere except a password manager.**
4. Switch to the host. Continue with §2.2.

### 2.2 Update `~/.hermes/.env` without exposing the token

```bash
# Stop the gateway briefly so we don't race on a partial read.
sudo systemctl stop hermes-gateway

# Open the env file in $EDITOR (vi/nano). NEVER use `echo "TOKEN" >> .env` — that puts
# the token in shell history.
${EDITOR:-vi} /home/vamsee/.hermes/.env

# In the editor: replace the old TELEGRAM_BOT_TOKEN=... line with the new value.
# Save and exit.

# Verify perms preserved.
stat -c '%a %U:%G' /home/vamsee/.hermes/.env
# Expected: 600 vamsee:vamsee

# Verify the token is not in your shell history.
grep -E "[0-9]{8,10}:[A-Za-z0-9_-]{30,}" ~/.bash_history | wc -l
# Expected: 0
```

### 2.3 Install the systemd drop-in override

This is the **load-bearing durability fix**. A drop-in override survives `hermes update` overwrites of the base unit (per `project_hermes_installation.md` — the shebang-revert recurrence).

```bash
sudo systemctl edit hermes-gateway
```

In the editor that opens, paste exactly this (no surrounding text, no leading dash):

```ini
[Service]
EnvironmentFile=/home/vamsee/.hermes/.env
TimeoutStopSec=210
```

> **Why no leading dash on `EnvironmentFile=`:** the dashed form (`EnvironmentFile=-/path`) makes systemd silently ignore a missing file. We want fail-closed: if the env file is missing, the gateway must NOT start with a stale-or-empty token.
>
> **Why `TimeoutStopSec=210`:** the gateway logs `Stale systemd unit detected: TimeoutStopSec=60s but drain_timeout=180s (expected >=210s)`. Bumping this clears the warning and prevents systemd from SIGKILLing the gateway mid-drain.

Save and exit. systemd writes to `/etc/systemd/system/hermes-gateway.service.d/override.conf`.

### 2.4 Reload + restart + verify

```bash
sudo systemctl daemon-reload
sudo systemctl restart hermes-gateway.service
sleep 5

# Verify the override is loaded.
systemctl show hermes-gateway -p EnvironmentFiles
# Expected: EnvironmentFiles=/home/vamsee/.hermes/.env (ro)

# Verify the drop-in file content.
grep -E "^EnvironmentFile=/home/vamsee/.hermes/.env$" \
    /etc/systemd/system/hermes-gateway.service.d/override.conf
# Expected: one matching line (no leading dash)

# Verify no startup errors.
journalctl -u hermes-gateway -n 200 --no-pager | \
    grep -iE '(error|exception|traceback)' | head
# Expected: empty

# Verify the stale-unit warning is gone.
journalctl -u hermes-gateway -n 200 --no-pager | grep -c "Stale systemd unit"
# Expected: 0

# Verify Telegram polling-mode connection.
journalctl -u hermes-gateway -n 200 --no-pager | grep -c "Telegram.*polling"
# Expected: >= 1
```

### 2.5 Validate the rotated token (without exposing it on cmdline)

```bash
( set +o history
  TG_TOKEN="$(grep -E '^TELEGRAM_BOT_TOKEN=' /home/vamsee/.hermes/.env | cut -d= -f2-)"
  curl -s "https://api.telegram.org/bot${TG_TOKEN}/getMe" -o /tmp/tg-getme.json
  unset TG_TOKEN
)
jq -r '.ok' /tmp/tg-getme.json
# Expected: true
jq -r '.result.username' /tmp/tg-getme.json
# Expected: AceEngineerBot
shred -u /tmp/tg-getme.json
```

> **Residual risk:** the token still appears in `/proc/<curl-pid>/cmdline` for the ~1-2s the request is in flight. On a single-tenant host that's acceptable; if you want a stricter posture, swap the curl line for a 4-line Python `requests` script that POSTs the token in a header (token never appears in argv).

### 2.6 Phase 1 acceptance test — mobile round-trip

From Telegram mobile:

```
/status
```

Expected: Hermes responds within 30s with current session state.

Cross-check on host:

```bash
journalctl -u hermes-gateway -n 100 --no-pager | grep -E "(telegram|status)" | tail -5
```

Expected: inbound `/status` log line + outbound response log line.

If the response doesn't arrive within 60s, see §5 troubleshooting.

---

## 3. Phase 2 guardrails — approval mode and toolset posture

### 3.1 Approval mode

```bash
grep -A3 "^approvals:" /home/vamsee/.hermes/config.yaml
```

Required:

```yaml
approvals:
  mode: manual   # or: smart
  timeout: 60
  cron_mode: deny   # auto-deny in cron sessions (already set as of 2026-05-13)
```

**Never** set `mode: off` on a bot with terminal access. The Hermes security doc (`~/.hermes/hermes-agent/website/docs/user-guide/security.md` line 76) labels this YOLO.

### 3.2 Mobile-safe toolset

Edit `~/.hermes/config.yaml` `gateway` or `tools` section. The mobile-safe set:

| Tool | Default | Approval-gated? | Notes |
|---|---|---|---|
| `memory` | enabled | no | Read/write Hermes memory store |
| `session_search` | enabled | no | Read-only over Hermes session log |
| `cronjob` | enabled | yes | Schedule/cancel cron entries |
| `send_message` | enabled | yes | Reply via Telegram (self-allowed) |
| `file` | enabled | yes for writes | Read-only is safe; writes must be approval-gated |
| `terminal` | enabled | **yes (always)** | Any shell exec requires explicit approve |
| `browser/web` | enabled | yes | URL fetches gated to allowlist domains |
| `kanban` | enabled | yes | Task-list management |

If `terminal` is currently approval-OFF, fix it before mobile use.

### 3.3 Destructive-action smoke test (Phase 2 acceptance)

This is the **t10 / t10b / t10c** triple from the plan.

```bash
# Setup: create the canary on host.
touch /tmp/test-approval-gate-canary
ls -la /tmp/test-approval-gate-canary
# Expected: file present
```

From mobile, send to `@AceEngineerBot`:

```
please rm /tmp/test-approval-gate-canary
```

**Phase 2.a — deny path:**
- Bot responds with an approval prompt.
- Reply anything other than `y`/`yes` (e.g., `no` or `n`).
- Check canary intact on host:

```bash
test -f /tmp/test-approval-gate-canary && echo GATE_HELD
# Expected: GATE_HELD
```

**Phase 2.b — approve path:**
- Send the same request again from mobile.
- Reply `y`.
- Check canary deleted:

```bash
test -f /tmp/test-approval-gate-canary || echo CANARY_DELETED
# Expected: CANARY_DELETED
```

### 3.4 Phase 2 evidence section — operator fills in after the smoke test

Append the journalctl excerpts below this line after running §3.3 (redact any token/user-id values before pasting):

```
[ Phase 2 evidence — fill in after smoke test 2026-MM-DD ]

  Deny-path log line:
  <paste output of: journalctl -u hermes-gateway --since "5 minutes ago" | grep -i approval | tail -3>

  Approve-path log line:
  <paste output of: journalctl -u hermes-gateway --since "5 minutes ago" | grep -i approval | tail -3>

  Canary outcomes: deny=GATE_HELD, approve=CANARY_DELETED
```

---

## 4. Phase 3 — voice (optional, deferred)

Not in scope for this runbook beyond a pointer. If the operator opts in:

1. Read `~/.hermes/hermes-agent/website/docs/guides/use-voice-mode-with-hermes.md`
2. Add `VOICE_TOOLS_OPENAI_KEY=<scoped-key>` to `~/.hermes/.env` (preserve mode 0600)
3. `sudo systemctl restart hermes-gateway`
4. Send a 5-second voice note from mobile
5. Verify journalctl shows STT transcript → Hermes response → optional TTS reply
6. Capture evidence in `.claude/skills/operations/telegram-hermes-bot/references/voice-mode.md`

---

## 5. Troubleshooting

### 5.1 Symptom: `/status` from mobile gets no reply

```bash
# Is the gateway running?
systemctl is-active hermes-gateway
# Expected: active

# Is Telegram connected?
journalctl -u hermes-gateway -n 200 --no-pager | grep -iE "(telegram.*(polling|connect|error))" | tail
# Look for: "Telegram polling started" (good) or "telegram connect timed out" (bad)

# Is the token loaded?
systemctl show hermes-gateway -p EnvironmentFiles | grep -c '/home/vamsee/.hermes/.env'
# Expected: 1
```

If `telegram connect timed out`: network egress to `api.telegram.org` may be blocked. Test:

```bash
curl -sI https://api.telegram.org/bot$(grep '^TELEGRAM_BOT_TOKEN=' /home/vamsee/.hermes/.env | cut -d= -f2-)/getMe | head -3
```

> **CAUTION:** this leaks the token into `/proc/<curl-pid>/cmdline`. Prefer the §2.5 subshell snippet.

### 5.2 Symptom: gateway exits with status=75/TEMPFAIL

Observed 2026-05-13 21:18 on `ace-linux-1`. Exit code 75 = `EX_TEMPFAIL` (BSD `sysexits.h`).

Diagnosis:

```bash
journalctl -u hermes-gateway -n 500 --no-pager | grep -B5 "status=75" | head -20
```

Typical root causes: provider-API rate limit (OpenAI codex), DNS hiccup, or hermes-cli sub-process exit. The systemd `Restart=on-failure` + `RestartSec=30` policy recovers automatically; concern only if exit-code-75 recurs more than 3× in 10 min.

### 5.3 Symptom: "Stale systemd unit detected" warning

Already mitigated by §2.3 (the drop-in override bumps `TimeoutStopSec=210`). If you still see it after the drop-in is in place:

```bash
systemctl cat hermes-gateway
# Look for the drop-in override AT THE BOTTOM. If absent, daemon-reload was skipped.

sudo systemctl daemon-reload
sudo systemctl restart hermes-gateway
```

### 5.4 Symptom: unauthorized user is messaging the bot

```bash
journalctl -u hermes-gateway --since "1 hour ago" --no-pager | grep -i "unauthorized"
```

Confirm `TELEGRAM_ALLOWED_USERS` is set in `~/.hermes/.env` (single allowed user ID) and `GATEWAY_ALLOW_ALL_USERS=` is empty or `false`.

```bash
grep -E "^(TELEGRAM_ALLOWED_USERS|GATEWAY_ALLOW_ALL_USERS)=" /home/vamsee/.hermes/.env
# Expected: TELEGRAM_ALLOWED_USERS=<your-id>
#           GATEWAY_ALLOW_ALL_USERS=    (empty value, OR absent)
```

If `GATEWAY_ALLOW_ALL_USERS=true` is present, **remove it** — the Hermes security doc line 199-231 confirms the allowlist precedence chain: platform allowlist wins, but the `_ALL_USERS=true` flag bypasses fail-closed defaults in cases the allowlist hasn't loaded yet.

---

## 6. Token-leak recovery procedure

If the bot token is exposed (pasted in chat, posted to issue, committed to repo):

1. **Immediately:** in BotFather mobile, `/mybots` → `@AceEngineerBot` → `API Token` → `Revoke current token`. This invalidates the leaked token even if it has not yet been written down.
2. Capture the new token in the password manager only.
3. Update `~/.hermes/.env` per §2.2 (editor only — no shell history).
4. Restart the gateway per §2.4.
5. If the leak was via git commit:
   - `git log --all --full-history --source -- <leak-file>` to find the bad SHA
   - `git push origin --delete <branch>` if the leak is on a feature branch
   - For main-branch leaks: rotate before any rewrite attempt; consider the leak permanent and treat the new token as the source of truth
6. Audit `git grep -E "[0-9]{8,10}:[A-Za-z0-9_-]{30,}"` returns empty.

---

## 7. References

- Plan: `docs/plans/2026-05-02-issue-2563-telegram-hermes.md`
- Issue: [vamseeachanta/workspace-hub#2563](https://github.com/vamseeachanta/workspace-hub/issues/2563)
- Skill: `.claude/skills/operations/telegram-hermes-bot/SKILL.md`
- Hermes Telegram guide: `~/.hermes/hermes-agent/website/docs/guides/team-telegram-assistant.md`
- Hermes env-var reference: `~/.hermes/hermes-agent/website/docs/reference/environment-variables.md`
- Hermes security doc: `~/.hermes/hermes-agent/website/docs/user-guide/security.md`
- Voice-mode guide: `~/.hermes/hermes-agent/website/docs/guides/use-voice-mode-with-hermes.md`
- Memory: `project_hermes_installation.md`, `project_hermes_codex_quota.md`
