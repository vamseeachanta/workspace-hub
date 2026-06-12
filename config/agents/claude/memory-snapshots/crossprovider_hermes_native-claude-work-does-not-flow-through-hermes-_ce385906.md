---
name: crossprovider hermes native-claude-work-does-not-flow-through-hermes-
description: Native Claude work does not flow through Hermes by default
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [provider-routing, hermes-integration, architecture]
---

Provider-session-ecosystem-audit (2026-05-20) confirmed independent session logs: claude (111628 records), hermes (305688 records), codex, gemini—all separate backends. Native Claude maintains its own routing; work is NOT auto-forwarded to Hermes agent. Clarify routing contract between native providers and Hermes gateway to avoid blind spots.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
