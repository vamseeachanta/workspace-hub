# Plan for #2941: Deckhand — connect Microsoft Teams platform (Bot Framework)

> **Status:** plan-review
> **Complexity:** T2 (multi-file + live infra; external Azure dependency)
> **Date:** 2026-06-01
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2941
> **Client:** N/A (transport/onboarding wiring; touches no wiki content)
> **Project:** —
> **Review artifacts:** pending (T2 → Claude inline + 1 dispatched provider before plan-approved)

---

## Resource Intelligence Summary

### Existing repo code
- Found: `~/.hermes/hermes-agent/plugins/platforms/teams/adapter.py` (1197 lines) + `plugin.yaml` (`teams-platform`) — a **complete Bot Framework adapter** already ships in Hermes. Runs an aiohttp webhook server (default port **3978**); supports Adaptive Card approval prompts; outbound via `incoming_webhook` or `graph` delivery mode.
- Found: `config/deckhand/scopes.yml` — `channel_repo_bindings` already support arbitrary `platform:` values with route-B `authorize_members: true`. WhatsApp recon (#2939) confirmed the binding shape is platform-agnostic; Teams should slot in the same way **pending CHAT_ID-format recon**.
- Found: `scripts/deckhand/add-member.sh` — already parameterized `--platform telegram|whatsapp`; adding `teams` mirrors the WhatsApp branch (allowlist var `TEAMS_ALLOWED_USERS`, id = UPN/AAD object id).
- Found: `scripts/deckhand/hermes-plugin/deckhand-scope/__init__.py` — enforcement hook keys off `HERMES_SESSION_PLATFORM/USER_ID/CHAT_ID`; works for any platform IF the Teams adapter populates those vars in a binding-compatible format.
- Gap: no Teams-specific recon yet of the **inbound** session-identity formats; no public ingress on ace-linux-2.

### Standards
Not applicable (transport/infra wiring; no engineering standard).

### LLM Wiki pages consulted
No relevant wiki pages (no wiki content touched — Client: N/A).

### Documents consulted
- Issue #2941 (this issue) — work breakdown + decision gates.
- Sibling #2939 (WhatsApp connect) — recon pattern that confirmed route B works unchanged on non-Telegram IDs; the model to mirror.
- `docs/deckhand/ONBOARDING.md` — Teams stub: "Azure app registration + public HTTPS webhook; `TEAMS_CLIENT_ID/SECRET/TENANT_ID`; member ID = AAD object id; `TEAMS_ALLOWED_USERS`."
- Live install recon (this session): `plugin.yaml` `requires_env` = `TEAMS_CLIENT_ID/SECRET/TENANT_ID`; optional `TEAMS_PORT`, `TEAMS_ALLOWED_USERS`, `TEAMS_ALLOW_ALL_USERS`. `ss`/`which` confirmed **no cloudflared/ngrok/caddy/nginx and nothing on :3978/:443** → public ingress is net-new.

### Gaps (build from scratch)
1. Public, TLS-terminated, stable HTTPS ingress → ace-linux-2:3978.
2. Azure AD app registration + Azure Bot resource (owner action; may need tenant-admin consent).
3. Teams inbound session-identity recon (the one technical unknown for plugin compatibility).
4. `add-member.sh --platform teams` + tests.
5. Teams route-B bindings in `scopes.yml`; ONBOARDING.md Teams section.

---

## Decision gates (OWNER — block the build)

**D1. External-member identity model.** Teams is tenant-bound (unlike open Telegram/WhatsApp). Options, ranked:
1. **(Recommended) Teams = ecosystem/internal-only** transport; external acma/doris members stay on Telegram/WhatsApp. Lowest org-security blast radius; no guest accounts. Deckhand still gets a Teams channel for internal operators.
2. **Guest users** — invite acma/doris members as guests into the aceengineer Azure AD tenant. Works, but guests gain tenant footprint; needs admin policy review.
3. **Multi-tenant bot** — heaviest; bot accepts any tenant. Broadest exposure; defer.

**D2. Public ingress mechanism.** Options, ranked:
1. **(Recommended) Cloudflare Tunnel (`cloudflared`)** — no inbound firewall hole, stable hostname, free tier, TLS handled. Best fit for a single home/office box.
2. **ngrok** — fastest to demo; free tier has unstable hostnames + session limits (poor for a persistent bot).
3. **Reverse proxy (caddy/nginx) + DNS A-record + Let's Encrypt + port-forward** — most control, most setup + exposes a real inbound port.

## Implementation steps (after D1/D2 approved)
1. **Recon** (Explore/Codex, read-only): trace the Teams adapter inbound path → exact `HERMES_SESSION_PLATFORM` (== "teams"?), `USER_ID` (AAD object id vs UPN), `CHAT_ID` (Bot Framework conversation id format). Decide: plugin/shim unchanged vs normalization. **TDD: write the recon assertions as tests first.**
2. **Azure** (owner): app registration → client id/secret/tenant; create Azure Bot resource; set messaging endpoint = `https://<public>/api/messages`; add Teams channel.
3. **Ingress** (D2 choice): stand up tunnel/proxy → :3978; verify Bot Framework can reach `/api/messages` (JWT-validated by the adapter).
4. **Gateway**: add `TEAMS_*` to `~/.hermes/.env`, enable `teams-platform`, set `TEAMS_ALLOWED_USERS` (gateway-closed; **never** `TEAMS_ALLOW_ALL_USERS`), restart, verify connected.
5. **Bindings**: add Teams `channel_repo_bindings` (route B `authorize_members:true`) for the in-scope channels; capture conversation IDs the same way (member posts → log).
6. **Tooling**: `add-member.sh --platform teams` + bash tests (mirror whatsapp branch).
7. **Parity verification**: force-push DENIED + out-of-scope repo 404 under a Teams session; full audit row written.
8. **Docs**: ONBOARDING.md Teams section stub → live.

## Adversarial review focus (both gates)
- Endpoint threat model: Bot Framework JWT validation actually enforced? Source-CIDR allowlist (adapter references `MSGRAPH_WEBHOOK_ALLOWED_SOURCE_CIDRS` precedent)? Tunnel auth?
- Does the enforcement hook truly fire on the Teams path, or does Adaptive Card / approval flow create a bypass around `pre_tool_call`?
- Gateway-closed invariant: confirm no code path honors `TEAMS_ALLOW_ALL_USERS` implicitly.
- CHAT_ID normalization: a tampered conversation id must not resolve into another scope's binding.

## Out of scope
- Slack/Signal/Discord (separate siblings).
- Adaptive Card destructive-op approval UX (promising follow-up; not POC-critical).

## Status / gate
**This plan is at `status:plan-review`. It must NOT be self-approved.** Owner decides D1 + D2 and applies `status:plan-approved` before any build. T2 cross-review (Claude inline + 1 dispatched provider) runs against this doc before approval.
