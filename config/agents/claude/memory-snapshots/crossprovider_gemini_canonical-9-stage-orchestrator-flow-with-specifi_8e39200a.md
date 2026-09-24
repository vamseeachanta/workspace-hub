---
name: crossprovider gemini canonical-9-stage-orchestrator-flow-with-specifi
description: Canonical 9-stage orchestrator flow with specific stage log points
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [orchestration, stages, audit, logging]
---

Orchestrator workflow: Capture → Resource Intelligence → Triage → Plan → Claim → Execute → Review → Close → Archive. Each stage produces a log event (YAML key-value format: timestamp/wrk_id/stage/action/provider/notes). Stage logs are the audit trail; their format must be standardized. Deviations like Gemini's ISO+INFO format are documented as drift requiring normalization.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
