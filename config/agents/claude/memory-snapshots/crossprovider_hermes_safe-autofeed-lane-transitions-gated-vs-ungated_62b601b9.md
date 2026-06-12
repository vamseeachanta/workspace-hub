---
name: crossprovider hermes safe-autofeed-lane-transitions-gated-vs-ungated
description: Safe autofeed lane transitions: gated vs. ungated
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [autofeed, lanes, automation, gates]
---

Safe transitions: draft→review, MAJOR review→patch-lane, MINOR/APPROVE→status-update-pack, blocked→blocker-prep. Gated (forbidden without explicit approval): no `status:plan-approved` label mutations, no outreach, no unapproved implementation. Limit autofeed to 1-2 new lanes per tick with unique prompt/log/result paths.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
