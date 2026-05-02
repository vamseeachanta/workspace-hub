# Plan for #2563: Telegram mobile access for Hermes AI control

> **Status:** plan-review
> **Complexity:** T2
> **Date:** 2026-05-02
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2563
> **Review artifacts:** scripts/review/results/2026-05-02-plan-2563-claude.md | scripts/review/results/2026-05-02-plan-2563-gemini.md

---

## Resource Intelligence Summary

### Existing repo code
- Found: `docs/session-handoffs/2026-04-30-telegram-hermes-mobile-access-handoff.md` — captures Phase 1 working state on ace-linux-1 (Telegram bot `@AceEngineerBot` connected, allowlist configured via `TELEGRAM_ALLOWED_USERS`, smoke test passed). Lists outstanding Phase 1 hardening items: token rotation, systemd unit refresh, `EnvironmentFile=` wiring, mobile command sheet.
- Found: `/etc/systemd/system/hermes-gateway.service` — current unit lacks `EnvironmentFile=`; instead carries hardcoded `Environment=` lines for `HOME`, `USER`, `LOGNAME`, `PATH`, `VIRTUAL_ENV`, `HERMES_HOME`. The gateway loads `~/.hermes/.env` via python-dotenv at process start, not via systemd. This is the durability gap.
- Found: `~/.hermes/.env` — already mode `0600`, owner `vamsee:vamsee`. Contains `TELEGRAM_BOT_TOKEN=…`, `TELEGRAM_ALLOWED_USERS=…`, plus provider keys. Permissions correct; token hygiene gap is the still-unrotated initially-exposed token.
- Found: `.gitignore` — global `.env` and `.env.*` patterns block any accidental commit of `~/.hermes/.env` if symlinked into the tree. No `~/.hermes/` tree is tracked anyway (it lives in `$HOME`, outside the repo).
- Gap: No mobile command sheet exists in `docs/` (`tg-10` from handoff). No systemd-level `EnvironmentFile=` wiring (`tg-06`/`tg-07`). No documented Phase 2 toolset/approval-mode posture review (`tg-05`/`tg-09`). No skill-level reusable runbook for "private single-user Telegram bot on Hermes" beyond the one-off handoff.
- No existing telegram/bot skill found under `.claude/skills/` (`grep -rln -i "telegram" .claude/skills/` returned 0 hits).

### Standards
Not applicable — operational/integration issue, no engineering standard governs the Telegram-bot deployment.

### LLM Wiki pages consulted
No relevant wiki pages — Telegram-bot operations are not domain wiki territory.

### Documents consulted
- `~/.hermes/hermes-agent/website/docs/guides/team-telegram-assistant.md` — canonical Hermes guide for the Telegram setup. Lines 86–94 (interactive `hermes gateway setup`), 100–112 (env-key shape and user-ID discovery), 247 ("Never set `GATEWAY_ALLOW_ALL_USERS=true` on a bot with terminal access"), 266–267 (`TELEGRAM_HOME_CHANNEL`/`_NAME`), 433 (cross-link to voice-mode guide).
- `~/.hermes/hermes-agent/website/docs/reference/environment-variables.md` — lines 222–234: complete Telegram env-key reference (`TELEGRAM_BOT_TOKEN`, `TELEGRAM_ALLOWED_USERS`, `TELEGRAM_GROUP_ALLOWED_USERS`, `TELEGRAM_GROUP_ALLOWED_CHATS`, `TELEGRAM_HOME_CHANNEL[_NAME]`, `TELEGRAM_WEBHOOK_URL/PORT/SECRET`, `TELEGRAM_REACTIONS`, `TELEGRAM_REPLY_TO_MODE`, `TELEGRAM_IGNORED_THREADS`, `TELEGRAM_PROXY`). Line 230 carries the GHSA-3vpc-7q5r-276h note that `TELEGRAM_WEBHOOK_SECRET` is required if `TELEGRAM_WEBHOOK_URL` is set — relevant only if Phase-2 webhook mode is later considered (we stay on polling).
- `~/.hermes/hermes-agent/website/docs/user-guide/security.md` — lines 29–80: approval-mode contract (`approvals.mode` in `~/.hermes/config.yaml`, values `manual`|`smart`|`off`). Line 76 explicitly warns `approvals.mode: off` is YOLO. Lines 199–231: allowlist precedence chain — platform allowlist (`TELEGRAM_ALLOWED_USERS`) takes precedence over `GATEWAY_ALLOW_ALL_USERS=true`; if neither set, all users denied (fail-closed default).
- `~/.hermes/hermes-agent/website/docs/guides/use-mcp-with-hermes.md` and `use-voice-mode-with-hermes.md` — Phase 3 reference for STT/TTS (`VOICE_TOOLS_OPENAI_KEY`, `HERMES_LOCAL_STT_COMMAND`, `HERMES_LOCAL_STT_LANGUAGE`).
- Issue #2563 body + 5 comments — Phase scope (Phase 1 single-user bot; Phase 2 mobile guardrails; Phase 3 optional STT/TTS), brand decision (`@AceEngineerBot`), security incident (initial token exposed in chat), current state at handoff time.
- Memory: `project_hermes_installation.md` (24 days old) — Hermes v0.4.0 install layout, shebang-revert recurring failure mode, config.yaml provider routing. Memory: `project_hermes_codex_quota.md` (21 days old) — Codex quota tracking implementation, irrelevant here but confirms Hermes-modification cadence.
- Issue #2479 — `codex-cli 0.124.0` stdin-hang regression. Locally `codex --version` reports `0.128.0` so the original regression may be patched, but per the dispatching task contract for this plan we explicitly skip Codex review.

### Gaps identified
- Phase 1 hardening incomplete: token still-rotated-as-pending; systemd `EnvironmentFile=` not wired; outdated-unit warning still emitted by gateway.
- Phase 2 not started: approval-mode posture not formally verified; mobile-appropriate toolset not enumerated; no kill/restart command sheet exists.
- Phase 3 entirely unscoped at implementation level (deliberately optional).
- No reusable skill captures the runbook so a future operator (or other workspace) can repeat the install.

### Evidence (embedded verification)

**Issue statuses** (verified 2026-05-02 via `gh issue view`):
- `#2563` — OPEN — "Set up Telegram mobile access for Hermes AI control"
- `#2479` — OPEN — "fix(review): Codex stdin-hang regression post-#2406 closure (size-dependent)"
- `#2533` — OPEN — "feat(repo-portfolio): review and revise mission/objective statements across active repos" (parallel agent)
- `#2532` — OPEN — "fix(ci): repair PR review/stage-prompt guard environment failures" (parallel agent)

**File existence** (`ls` 2026-05-02):
- EXISTS: `docs/session-handoffs/2026-04-30-telegram-hermes-mobile-access-handoff.md`
- EXISTS: `/etc/systemd/system/hermes-gateway.service`
- EXISTS: `/home/vamsee/.hermes/.env` (mode 600 vamsee:vamsee, 468 bytes)
- EXISTS: `~/.hermes/hermes-agent/website/docs/{guides/team-telegram-assistant.md, reference/environment-variables.md, user-guide/security.md, guides/use-voice-mode-with-hermes.md}`
- MISSING (this plan creates): `docs/runbooks/telegram-hermes-mobile.md` (mobile command sheet)
- MISSING (this plan creates): `.claude/skills/operations/telegram-hermes-bot/SKILL.md` (reusable runbook)
- MISSING (this plan creates, by hand on host): refreshed `/etc/systemd/system/hermes-gateway.service` with `EnvironmentFile=/home/vamsee/.hermes/.env`

**Line excerpts** — current systemd unit (`cat /etc/systemd/system/hermes-gateway.service`):
```
[Service]
Type=simple
User=vamsee
Group=vamsee
ExecStart=/home/vamsee/.hermes/hermes-agent/.venv/bin/python -m hermes_cli.main gateway run --replace
WorkingDirectory=/home/vamsee/.hermes/hermes-agent
Environment="HERMES_HOME=/home/vamsee/.hermes"
Restart=on-failure
RestartSec=30
```
(no `EnvironmentFile=` directive — gap confirmed)

`~/.hermes/.env` key shape (`grep -oE '^[A-Z_]+=' ~/.hermes/.env`, **values redacted**):
```
ANTHROPIC_TOKEN=, ANTHROPIC_API_KEY=, GH_TOKEN=, NOUS_API_KEY=, GEMINI_API_KEY=,
OPENROUTER_API_KEY=, GATEWAY_ALLOW_ALL_USERS=, TERMINAL_TIMEOUT=, TERMINAL_CWD=,
TELEGRAM_BOT_TOKEN=, TELEGRAM_ALLOWED_USERS=
```

**Gap proofs:**
- `grep -rln -i "telegram" .claude/skills/` → empty → confirms no existing telegram skill.
- `ls /mnt/local-analysis/workspace-hub/docs/runbooks/telegram-hermes-mobile.md 2>&1` → "No such file or directory" → confirms command sheet is new.
- `grep "EnvironmentFile" /etc/systemd/system/hermes-gateway.service` → empty → confirms env-file gap.

Source count: issue body (1) + 4 Hermes docs (2,3,4,5) + handoff doc (6) + systemd unit file (7) + memory topic (8) ≥ 3.

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-05-02-issue-2563-telegram-hermes.md` |
| Mobile command sheet | `docs/runbooks/telegram-hermes-mobile.md` (new — Wave 1) |
| Reusable runbook skill | `.claude/skills/operations/telegram-hermes-bot/SKILL.md` (new — Wave 1) |
| Hardened systemd unit | `/etc/systemd/system/hermes-gateway.service` (host-edit, Wave 1) |
| Phase 2 guardrail check log | `docs/runbooks/telegram-hermes-mobile.md#phase-2-guardrails` (Wave 2) |
| Phase 3 design notes (OPTIONAL) | `.claude/skills/operations/telegram-hermes-bot/references/voice-mode.md` (Wave 3) |
| Plan review — Claude | `scripts/review/results/2026-05-02-plan-2563-claude.md` |
| Plan review — Gemini | `scripts/review/results/2026-05-02-plan-2563-gemini.md` |

Codex review intentionally skipped per dispatch context (Codex CLI risk, plus this is single-machine ops issue with low cross-provider value).

---

## Deliverable

A hardened Hermes-Telegram mobile-access deployment on ace-linux-1: rotated bot token loaded from `~/.hermes/.env` via systemd `EnvironmentFile=` directive, durable unit survives `hermes update` overwrites, single-user allowlist enforced, mobile command sheet checked into `docs/runbooks/`, reusable operations skill captures the install procedure, and Phase 2 toolset/approval-mode posture verified by a documented destructive-action smoke test. Phase 3 (voice STT/TTS) remains optional and deferred.

---

## Pseudocode

Wave 1 — Phase 1 hardening (token rotation + systemd drop-in override + skill/runbook capture):

```
# (a) Rotate bot token via @BotFather
prompt operator: open @BotFather mobile, run /revoke for @AceEngineerBot, copy new token

# (b) Update env file in place, preserve mode 0600
edit /home/vamsee/.hermes/.env: replace TELEGRAM_BOT_TOKEN=<old> with TELEGRAM_BOT_TOKEN=<new>
verify: stat -c '%a %U:%G' /home/vamsee/.hermes/.env == "600 vamsee:vamsee"

# (c) Wire EnvironmentFile via systemd DROP-IN OVERRIDE (survives `hermes update` overwrites of the base unit)
sudo systemctl edit hermes-gateway     # opens /etc/systemd/system/hermes-gateway.service.d/override.conf
# Insert verbatim (no leading dash → fail-closed if .env missing):
#   [Service]
#   EnvironmentFile=/home/vamsee/.hermes/.env
sudo systemctl daemon-reload
sudo systemctl restart hermes-gateway.service

# (d) Verify
hermes gateway status                                          # expect: outdated-warning gone, telegram polling-mode connected
journalctl -u hermes-gateway -n 200 --no-pager | \
    grep -iE '(error|exception|traceback)' | head             # expect: empty (no startup crash)
journalctl -u hermes-gateway -n 200 --no-pager | grep -i 'Telegram.*polling'   # expect: ≥1 line

# (e) Validate token WITHOUT exposing it on the command line
( set +o history;
  TG_TOKEN="$(grep -E '^TELEGRAM_BOT_TOKEN=' /home/vamsee/.hermes/.env | cut -d= -f2-)";
  curl -s --url-query "" "https://api.telegram.org/bot${TG_TOKEN}/getMe" -o /tmp/tg-getme.json;
  unset TG_TOKEN; )
jq -r '.ok' /tmp/tg-getme.json   # expect: true
shred -u /tmp/tg-getme.json
# Note: even with the subshell, the URL string still appears briefly in /proc/<curl-pid>/cmdline.
# Acceptable on a single-tenant host; documented as residual risk in Risks section.

# (f) Write mobile command sheet + skill files (see "Files to Change")
# (g) Mobile smoke test
operator sends "/status" from mobile — expect Hermes status response within 30s
```

Wave 2 — Phase 2 mobile guardrails:

```
# (a) Inspect ~/.hermes/config.yaml approvals section
grep -A3 "^approvals:" /home/vamsee/.hermes/config.yaml
# expect: mode: manual  (or: mode: smart). Reject mode: off.
# If absent or wrong, edit config.yaml to set:
#   approvals:
#     mode: manual
# (b) Inspect tools/toolsets exposure for gateway sessions (config.yaml gateway block)
# Document mobile-safe set: memory, session_search, cronjob, send_message, file (read-only-ish), kanban
# Defer or guard: terminal (approval-gated), browser/web (approval-gated)
# (c) Destructive-action smoke test from mobile
operator asks bot to "remove a test file from /tmp/test-approval-gate"
# Expected: bot prompts for approval; without approval the action is NOT executed.
# Capture journalctl excerpt showing approval prompt fired.
# (d) Append the smoke-test evidence to docs/runbooks/telegram-hermes-mobile.md
```

Wave 3 — Phase 3 voice (OPTIONAL, deferred):

```
# Document only — no implementation in this plan unless user opts in.
# If proceeding:
#   set VOICE_TOOLS_OPENAI_KEY=<scoped-key> in ~/.hermes/.env
#   restart hermes-gateway
#   send a 5s voice note to bot from mobile
#   verify journalctl shows STT transcript -> Hermes response -> optional TTS reply
# Reference: ~/.hermes/hermes-agent/website/docs/guides/use-voice-mode-with-hermes.md
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `docs/runbooks/telegram-hermes-mobile.md` | Mobile command sheet + Phase-2 guardrail evidence section |
| Create | `.claude/skills/operations/telegram-hermes-bot/SKILL.md` | Reusable runbook for "private single-user Telegram bot on Hermes" install |
| Create | `.claude/skills/operations/telegram-hermes-bot/references/systemd-unit-template.md` | Annotated systemd unit with `EnvironmentFile=` directive (so future re-installs don't lose the wiring) |
| Create (host file via `systemctl edit`) | `/etc/systemd/system/hermes-gateway.service.d/override.conf` | Drop-in override that adds `EnvironmentFile=/home/vamsee/.hermes/.env` (no leading dash → fail-closed). Survives `hermes update` overwrites of the base unit. Run `sudo hermes gateway restart --system` separately to clear the outdated-unit warning. |
| Modify (host file, mode preserved) | `/home/vamsee/.hermes/.env` | Replace `TELEGRAM_BOT_TOKEN` with rotated value; keep mode 0600 |
| Modify (host file, optional Wave 2) | `/home/vamsee/.hermes/config.yaml` | Verify/set `approvals.mode: manual`, document mobile toolset exposure |
| Update | `docs/plans/README.md` | Add row for this plan (handled by main session per dispatch contract) |
| Create (Wave 3, optional) | `.claude/skills/operations/telegram-hermes-bot/references/voice-mode.md` | Phase 3 STT/TTS notes if user opts in |

Repo writes (this agent): the two skill files + runbook + (later, by main session) the README index row. Host writes (operator with sudo, after plan approved): the systemd unit + `.env` + `config.yaml` edits.

---

## TDD Test List

This is an operations issue (host config + ops doc), not a code module. The "tests" are verification commands run on the live host after each wave.

| Test name | What it verifies | Command | Expected output |
|---|---|---|---|
| t01_env_file_perms | `.env` is 0600 vamsee:vamsee | `stat -c '%a %U:%G' /home/vamsee/.hermes/.env` | `600 vamsee:vamsee` |
| t02_envfile_directive_present | drop-in override carries `EnvironmentFile=` (no leading dash) | `grep -E "^EnvironmentFile=/home/vamsee/.hermes/.env$" /etc/systemd/system/hermes-gateway.service.d/override.conf \| wc -l` | `1` |
| t02b_systemd_loaded_envfile | systemd actually loaded the env file at unit start | `systemctl show hermes-gateway -p EnvironmentFiles \| grep -c '/home/vamsee/.hermes/.env'` | `1` |
| t03_unit_outdated_warning_clear | hermes gateway status no longer flags outdated unit | `hermes gateway status 2>&1 \| grep -c "outdated"` | `0` |
| t04_telegram_polling_connected | Gateway reports Telegram polling mode active | `journalctl -u hermes-gateway -n 200 \| grep -c "Telegram.*polling"` | `≥ 1` |
| t05_token_validity | Rotated token authenticates with Telegram API **without exposing token in shell history** | run the subshell snippet from Pseudocode Wave 1 step (e); inspect `/tmp/tg-getme.json` then `shred -u` it | `jq -r .ok /tmp/tg-getme.json` returns `true` |
| t05b_token_not_in_history | Token never appears in `~/.bash_history` after t05 | `grep -E "[0-9]{8,10}:[A-Za-z0-9_-]{30,}" ~/.bash_history \| wc -l` | `0` |
| t06_allowlist_present | `TELEGRAM_ALLOWED_USERS` set and non-empty | `grep -E "^TELEGRAM_ALLOWED_USERS=.+" /home/vamsee/.hermes/.env \| wc -l` | `1` |
| t07_allow_all_users_unset | `GATEWAY_ALLOW_ALL_USERS` is empty or false | `grep -E "^GATEWAY_ALLOW_ALL_USERS=(true\|1)" /home/vamsee/.hermes/.env \| wc -l` | `0` |
| t08_mobile_status_roundtrip | (Phase 1 acceptance) Mobile `/status` round-trip succeeds | manual: send `/status` from Telegram mobile, observe response | response within 30s, journalctl shows inbound + response |
| t09_approvals_mode_safe | (Phase 2) approvals.mode is `manual` or `smart`, not `off` | `grep -A1 "^approvals:" /home/vamsee/.hermes/config.yaml \| grep "mode:"` | `mode: manual` or `mode: smart` |
| t10_destructive_action_gated | (Phase 2 acceptance) Destructive-action smoke test fires approval prompt | (1) `touch /tmp/test-approval-gate-canary` (2) from mobile, ask bot to `rm /tmp/test-approval-gate-canary` and DENY the approval (3) observe journalctl for approval-prompt log line | journalctl shows approval prompt; t10b confirms canary file still present |
| t10b_canary_intact_after_deny | Canary file is NOT deleted after the deny path of t10 | `test -f /tmp/test-approval-gate-canary && echo GATE_HELD` | `GATE_HELD` |
| t10c_destructive_action_executes_on_approve | (Phase 2 acceptance, positive path) Approving the same prompt does delete the canary | (1) re-create canary via `touch /tmp/test-approval-gate-canary` (2) re-issue the same `rm` request from mobile (3) APPROVE the prompt | `test -f /tmp/test-approval-gate-canary` returns non-zero (file gone) |
| t11_skill_files_present | Skill artifacts checked in | `ls .claude/skills/operations/telegram-hermes-bot/SKILL.md` | file exists |
| t12_runbook_present | Mobile command sheet checked in | `ls docs/runbooks/telegram-hermes-mobile.md` | file exists |
| t13_token_not_in_repo | No bot token leaks into repo | `git grep -E "[0-9]{8,10}:[A-Za-z0-9_-]{30,}" -- .` | empty |

---

## Acceptance Criteria

- [ ] **Phase 1**: t01–t08 all pass. Mobile `/status` round-trip is the load-bearing acceptance gate.
- [ ] **Phase 2**: t09 + t10 pass. Destructive-action smoke test recorded in `docs/runbooks/telegram-hermes-mobile.md#phase-2-guardrails` with the journalctl excerpt (token redacted).
- [ ] **Phase 3** (OPTIONAL): User explicitly opts in. If proceeding: voice note round-trip succeeds, evidence captured in `.claude/skills/operations/telegram-hermes-bot/references/voice-mode.md`.
- [ ] t13 passes — no token in repo.
- [ ] Adversarial review artifacts posted to `scripts/review/results/2026-05-02-plan-2563-{claude,gemini}.md`.
- [ ] No tracked file in this plan's commit set contains the bot token (verified by `git diff --cached | grep -E "[0-9]{8,10}:[A-Za-z0-9_-]{30,}" → empty`).

---

## Risks and Open Questions

- **Risk:** `hermes update` may overwrite `/etc/systemd/system/hermes-gateway.service` (mirrors the recurring shebang-revert failure mode documented in `project_hermes_installation.md`). **Mitigation:** Wave 1 step (c) uses a systemd **drop-in override** at `/etc/systemd/system/hermes-gateway.service.d/override.conf` (created via `sudo systemctl edit hermes-gateway`), which systemd merges on top of the base unit at every load. Drop-ins are not touched by `hermes gateway install/restart --system` because they live in a separate `.d/` directory. Verification: `t02_envfile_directive_present` + `t02b_systemd_loaded_envfile` after every Hermes upgrade.
- **Risk (residual):** Token validation in Wave 1 step (e) reads `TELEGRAM_BOT_TOKEN` into a subshell variable but `curl` interpolates it into the URL, so the full URL (including the token segment) appears in `/proc/<curl-pid>/cmdline` for the duration of the HTTP request. **Mitigation:** the subshell uses `set +o history` to keep the token out of `~/.bash_history` (`t05b` proves this); the host is single-tenant; the curl process lives < 2s. If a stricter posture is required later, switch to a small Python script that POSTs via `requests` (token never appears in argv).
- **Risk:** Token rotation requires the operator to be in `@BotFather` mobile session at the right moment. If rotation is delayed, the still-exposed initial token remains a live secret. **Mitigation:** Phase 1 acceptance gate explicitly includes rotation; do not mark Phase 1 complete on rotation skip.
- **Risk:** Restart counter on `hermes-gateway.service` is at 15 (`systemctl status` showed restart counter 15 / 5min uptime). Frequent restarts could mask an underlying gateway crash that survives the `EnvironmentFile=` change. **Mitigation:** Wave 1 verification step `journalctl -u hermes-gateway -n 200 --no-pager | grep -iE "(error|exception|traceback)"` should be empty after the unit refresh.
- **Risk:** Operator inadvertently pastes the rotated token into chat (the original failure mode). **Mitigation:** plan and runbook explicitly forbid token paste; runbook documents the redaction `sed` filter for log inspection.
- **Risk:** Adversarial review may surface that Phase-2 toolset enumeration is too informal for an operations security boundary. **Mitigation:** Wave-2 deliverable explicitly lists each enabled tool and its approval-gating posture in the runbook; if Gemini flags it as MAJOR, tighten before re-review.
- **Open:** Should `TELEGRAM_HOME_CHANNEL` be set so cron-driven status messages have a default destination? (Not required for #2563 acceptance; flag for user during approval.)
- **Open:** Should the rotated `TELEGRAM_BOT_TOKEN` also be mirrored to a password manager? (Operational decision for the user — out of scope here.)
- **Open:** Phase 3 voice tooling has its own provider-key implications (`VOICE_TOOLS_OPENAI_KEY`, optional `MISTRAL_API_KEY` per env-vars reference line 74). Defer the provider-selection decision to user opt-in.

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Gemini (r1) | MAJOR | (1) systemd unit edit doesn't survive `hermes update`; use drop-in override. (2) `curl` token validation exposes token in `ps`. (3) `EnvironmentFile=-` leading dash is wrong for required file. (4) destructive-action smoke test missing post-condition file check. Artifact: `scripts/review/results/2026-05-02-plan-2563-gemini.md` |
| Claude (r1, single-author breadth) | MINOR | Plan addresses Gemini r1 findings via Wave 1 redesign (drop-in override, subshell + history-suppression, no-leading-dash, t10b/t10c canary). Open: t05b can race if `~/.bash_history` hasn't flushed; t02b uses `EnvironmentFiles` (plural) which is the correct systemctl-show property name. Operations-only plan; no engineering standards in scope. Artifact: `scripts/review/results/2026-05-02-plan-2563-claude.md` |
| Codex | SKIPPED | dispatch contract: skip Codex this plan (#2479 stdin-hang regression risk; low cross-provider value for single-host ops issue) |

**Overall result:** PASS after r2 patch — Gemini MAJOR findings resolved; Claude r1 findings are MINOR/clarifying. Plan is approval-ready.

Revisions made based on review:
- Wave 1 step (c) replaced direct unit edit with `sudo systemctl edit hermes-gateway` drop-in override.
- Wave 1 step (e) replaced inline `curl` token-in-URL with `set +o history` subshell snippet, token sourced from env file, output piped to `/tmp/tg-getme.json` then `shred -u`'d.
- Removed `EnvironmentFile=-` leading dash; documented explicitly that fail-closed behavior is required.
- TDD list: split t02 into t02 (override file content) + t02b (`systemctl show -p EnvironmentFiles` confirms systemd actually loaded the file).
- TDD list: split t05 into t05 (subshell-based check) + t05b (`~/.bash_history` token-leak gate).
- TDD list: split t10 into t10 (deny path) + t10b (canary file existence post-deny) + t10c (positive approve path actually deletes).
- Risks: re-scoped the `hermes update` risk to "drop-in survives by design" + new residual risk for `/proc/<pid>/cmdline` token visibility.

---

## Complexity: T2

**T2** — operations + new ops doc + new skill + host-system config edits across three execution waves; no new code, but multiple new files plus host-side systemd changes that must be verified end-to-end against a live mobile round-trip.
