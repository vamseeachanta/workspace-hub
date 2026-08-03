---
name: crossprovider codex snapshot-attestation-module-boundaries-snapshott
description: Snapshot/attestation module boundaries: snapshotting ≠ manifest
metadata:
  type: reference
  source: codex
  bridged: 2026-07-11
  tags: [architecture, separation-of-concerns, git]
---

Immutable Git-object snapshotting (commit/tree/member OID pinning) is separate from manifest attestation. Don't merge concerns; snapshot validates object graph integrity, attestation happens downstream. Keep renderer integration isolated; don't remove archive API if legacy tests still exercise it.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
