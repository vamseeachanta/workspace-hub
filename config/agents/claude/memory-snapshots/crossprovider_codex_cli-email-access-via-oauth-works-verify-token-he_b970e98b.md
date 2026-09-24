---
name: crossprovider codex cli-email-access-via-oauth-works-verify-token-he
description: CLI email access via OAuth works; verify token health per account before commit
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [gmail-cli, oauth, context-management]
---

Existing Gmail OAuth setup allows direct CLI access (e.g., `gh` or direct API calls) for accounts with fresh tokens. Token refresh failures (HTTP 400) degrade gracefully to read-only or fail closed on some accounts. Clarify account scope and test token health before committing to large email searches. Abort broad filesystem scans early during mail-context work to preserve context budget.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
