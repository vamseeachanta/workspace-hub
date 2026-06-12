---
name: crossprovider hermes data-execution-report-layers-must-be-isolated-in
description: Data/execution/report layers must be isolated into separate GitHub issues
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [architecture, github-issues, layering, data-governance, legal]
---

Architecture review requires three child issues per layer to prevent cross-layer contamination: Data (raw sources, llm-wiki promotion model), Execution (tools, compute, input routing), Report (client HTML/PDF, chatbots). Legal/IP sanity checks mandatory before public-facing artifact promotion. Avoid leaking private data into public repos.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
