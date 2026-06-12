---
name: crossprovider hermes telegram-hermes-dispatch-requires-multi-layer-ho
description: Telegram/Hermes dispatch requires multi-layer host-side gating
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [hermes, telegram, readiness-gating]
---

Repo-side verifier/tests (#2738) can pass independently, but dispatch enablement requires: (1) env-file setup with `GATEWAY_ALLOW_ALL_USERS` control, (2) systemd env wiring with `TimeoutStopSec >= 210`, (3) duplicate poller resolution, (4) explicit state-clean before dispatch. No single layer is sufficient.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
