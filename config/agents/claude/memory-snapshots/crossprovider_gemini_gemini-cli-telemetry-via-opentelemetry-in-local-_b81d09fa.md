---
name: crossprovider gemini gemini-cli-telemetry-via-opentelemetry-in-local-
description: Gemini CLI telemetry via OpenTelemetry in local files
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [telemetry, quota-tracking, gemini-cli]
---

Gemini CLI supports local file-based telemetry (configured in .gemini/settings.json with outfile, enabled=true, target='local'). Captures model usage, token counts (input/output/cache/thought), and request counts per operation. Enables quota tracking without external dashboard dependency.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
