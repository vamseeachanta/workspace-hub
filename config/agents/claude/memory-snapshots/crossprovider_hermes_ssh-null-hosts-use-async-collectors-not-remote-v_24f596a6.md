---
name: crossprovider hermes ssh-null-hosts-use-async-collectors-not-remote-v
description: SSH-null hosts use async collectors, not remote verification
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [multi-machine-automation, windows-hosts, async-verification]
---

Windows simulation license hosts with `ssh: null` cannot be verified/configured remotely; use async collectors that save output to a known git-reachable location. The main machine observes outputs asynchronously via git pull/queue patterns.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
