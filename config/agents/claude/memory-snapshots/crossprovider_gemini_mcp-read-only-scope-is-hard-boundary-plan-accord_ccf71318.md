---
name: crossprovider gemini mcp-read-only-scope-is-hard-boundary-plan-accord
description: MCP read-only scope is hard boundary; plan accordingly
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [mcp-scope, gmail-integration, auth-boundaries]
---

Gmail MCP is read+compose only; Gmail-side deletion/modification requires re-auth for gmail.modify scope. Clarify at plan time what's MCP-scoped vs requires different auth flow. Example: local queue state deletion is in-scope, Gmail inbox hygiene stays with user via Gmail UI.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
