---
name: crossprovider hermes lease-atomicity-must-span-local-remote-github-bo
description: Lease atomicity must span local + remote + GitHub boundaries
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [distributed-systems, lease-semantics, idempotency, ace-linux]
---

Distributed cron workers need leases that are atomic across: local flock, remote git ref (non-force), and GitHub comment marker. Single-layer leases (comment-only or flock-only) leave race windows. Acceptance criteria must prove reentrancy, idempotency, and recovery semantics.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
