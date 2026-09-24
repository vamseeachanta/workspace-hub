---
name: crossprovider codex remote-evidence-requires-schema-producer-freshne
description: Remote evidence requires schema/producer/freshness, not just status field
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [remote-evidence, security, fail-closed]
---

Handcrafted minimal `{"status": "pass"}` blobs must fail validation. Remote evidence must declare evidence_type, producer, schema_version, hostname match, freshness timestamp, and host-local proof of each required check before being trusted for dispatch eligibility.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
