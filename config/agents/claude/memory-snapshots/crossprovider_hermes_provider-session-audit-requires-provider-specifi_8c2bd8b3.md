---
name: crossprovider hermes provider-session-audit-requires-provider-specifi
description: Provider session audit requires provider-specific tool name mapping, not shared table
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [multi-provider, tool-mapping, export-schema, field-synthesis]
---

Gemini's cli_help and codebase_investigator both export as Read but have different field shapes (cli_help has no file, only question→query; codebase_investigator has objective→query). Hard-coded TOOL_MAP doesn't scale. Need per-provider mapping config that handles missing/synthetic fields (e.g., use response.sources for cli_help instead of exported file).

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
