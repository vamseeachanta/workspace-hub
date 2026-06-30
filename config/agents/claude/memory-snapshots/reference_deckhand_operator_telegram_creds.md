---
name: reference_deckhand_operator_telegram_creds
description: "Why deckhand send-fixture.py \"AS THE OPERATOR\" Telegram sends fail on a box, and how to provision the MTProto creds"
metadata: 
  node_type: memory
  type: reference
  originSessionId: 54969856-a86b-4908-aeb5-93c9b166999f
---

2026-06-27: `deckhand/scripts/review/send-fixture.py` (the live fixture/operator
sender) sends **as the operator = a Telegram USER account** via Telethon
`TelegramClient`, so it needs **MTProto** creds `TELEGRAM_API_ID` +
`TELEGRAM_API_HASH` (from https://my.telegram.org). It reads them, via
`os.environ.setdefault`, from exactly 3 files in order:
`~/.hermes/deckhand/operator.env`, `~/.hermes/deckhand/secrets.env`,
`~/.hermes/.env`. Session persists at `~/.hermes/deckhand/operator` (`.session`).

**The trap:** `~/.hermes/.env` only has `TELEGRAM_BOT_TOKEN` (Bot API — a DIFFERENT
auth system Telethon's user client can't use) + `TELEGRAM_ALLOWED_USERS`. The two
`deckhand/*.env` files don't exist; api_id/hash aren't in `config.yaml` either; no
`operator.session` exists → operator has NEVER logged in on this box. Error:
`TELEGRAM_API_ID/HASH not found in env files`.

**Fix:** (1) get api_id/api_hash from my.telegram.org → write
`~/.hermes/deckhand/secrets.env` with `TELEGRAM_API_ID=` / `TELEGRAM_API_HASH=`.
(2) Run the send ONCE interactively (user must, via `! <cmd>` — Telethon prompts
for phone + login code + maybe 2FA); that mints `operator.session`, after which
sends are non-interactive. Faster alt: copy an existing `operator.session` + the
two creds from a box where the operator already logged in (e.g. ace-linux-1).
Agent CANNOT do the interactive login. Note: grepping multiple ~/.hermes secret
files for API_ID/API_HASH trips the credential-exploration classifier — inspect
key NAMES only (`cut -d= -f1`), not values. See [[project_share_live_session_skill]],
[[reference_claude_hooks_cannot_see_spend]].
