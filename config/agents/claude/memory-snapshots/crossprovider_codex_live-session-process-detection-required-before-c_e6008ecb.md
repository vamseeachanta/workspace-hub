---
name: crossprovider codex live-session-process-detection-required-before-c
description: Live-session process detection required before config mutations in shared systems
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [live-systems, daemon-safety, configuration]
---

Applying config changes to a machine running live daemons (e.g., a2 with Telegram/WhatsApp/deckhand) needs explicit daemon detection and opt-in (--apply --allow-live-reload) or safe staging, not just backup capability. Config reload semantics must be documented before apply is allowed.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
