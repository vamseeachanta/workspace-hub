# Capacity-Aware Provider Routing

## Session learning

The user's provider-routing preference evolved from a hard rule (Gemini only for reviews) into a telemetry-driven operating model:

- Refresh AI provider usage/capacity roughly every 6 hours before planning the next work wave.
- Avoid rigid provider bans when reliable capacity is available and the work is appropriate.
- Default main execution capacity is Claude Max and Codex because they have substantially higher frontier-model budget.
- Gemini is a lower-budget account and should normally be used for cross-reviews, adversarial reviews, research/recon, and risk scans rather than main implementation work.
- If fresh telemetry shows Gemini capacity and the task is suitable, use it for bounded review/recon work instead of leaving capacity idle.

## Operational implication

Before launching or refilling lanes, the monitor should classify providers by both:

1. **Capacity availability**: recent quota/usage telemetry, provider CLI health, capacity errors, credit errors, and reset timing.
2. **Work fit**: implementation vs review vs research/recon vs governance.

The desired future state is capacity-aware next-work planning: provider assignments are refreshed from telemetry and task fit, not frozen in a static routing table.
