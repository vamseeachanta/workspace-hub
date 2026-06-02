# Deckhand WhatsApp Identity Recon

Issue: #2939
Date: 2026-06-01

## Scope

Read-only inspection of:

- `/home/vamsee/.hermes/hermes-agent/gateway/platforms/whatsapp.py`
- `/home/vamsee/.hermes/hermes-agent/gateway/session_context.py`
- `/home/vamsee/.hermes/hermes-agent/gateway/run.py`
- supporting read-only evidence from the WhatsApp bridge/CLI and Deckhand resolver code

No WhatsApp pairing was performed. No gateway, `~/.hermes`, or plugin files were modified.

## Runtime Session Identity

When a WhatsApp message arrives:

- `HERMES_SESSION_PLATFORM` is exactly `whatsapp`.
  - `Platform.WHATSAPP = "whatsapp"` in `/home/vamsee/.hermes/hermes-agent/gateway/config.py:100-111`.
  - `WhatsAppAdapter.__init__` passes `Platform.WHATSAPP` to the base adapter in `/home/vamsee/.hermes/hermes-agent/gateway/platforms/whatsapp.py:250-251`.
  - Gateway session vars use `context.source.platform.value` in `/home/vamsee/.hermes/hermes-agent/gateway/run.py:15205-15223`.

- `HERMES_SESSION_CHAT_ID` is the bridge `chatId` exactly as emitted by Baileys.
  - The bridge sets `chatId = msg.key.remoteJid` in `/home/vamsee/.hermes/hermes-agent/scripts/whatsapp-bridge/bridge.js:252`.
  - It classifies groups with `chatId.endsWith('@g.us')` in `/home/vamsee/.hermes/hermes-agent/scripts/whatsapp-bridge/bridge.js:263-264`.
  - The bridge event includes that `chatId` unchanged in `/home/vamsee/.hermes/hermes-agent/scripts/whatsapp-bridge/bridge.js:423-429`.
  - The adapter builds the Hermes source with `chat_id=data.get("chatId", "")` in `/home/vamsee/.hermes/hermes-agent/gateway/platforms/whatsapp.py:1278-1284`.

Expected format:

- WhatsApp group chat: group JID, for example `<group-id>@g.us`.
- WhatsApp DM chat: contact/self JID, typically `<number>@s.whatsapp.net` or a LID-shaped JID depending on Baileys/runtime state.

- `HERMES_SESSION_USER_ID` is the bridge `senderId` exactly as emitted, not normalized to E.164 by the adapter.
  - The bridge sets `senderId = msg.key.participant || chatId` in `/home/vamsee/.hermes/hermes-agent/scripts/whatsapp-bridge/bridge.js:263`.
  - For groups, `msg.key.participant` is expected, so sender IDs are participant JIDs such as `<number>@s.whatsapp.net` or `<lid>@lid`.
  - For DMs, sender ID falls back to the chat JID, commonly `<number>@s.whatsapp.net` or a LID-shaped JID.
  - The adapter passes `user_id=data.get("senderId")` to `build_source` in `/home/vamsee/.hermes/hermes-agent/gateway/platforms/whatsapp.py:1278-1284`.

## Deckhand Resolver Compatibility

Group authorize-member bindings should work unchanged if `config/deckhand/scopes.yml` stores the exact WhatsApp group `chatId` JID.

Evidence:

- The plugin reads `HERMES_SESSION_PLATFORM`, `HERMES_SESSION_CHAT_ID`, and `HERMES_SESSION_USER_ID` from session context in `scripts/deckhand/hermes-plugin/deckhand-scope/__init__.py:260-269`.
- Plugin group resolution matches `binding.platform == identity.platform` and `str(binding.channel_id) == chat_id` for `authorize_members` bindings in `scripts/deckhand/hermes-plugin/deckhand-scope/__init__.py:364-378`.
- The shim resolver uses the same platform/chat exact-match rule for `authorize_members` in `src/deckhand/shim_resolve.py:99-133`.
- WhatsApp group `chatId` is already the exact group JID (`...@g.us`) from the bridge, so no chat-ID normalization is needed for group bindings.

Follow-up risk:

- Operator-specific WhatsApp routes can see `HERMES_SESSION_USER_ID` as a full JID or LID, while Deckhand operators are documented as stable IDs and `config/deckhand/README.md` says WhatsApp E.164. The gateway has WhatsApp alias helpers, but Deckhand plugin/shim do not currently normalize WhatsApp `operator_id`. This is not required for `authorize_members` group bindings, but it is a follow-up for operator-specific WhatsApp matching.

Plugin/shim change needed for this issue:

- No, for WhatsApp group `authorize_members` bindings, as long as the Deckhand `channel_id` is the exact WhatsApp group JID ending in `@g.us`.

## WHATSAPP_ALLOWED_USERS Format

The gateway expects phone-number style values in `WHATSAPP_ALLOWED_USERS`; the bridge and gateway normalize plus/JID syntax internally.

Evidence:

- `hermes whatsapp` prompts for phone numbers and saves `WHATSAPP_ALLOWED_USERS` after removing spaces in `/home/vamsee/.hermes/hermes-agent/hermes_cli/main.py:2010-2039`.
- The bridge reads `WHATSAPP_ALLOWED_USERS` and parses it with `parseAllowedUsers` in `/home/vamsee/.hermes/hermes-agent/scripts/whatsapp-bridge/bridge.js:51-54`.
- `parseAllowedUsers` strips a leading `+`, JID suffixes, and device suffixes in `/home/vamsee/.hermes/hermes-agent/scripts/whatsapp-bridge/allowlist.js:4-18`.
- Gateway config bridges `allow_from` into `WHATSAPP_ALLOWED_USERS` in `/home/vamsee/.hermes/hermes-agent/gateway/config.py:1087-1091`.
- Gateway authorization maps WhatsApp to `WHATSAPP_ALLOWED_USERS` in `/home/vamsee/.hermes/hermes-agent/gateway/run.py:6811-6815` and expands WhatsApp aliases before matching in `/home/vamsee/.hermes/hermes-agent/gateway/run.py:6969-6986`.

Practical add-member format:

- Accept E.164 digits with optional leading `+`, for example `15551234567` or `+15551234567`.
- Do not require callers to enter `@s.whatsapp.net`, `@lid`, or group JID forms for user allowlisting.

## Pairing Steps

Exact pairing flow from the Hermes CLI:

1. Run `hermes whatsapp` in an interactive TTY.
2. Choose mode: separate bot number or personal self-chat (`WHATSAPP_MODE`) per `/home/vamsee/.hermes/hermes-agent/hermes_cli/main.py:1947-1995`.
3. Enter `WHATSAPP_ALLOWED_USERS` phone numbers when prompted in `/home/vamsee/.hermes/hermes-agent/hermes_cli/main.py:2010-2039`.
4. The CLI installs bridge dependencies if needed in `/home/vamsee/.hermes/hermes-agent/hermes_cli/main.py:2043-2079`.
5. If no existing session is kept, it runs `node bridge.js --pair-only --session <session_dir>` in `/home/vamsee/.hermes/hermes-agent/hermes_cli/main.py:2108-2125`.
6. The bridge prints QR pairing mode and starts the socket in `/home/vamsee/.hermes/hermes-agent/scripts/whatsapp-bridge/bridge.js:706-712`; QR display happens in `/home/vamsee/.hermes/hermes-agent/scripts/whatsapp-bridge/bridge.js:203-210`.
7. On success, creds are saved and `WHATSAPP_ENABLED=true` is written only after `creds.json` exists in `/home/vamsee/.hermes/hermes-agent/hermes_cli/main.py:2129-2157`.

This task did not run pairing and did not touch gateway/session state.
