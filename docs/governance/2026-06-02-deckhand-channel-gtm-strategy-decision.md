# Strategy note (recommendation): Deckhand channel GTM — Telegram-led, other channels demand-driven

> **Date:** 2026-06-02
> **Owner:** Vamsee Achanta
> **Epic:** [#2931](https://github.com/vamseeachanta/workspace-hub/issues/2931) (Deckhand) · relates [#2939](https://github.com/vamseeachanta/workspace-hub/issues/2939) (WhatsApp), [#2940](https://github.com/vamseeachanta/workspace-hub/issues/2940) (WhatsApp dedicated identity), [#2941](https://github.com/vamseeachanta/workspace-hub/issues/2941) (Teams)
> **Status:** RECOMMENDED DIRECTION — owner leaning this way (raised 2026-06-02); not formally ratified. The only *firm* call as of 2026-06-02 is: leave the WhatsApp POC running as-is and decide later.

## Recommended direction (agent recommendation; owner leaning, pending ratification)

**Make Telegram the primary go-to-market and demonstration channel for Deckhand, and treat all other transports (WhatsApp, Signal, Teams, …) as demand-driven** — stood up per client engagement, with the client deciding its own number/identity and the engagement funding the official, no-ban integration path.

Corollary recommendation: **do not** acquire a speculative second phone number to give WhatsApp a dedicated "Deckhand" identity for the POC. (Owner had not ratified this as final at time of writing — captured as the leaning direction.)

## Why

- **Telegram already provides the ideal identity model for free.** Its Bot API mints a phone-less bot account (`@the_deckhand_bot`) that is inherently separate from any human operator — the exact "two identities" property we want — at zero cost and zero ban risk. It is live with the acma and doris scopes.
- **WhatsApp cannot replicate that cheaply.** WhatsApp has no phone-less bot account; every identity is a phone number. A separate "Deckhand" identity therefore requires either (a) a dedicated number on the unofficial Baileys protocol (ban risk) or (b) the official WhatsApp Business Cloud API (Meta verification + conversation pricing). Pre-investing in either for a POC is negative ROI.
- **Demand-driven channel rollout is a stronger enterprise story**, not a weaker one: "we meet your team on whatever channel it already uses, and that channel carries its own identity." It also matches the multi-tenant, build-for-an-industry posture — no per-channel cost or risk is borne speculatively.

## What this means operationally

- **GTM/marketing:** lead with Telegram. The GTM deck's enterprise-platform sections (e.g. `docs/gtm/deckhand-teams-enterprise-connectivity.html`) frame non-Telegram channels as client-elected, client-funded, on official rails.
- **WhatsApp ([#2939](https://github.com/vamseeachanta/workspace-hub/issues/2939)):** remains *supported and live* but deprioritized to demand-driven. The current POC bridge stays running on the owner's personal number **as-is** (ban risk explicitly accepted, 2026-06-02 owner decision — "leave it running, decide later"). No migration is forced.
- **WhatsApp dedicated identity ([#2940](https://github.com/vamseeachanta/workspace-hub/issues/2940)):** if this direction is ratified, the 2026-06-08 migration deadline would relax to demand-driven. **Not yet changed on the issue** (owner said "decide later"). When a client actually needs WhatsApp, prefer the **official Business Cloud API** (verified "Deckhand" brand, no ban risk) funded by that engagement, over a personal/dedicated Baileys number.
- **Teams ([#2941](https://github.com/vamseeachanta/workspace-hub/issues/2941)):** unchanged — internal-only, client reviews the ingress decision (D2). Consistent with "the channel decides its own identity/infra."

## Reversibility

Fully reversible. Re-enabling or upgrading any channel is configuration, not redesign. This decision sets *priority and spend posture*, not capability — the adapters remain available.
