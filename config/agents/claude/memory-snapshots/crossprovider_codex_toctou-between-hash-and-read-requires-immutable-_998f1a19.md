---
name: crossprovider codex toctou-between-hash-and-read-requires-immutable-
description: TOCTOU between hash and read requires immutable binding
metadata:
  type: reference
  source: codex
  bridged: 2026-07-14
  tags: [concurrency, snapshot-consistency, sqlite]
---

If a snapshot SHA-256 is computed offline and rows later read from a live database connection, mutations between the hash and read are undetected. Bind hashing and reading to the same immutable transaction or file identity; reject journal/WAL/SHM sidecars; test mutation post-verification.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
