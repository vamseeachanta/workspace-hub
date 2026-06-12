---
name: crossprovider hermes system-cron-and-hermes-scheduler-routing-boundar
description: System cron and Hermes scheduler routing boundary is undefined
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [scheduler-routing, cron-gap, hermes-contract]
---

Session 13 identified gap: native Claude cron jobs do not route through Hermes agent by default; system cron (/etc/cron.d) and Hermes gateway have no explicit contract. Created issue #2762 to define routing boundaries. Gsd-researcher and other native schedulers need explicit Hermes-vs-system decision.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
