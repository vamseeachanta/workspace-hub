# Hermes Messaging Platform Routing

## Trigger
Use when a user asks whether Hermes can send or receive through multiple chat platforms (Telegram, WhatsApp, Teams, Slack, etc.) or whether scheduled/proactive messages can fan out to more than one bot.

## Key pattern
Hermes has two related but distinct paths:

1. **Gateway/platform adapters** receive inbound messages and expose platform-specific send behavior.
2. **Delivery targets** for cron/proactive output resolve `deliver` strings into concrete platform/chat targets.

Do not treat every platform as identical:

- **Telegram** is commonly configured as a built-in gateway platform and often already has `TELEGRAM_HOME_CHANNEL` / topic configuration.
- **WhatsApp** should be treated as bridge-based and operationally fragile unless verified in the target deployment. If using Baileys or another unofficial Web WhatsApp bridge, document that it is unofficial, may require QR pairing/session persistence, may break when WhatsApp changes behavior, and should use a dedicated bot number rather than a personal number. Use E.164 form (`+15551234567`) for explicit sends/home channel values, but redact real numbers in docs and chat.
- **Microsoft Teams** is not just a local desktop app target. For interactive bot behavior, Teams requires a Teams app/Bot Framework route, Azure app/bot registration, tenant policy approval, a public HTTPS endpoint, and stored conversation references for proactive sends. Incoming webhooks are post-only/demo-oriented and do not provide full conversational bot behavior. A local Teams desktop install only supports manual/deep-link fallback; it does not prove bot readiness.

## Fanout boundaries
For cron/proactive jobs, Hermes delivery may support comma-separated explicit targets and the routing token `all`, depending on the configured runtime. This is **not** the same as live conversation mirroring.

Safe baseline examples:

```text
deliver="origin"
deliver="telegram:-1001234567890:17585"
deliver="telegram:-1001234567890:17585,whatsapp:+15551234567,teams:<conversation-id>"
```

Avoid presenting `deliver="origin,all"` as a normal pattern. `all` is opt-in only: it expands at fire time to every platform with a configured home channel, so jobs created before a platform is wired up can begin delivering there once configuration is added. Do not use `all` for sensitive content without explicit operator approval and a current target inventory.

Interactive `send_message` / inbound conversation replies should be treated as single-target or origin-only unless a separate approved fanout implementation exists. Cross-channel mirroring can leak context between Telegram, WhatsApp, Teams, and other channels.

## Privacy and credential boundary
Never preserve or echo credential values; mention env var names only or redact values as `[REDACTED]`. Also redact platform identifiers when they are not necessary for the answer:

- Telegram bot tokens and numeric chat/user IDs.
- WhatsApp phone numbers, JIDs, QR/session state paths, and bridge credentials.
- Teams webhook URLs, conversation IDs, service URLs, tenant IDs, Azure app/client secrets, and Bot Framework credentials.
- Any `.env` value.

Do not mirror live user conversations across platforms by default. Replies to inbound messages should go only to the originating platform/chat unless the operator explicitly selects additional redacted notification targets. Multi-target cron output is for proactive notifications, not conversation replication.

## Home-channel requirements
Each platform must have a configured home target or it will be skipped by home-channel delivery:

```bash
TELEGRAM_HOME_CHANNEL=...
WHATSAPP_HOME_CHANNEL=+15551234567
TEAMS_HOME_CHANNEL=...
```

Teams plugin metadata also supports:

```bash
TEAMS_CLIENT_ID=...
TEAMS_CLIENT_SECRET=...
TEAMS_TENANT_ID=...
TEAMS_PORT=3978
TEAMS_ALLOWED_USERS=...
TEAMS_ALLOW_ALL_USERS=false
TEAMS_HOME_CHANNEL_NAME=...
```

Never preserve or echo credential values; mention env var names only or redact values as `[REDACTED]`.

## Answering guidance
When answering a user asking "can Hermes emit to Telegram, WhatsApp, and Teams simultaneously":

1. Say **only for explicitly configured and approved delivery targets**, primarily for cron/proactive notifications. Do not imply live conversational mirroring.
2. Distinguish platform maturity/setup:
   - Telegram: commonly configured in many installs, but still verify the active home channel before claiming delivery.
   - WhatsApp: bridge-based; require dedicated bot-number guidance, QR/session persistence, process supervision/reconnect behavior, opt-in recipients, and rate/spam-limit awareness.
   - Teams: requires tenant/app-policy evidence, Azure/Bot Framework registration, admin consent owner, public HTTPS endpoint, secret storage/rotation, and conversation-reference capture for proactive sends. Incoming webhook, Bot Framework bot, and Teams tab are different routes.
3. Note media caveat: generic `send_message` native media delivery is not universally supported for WhatsApp/Teams; text delivery is the safe baseline unless the platform adapter explicitly supports the media type.
4. If exact current behavior matters, verify live config and plugin discovery before making hard claims about a machine.
5. For GitHub planning packages, add an explicit approval gate: planning/research issues are not implementation approval; do not self-label `status:plan-approved`, and do not use labels that imply implementation readiness before canonical plan + adversarial review + user approval.