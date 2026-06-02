# Deckhand — member onboarding guide (living doc)

> One section **per connected platform**. Keep it current as platforms come online and as we
> learn onboarding details. Host: ace-linux-2. Issue: [#2937](https://github.com/vamseeachanta/workspace-hub/issues/2937) (sub-issue of [#2931](https://github.com/vamseeachanta/workspace-hub/issues/2931)).
> Tooling: `scripts/deckhand/add-member.sh`, `/whoami`, `scripts/deckhand/protect-and-verify.sh verify-pat`.

## Model (all platforms)
Two authorization layers + the same guards everywhere:
1. **Gateway allowlist** — who may talk to the bot at all (per-platform `*_ALLOWED_USERS`). **Gateway stays CLOSED** (owner decision 2026-06-01): no `GATEWAY_ALLOW_ALL_USERS`.
2. **Scope authorization** — which channel/scope a message operates on:
   - **Route A** — explicit `operators` (stable platform ID) in `config/deckhand/scopes.yml`, optionally a DM channel→repo binding.
   - **Route B** — a **group bound to a scope** (`authorize_members: true`): any group member is authorized for that scope.
3. **Always enforced:** scope repo-allowlist, no-destructive, per-scope fine-grained **PAT** (real boundary; out-of-scope repo → 404), full audit. `execute_code` re-entry is gated.

**Golden rule:** the *owner* confirms every member by **name + numeric ID** before authorization — never auto-grant from group presence (a safety gate enforces this).

---

## Telegram — CONNECTED ✅  (bot: `@the_deckhand_bot`)

**Channels (group → scope):**

| Channel | Telegram group chat_id | Scope | Repos |
|---|---|---|---|
| acma | `-5109954935` | acma | `llm-wiki-acma` |
| doris | `-5211977662` | doris | `llm-wiki-doris` (write) + `doris` (read-only ref) |

**Prerequisites (one-time):** bot live; bot added to each channel group; **group privacy OFF** (BotFather `/setprivacy` → Disable) so member IDs are capturable from the log; per-scope PAT in `~/.hermes/.env` (`DECKHAND_PAT_ACMA`, `DECKHAND_PAT_DORIS`).

**Add a member (gateway-closed):**
1. **Capture their numeric ID** (any of):
   - They post in the channel group → with privacy OFF, the gateway logs it. Capture with:
     `grep -oE "telegram:group:-[0-9]+:[0-9]+" ~/.hermes/logs/*.log | sort -u`
     and names via `grep -oE "Unauthorized user: [0-9]+ \([^)]*\)" ~/.hermes/logs/*.log`.
   - Or the member runs **`/whoami`** in the group (only works if already allowlisted — confirms ID).
   - Or the member messages **@userinfobot** (separate bot; works for brand-new members) and relays the `Id`.
2. **Owner confirms** the person (name + ID) for the intended channel.
3. **Authorize:** `scripts/deckhand/add-member.sh <numeric_id> --apply` (add `--scope acma|doris` only for route-A explicit operators; route B via group needs only the allowlist add).
4. **Restart:** `hermes gateway restart`.
5. Member is in the channel group → operates on that scope. Verify isolation:
   `HERMES_SESSION_USER_ID=<id> HERMES_SESSION_PLATFORM=telegram HERMES_SESSION_CHAT_ID=<group_id> PYTHONPATH=src python3 -m deckhand.shim_resolve` → expect the scope's `DECKHAND_PAT_*`.

**Remove a member:** delete their ID from `TELEGRAM_ALLOWED_USERS` (and any scope `operators`) → restart. (A `remove-member` helper is a TODO.)

**Onboarded so far:**
| Name | ID | Channel | Date |
|---|---|---|---|
| Vamsee Achanta (owner) | 8748731589 | acma + doris | 2026-06-01 |
| Vamsi Galigutta | 448087190 | doris | 2026-06-01 |

**Gotchas learned:**
- Group inbound logs show the **display name, not the numeric ID** — capture IDs via the `telegram:group:<chat>:<id>` log token (privacy-off), `/whoami`, or @userinfobot.
- A safety gate **blocks auto-adding** an ID scraped from logs — owner must explicitly confirm each member.
- Gateway closed → a brand-new (non-allowlisted) member **cannot reach the bot**, so `/whoami` can't bootstrap them; use @userinfobot or log-capture-on-(privacy-off)-post for the first contact.

---

## WhatsApp — NOT CONNECTED (stub)
Connect first (#2901): `hermes whatsapp` → QR pair (unofficial-API/ban risk). Member ID = E.164 number; allowlist var `WHATSAPP_ALLOWED_USERS`. Onboarding mirrors Telegram once connected. *(Fill in when live.)*

## Signal — NOT CONNECTED (stub)
Connect first: install `signal-cli` + Java, link device, run daemon, `SIGNAL_*`. Member ID = phone number; `SIGNAL_ALLOWED_USERS`. *(Fill in when live.)*

## Microsoft Teams — NOT CONNECTED (stub)
Connect first: Azure app registration + public HTTPS webhook; `TEAMS_CLIENT_ID/SECRET/TENANT_ID`. Member ID = AAD object id; `TEAMS_ALLOWED_USERS`. *(Fill in when live.)*

---

## Cross-platform identity note
One person = one ID **per platform** (no unified person-registry yet — roadmap). Authorize each platform identity separately. Audit records the actual operator ID + platform per decision.
