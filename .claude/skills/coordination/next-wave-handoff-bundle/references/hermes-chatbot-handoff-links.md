# Hermes chatbot handoff links

Use this reference when building a handoff prompt for Hermes/Deckhand multi-channel chatbot routing, gateway delivery, or bot wiring work.

## What to include in the handoff

1. **Full board inventory**
   - Board/list name.
   - Every ready task ID and title.
   - Linked GitHub issue URL for each task.
   - The intended planning/execution lane for each task.
   - Any known gate state: `status:plan-review`, `status:plan-approved`, blocked, or validation-only.

2. **Hermes documentation section**
   - Start from the docs home: <https://hermes-agent.nousresearch.com/docs>
   - Include the current installed/local docs path when available, commonly under `~/.hermes/hermes-agent/website/docs` or the checked-out Hermes Agent repository.
   - Link or cite the specific docs pages for the platforms in scope. For multi-channel routing work, usually verify and include: messaging/gateway overview, Telegram, WhatsApp, Microsoft Teams bot, Teams Meetings, Microsoft Graph webhook, Signal, Discord, Slack, Webhooks, daily briefing bot, gateway CLI reference, and Kanban/board docs.
   - Do not rely on remembered URL slugs; inspect the local docs tree or website before finalizing the handoff.

3. **Fanout/current-state evidence**
   - State whether the current Hermes gateway already supports multi-target routing conceptually.
   - Point the next operator at the relevant gateway delivery/router and scheduler files if known.
   - Separate configured/currently-working transports from planned or unconfigured transports.
   - For a user who currently has Telegram working, make clear that simultaneous Telegram + WhatsApp + Teams emission is a routing/configuration question, not proof that the latter two are already configured.

4. **Verification after edit**
   - Re-open or refresh the prompt artifact if the user is actively viewing it.
   - Verify file size or checksum and grep for the key new section headings.
   - Report only the sections actually present in the saved artifact.

## Pitfalls

- Do not hand off only the primary GitHub issue when the user asked for the whole chatbot board.
- Do not bury documentation links at the bottom; put them near the top where a fresh operator sees them before drafting or reviewing plans.
- Do not claim WhatsApp/Teams are configured just because Telegram works or the docs exist.
- Do not claim exact Hermes documentation paths from memory. Verify the local docs tree or docs site first when tool access permits.
