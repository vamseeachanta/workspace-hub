---
name: crossprovider hermes multi-account-email-architecture-gmail-mcp-multi
description: Multi-account email architecture: gmail-mcp-multiauth + himalaya fallback
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [email, gmail, architecture]
---

For multi-account Gmail access, primary tool is gmail-mcp-multiauth (381K downloads/mo, purpose-built for 3+ accounts via named MCP servers + OAuth2). Fallback is himalaya CLI for cron jobs (App Password auth, no OAuth needed). No MCP server has native unsubscribe — must parse List-Unsubscribe headers manually.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
