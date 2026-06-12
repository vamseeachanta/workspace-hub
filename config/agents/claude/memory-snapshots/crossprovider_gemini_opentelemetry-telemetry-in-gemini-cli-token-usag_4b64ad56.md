---
name: crossprovider gemini opentelemetry-telemetry-in-gemini-cli-token-usag
description: OpenTelemetry telemetry in Gemini CLI: token usage and API call counts
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [observability, gemini-cli]
---

Gemini CLI tracks usage via OpenTelemetry metrics: `gemini_cli.token.usage` (input/output/thought/cache), `gemini_cli.api.request.count` (all requests). Configured in `.gemini/settings.json` (enable, target, outfile). Can export to Google Cloud Monitoring or local log files.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
