---
name: crossprovider hermes telegram-is-dispatch-notification-plane-only-git
description: Telegram is dispatch/notification plane only; git/GitHub is sync source of truth
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [dispatch, multi-machine, sync-source]
---

workspace-hub #2720 planning emphasizes that Telegram enables multi-machine command dispatch and notifications, but canonical sync state lives in GitHub issues/labels, git-tracked state, and Hermes/agent configs. Fail-closed on dirty repos, unpushed commits, or unavailable hosts.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
