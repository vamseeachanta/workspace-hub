---
name: crossprovider codex gemini-cli-authentication-requires-interactive-b
description: Gemini CLI authentication requires interactive browser flow (exit 41) in non-interactive sessions
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [gemini, authentication, review-gates]
---

The Gemini CLI requires interactive OAuth; in non-interactive sessions it exits with code 41. This degrades T3 (3-provider) review gates to T2 (2-provider). Document the unavailable status rather than substituting an unverified verdict.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
