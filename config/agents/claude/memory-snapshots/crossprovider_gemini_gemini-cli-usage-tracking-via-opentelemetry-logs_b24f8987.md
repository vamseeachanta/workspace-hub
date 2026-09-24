---
name: crossprovider gemini gemini-cli-usage-tracking-via-opentelemetry-logs
description: Gemini CLI usage tracking via OpenTelemetry logs
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [gemini-cli, observability]
---

Gemini CLI does not expose a built-in `gemini usage` command. Usage metrics must be extracted from OpenTelemetry logs configured in `.gemini/settings.json`. Integration with Google Cloud Monitoring or local log parsing required for quota tracking.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
