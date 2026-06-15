---
name: crossprovider codex run-identity-versioning-is-load-bearing-for-audi
description: Run identity versioning is load-bearing for auditability and replayability
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [versioning, auditability, run-semantics]
---

Every automated run must carry immutable identity: run_id, attempt_id, schema_version, code_ref, catalog_ref, dataset versions, source URLs, timestamps, content hashes, output hashes, and rerun lineage. Without this, reruns cannot be audited, replayed, or proven idempotent.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
