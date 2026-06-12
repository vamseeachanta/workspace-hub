---
name: crossprovider hermes telegram-is-dispatch-plane-github-is-canonical-s
description: Telegram is dispatch plane, GitHub is canonical sync source
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [distributed-systems, dispatch, source-of-truth]
---

Multi-machine dispatch must not treat Telegram messages as source of truth. Canonical sync belongs in GitHub issues/comments/labels, git-backed repo state, and explicit job/host routing records. Telegram is notification/dispatch only.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
