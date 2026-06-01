# Messaging platform fanout planning reference

Use this reference when planning Hermes Agent work that spans Telegram, WhatsApp, Teams, or other messaging gateway adapters.

## Source to review first

- Hermes Agent Messaging Gateway docs: https://hermes-agent.nousresearch.com/docs/user-guide/messaging/

The docs establish that Hermes uses a single `hermes gateway` background process that can run multiple platform adapters, route inbound messages through a per-chat session store, dispatch to `AIAgent`, expose platform-specific toolsets, and operate adapters with `/platform list`, `/platform pause <name>`, `/platform resume <name>`, circuit breakers, logs, restart notifications, and per-platform configuration.

## Planning pattern

1. Separate **inbound conversation routing** from **outbound notification fanout**.
   - Inbound: `platform chat -> platform adapter -> router/auth scope checks -> per-chat session store -> AIAgent -> origin platform reply`.
   - Explicit fanout: `AIAgent or send_message -> delivery group resolver -> target preflight/redaction -> fanout dispatcher -> platform adapters`.
2. Default conversation behavior should remain **origin-only** unless the plan explicitly introduces a delivery group or fanout target.
3. First implementation plans should be **text-only** unless media fanout/security is separately planned and approved.
4. Treat WhatsApp and Teams as platform-parity surfaces that need live deployment verification, not as equivalent to Telegram just because Telegram already works.
5. Before drafting fanout implementation, produce a platform readiness matrix with at least: adapter availability, configured credentials/session, live send/read verification status, target identifier type, rate-limit/retry behavior, redaction requirements, and operator setup gaps.
6. Model fanout targets as explicit opt-in **delivery groups**. Do not let `send_message` silently broadcast to every configured platform; require a named group or explicit target list that can be preflighted and audited.
7. If the user asks for a board but GitHub Projects scope/readiness is missing, create a Markdown Kanban in the parent plan first and list a real GitHub Project board as a gated follow-up rather than blocking preliminary planning.
8. Include day-2 operations in acceptance criteria: platform pause/resume, adapter circuit-breaker behavior, logs, restart notifications, and operator visibility.
9. Add a Mermaid architecture drawing to the parent/umbrella issue when the user asks for multi-platform message paths. Show platform chats, gateway adapters, router/session store, `AIAgent`, `send_message`, delivery group resolver, fanout dispatcher, and ops/safety controls.

## Naming/product identity subissue

For bot naming requests, create a small design subissue linked to the parent fanout issue instead of burying naming in implementation scope. Seed the issue with:

- A ranked shortlist.
- Display name and lowercase slug expectations.
- Suitability criteria: short in chat, domain-relevant, supportive rather than authority-coded, cross-platform friendly, not gendered, not client-identifying, not legally risky.
- Rejected alternatives with rationale.

For offshore/oil-and-gas context, `Deckhand` is a strong baseline: practical, helpful, crew-member framing, and less authority-coded than terms like `Toolpusher` or `Company Man`.
