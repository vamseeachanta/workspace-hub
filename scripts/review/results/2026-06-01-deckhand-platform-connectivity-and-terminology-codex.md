## PART A — platform connectivity

Live status was partially verified on ace-linux-2: `hermes gateway status` and `hermes gateway list` work, but report the default gateway is not running. `gateway status` also printed `Failed to connect to bus: No data available`, so service-manager reachability is not fully clean. `~/.hermes/channel_directory.json` currently has empty target lists for all relevant platforms.

| Platform | Current State | Required Setup | Blockers / Risks | Effort / Owner |
|---|---|---|---|---|
| Telegram | Not enabled/configured. `~/.hermes/config.yaml` has top-level `telegram:` options only; no active `TELEGRAM_*` names in `~/.hermes/.env`; no discovered channels. | Create bot via BotFather, set `TELEGRAM_BOT_TOKEN`, `TELEGRAM_ALLOWED_USERS`; optional `TELEGRAM_HOME_CHANNEL`, `TELEGRAM_WEBHOOK_URL`, `TELEGRAM_WEBHOOK_SECRET`, `TELEGRAM_WEBHOOK_PORT`. Start with `hermes gateway start` or foreground `hermes gateway run`. Docs: `/home/vamsee/.hermes/hermes-agent/website/docs/user-guide/messaging/telegram.md`. | Group behavior needs BotFather privacy/admin settings. Webhook mode needs public HTTPS; polling avoids inbound exposure. | **S**. Owner creates bot/token and supplies allowed user IDs; agent can configure/restart once secrets exist. |
| WhatsApp | Partially enabled but not paired. Active env name: `WHATSAPP_ENABLED`. Live status says: “WhatsApp enabled but not paired — run `hermes whatsapp` to pair.” `~/.hermes/whatsapp/session/` exists but no `creds.json`; Node/npm are installed. | Run `hermes whatsapp`, choose mode, scan QR from WhatsApp Linked Devices. Set `WHATSAPP_ALLOWED_USERS` or `WHATSAPP_ALLOW_ALL_USERS`; optional `WHATSAPP_MODE`, `WHATSAPP_HOME_CHANNEL`, `WHATSAPP_DEBUG`. Restart gateway after pairing. Adapter preflight requires `creds.json`: `/home/vamsee/.hermes/hermes-agent/gateway/platforms/whatsapp.py`. | Unofficial Baileys/WhatsApp Web bridge, not Business API; ban/account restriction risk. Needs owner phone/QR action. Current access-control state is risky/incomplete because only `WHATSAPP_ENABLED` is active. | **M**. Owner must scan QR and decide bot vs self-chat; agent can verify/restart. |
| Signal | Not enabled/configured. No active `SIGNAL_*` names; `signal-cli` not on PATH; no discovered channels. | Install `signal-cli` + Java 17+, link device with `signal-cli link -n "HermesAgent"`, start daemon: `signal-cli --account +NUMBER daemon --http 127.0.0.1:8080`. Set `SIGNAL_HTTP_URL`, `SIGNAL_ACCOUNT`, `SIGNAL_ALLOWED_USERS`; optional `SIGNAL_GROUP_ALLOWED_USERS`, `SIGNAL_HOME_CHANNEL`, `SIGNAL_ALLOW_ALL_USERS`. Docs: `/home/vamsee/.hermes/hermes-agent/website/docs/user-guide/messaging/signal.md`. | Needs Signal account/device linking and a persistent daemon. Duplicate signal-cli listeners for same number can break delivery. Account credentials live under signal-cli state and need protection. | **M**. Owner links Signal device; agent can install/configure daemon if authorized. |
| Microsoft Teams | Plugin exists, but not configured/enabled. No active `TEAMS_*` names; `teams`, `devtunnel`, `ngrok`, `cloudflared` not on PATH. Teams adapter is a plugin at `/home/vamsee/.hermes/hermes-agent/plugins/platforms/teams/adapter.py`, not `gateway/platforms/teams.py`. | Install Teams CLI: `npm install -g @microsoft/teams.cli@preview`; run `teams login`; expose public HTTPS to local `TEAMS_PORT` default `3978`; create bot with `teams app create --endpoint https://.../api/messages`; set `TEAMS_CLIENT_ID`, `TEAMS_CLIENT_SECRET`, `TEAMS_TENANT_ID`, `TEAMS_ALLOWED_USERS`; optional `TEAMS_HOME_CHANNEL`, `TEAMS_PORT`. | Requires public HTTPS endpoint and valid Microsoft/Azure tenant app registration. Bot Framework endpoint must stay stable. | **L**. Owner must authenticate to Microsoft tenant and approve app setup; agent can install CLI/configure after credentials. |
| Teams vs `msgraph_webhook` | Distinct surfaces. `teams` is the chat bot humans type to. `msgraph_webhook` is an inbound Microsoft Graph change-notification listener. | For Graph events/meeting pipeline, configure `platforms.msgraph_webhook.extra` or env names: `MSGRAPH_WEBHOOK_ENABLED`, `MSGRAPH_WEBHOOK_PORT`, `MSGRAPH_WEBHOOK_CLIENT_STATE`, `MSGRAPH_WEBHOOK_ACCEPTED_RESOURCES`, `MSGRAPH_WEBHOOK_ALLOWED_SOURCE_CIDRS`. Docs: `/home/vamsee/.hermes/hermes-agent/website/docs/user-guide/messaging/msgraph-webhook.md`. | Graph requires public HTTPS and `clientState`; non-loopback bind requires source CIDR allowlist. This does not replace the Teams chatbot. | Add only if Deckhand needs M365 event ingress or meeting summaries. |

Ordered work list:

1. Bring gateway service up cleanly: resolve the bus/service-manager issue, then run `hermes gateway start` or `hermes gateway run --accept-hooks`; verify `hermes gateway status`.
2. Telegram first: lowest friction. Create BotFather bot, configure token + allowlist, restart, message bot, verify `channel_directory`.
3. WhatsApp second: run `hermes whatsapp`, scan QR, add `WHATSAPP_ALLOWED_USERS`, restart, verify pairing and inbound/outbound.
4. Signal third: install/link/start `signal-cli` daemon, configure `SIGNAL_*`, restart, verify `curl /api/v1/check` and a Signal DM.
5. Teams last: tenant/app/public HTTPS work is the longest. Configure Teams bot separately from `msgraph_webhook`.
6. Add `msgraph_webhook` only for meeting/event pipeline needs, not for normal Deckhand operator chat.

## PART B — terminology alignment

| Deckhand Term | Alignment | Hermes Usage / Evidence | Recommendation |
|---|---|---|---|
| Scope | **NO Hermes equivalent** | Hermes platform config is transport-oriented; no repo authorization domain in inspected gateway files. | Keep, but define as Deckhand-only repo/action authorization domain. |
| Channel | **MATCH** | `channel_directory.py` describes “reachable channels/contacts per platform” and resolves channel names; `send_message_tool.py` sends to “user or channel” and lists “channels/contacts”. | Keep. It matches Hermes transport-target usage. |
| Delivery group | **NO direct equivalent** | Hermes has `DeliveryTarget` as a single destination and `DeliveryRouter.deliver(... targets: List[DeliveryTarget])` in `gateway/delivery.py`; no named grouping term found. | Keep, but annotate: “a Deckhand named set of Hermes delivery targets.” |
| Fanout | **NO named Hermes equivalent** | Hermes delivery loops across a list of targets and records per-target results, but does not appear to name that “fanout”. | Keep, but annotate as Deckhand behavior implemented over multiple Hermes delivery targets. |
| Permission level | **POTENTIAL CONFLICT if confused with gateway auth** | Hermes uses `*_ALLOWED_USERS`, `*_ALLOW_ALL_USERS`, pairing, and platform allowlists for who may use a gateway; not repo read/write permission. | Keep, but explicitly say it is repo/action permission, not Hermes platform access control. |
| Destructive operation | **NO direct Hermes equivalent** | Teams plugin docs/code refer to approval cards for dangerous commands; Hermes has approval/session concepts, but not this repo-specific destructive-operation taxonomy. | Keep. It is Deckhand policy language. |
| Operator | **PARTIAL MATCH / NO exact term** | Hermes docs mostly use user/sender/allowed users; `channel_directory.py` uses origin user/chat names from sessions. | Keep, but annotate as “authenticated Hermes gateway user/contact authorized for Deckhand.” |
| Sensitivity / Clearance | **NO Hermes equivalent** | No inspected Hermes gateway term for data classification or delivery eligibility by sensitivity. | Keep. This is Deckhand leakage-control vocabulary. |

Potential wording friction:

- “Channel” is fine. Hermes uses it for transport targets, and Deckhand uses the same meaning.
- “Delivery group” should not be shortened to “channel” or “target”; Hermes already uses “target” for one destination.
- “Permission level” must not be described as a Hermes role/allowlist. Hermes allowlists answer “who can talk to the bot”; Deckhand permission levels answer “what repo actions are allowed.”

## Recommended CONTEXT.md adjustments

- Keep `scope`, `channel`, `delivery group`, `fanout`, `permission level`, `operator`, `sensitivity/clearance`, and `destructive operation`.
- Add one sentence under `delivery group`: “A delivery group is Deckhand terminology; in Hermes terms it expands to multiple `DeliveryTarget`s / `send_message` targets.”
- Add one sentence under `permission level`: “This is independent of Hermes `*_ALLOWED_USERS` / pairing access control.”
- Add one sentence under `operator`: “Maps to a Hermes authenticated platform sender/contact, usually controlled by `*_ALLOWED_USERS` or pairing.”
- Add a note near Teams language: “Teams chatbot (`teams` platform plugin) is separate from `msgraph_webhook`, which is Microsoft Graph event ingress for meeting/event pipelines.”

UNVERIFIED: actual end-to-end reachability for every platform, because the gateway is currently stopped and channel directory entries are empty. Cleanup audit surfaced only pre-existing dirty workspace state and `/tmp` cache/scratch files; I made no writes.
