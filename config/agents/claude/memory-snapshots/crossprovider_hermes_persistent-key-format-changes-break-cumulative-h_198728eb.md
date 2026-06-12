---
name: crossprovider hermes persistent-key-format-changes-break-cumulative-h
description: Persistent key format changes break cumulative history without migration
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [data-formats, backward-compatibility, persistence, migration]
---

Changing a persistent ID format (job_id now includes source/url/posted_date) breaks all existing records because the new format won't match old keys in cumulative-index.json. Weekly-refresh tracking, seen_count, and trend continuity become incorrect for one run. When shipping a format change, provide a migration script or reset plan for dependent indices.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
