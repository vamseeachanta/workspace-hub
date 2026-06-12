---
name: crossprovider codex remote-host-evidence-requires-type-producer-time
description: Remote host evidence requires type, producer, timestamp, and identity validation
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [remote-dispatch, security, validation]
---

Single-field JSON fragments are insufficient for remote dispatch gates. Require evidence type, producer identity, freshness timestamp, hostname/alias match, and explicit host-local check results. Reject handcrafted minimal payloads.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
