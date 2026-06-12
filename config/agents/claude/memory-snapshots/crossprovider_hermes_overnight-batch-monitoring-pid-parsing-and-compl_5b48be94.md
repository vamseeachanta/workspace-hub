---
name: crossprovider hermes overnight-batch-monitoring-pid-parsing-and-compl
description: Overnight batch monitoring: PID parsing and completion rules
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [batch-monitoring, workflow-quirks, hermes-integration]
---

When monitoring overnight Claude/Hermes/Gemini planning batches: read PID files via terminal/Python, not read_file() which prefixes lines with 'N|'. Extract issue numbers from dossier markdown metadata table (handles markdown links like [#2063](url)), not regex-first from body. Completion fires when all expected dossiers exist OR no batch PIDs remain alive, whichever arrives first.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
