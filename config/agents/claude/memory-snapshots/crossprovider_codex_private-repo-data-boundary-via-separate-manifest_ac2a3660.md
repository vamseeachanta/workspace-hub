---
name: crossprovider codex private-repo-data-boundary-via-separate-manifest
description: Private-repo data boundary via separate manifest schemas
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [data-governance, schema-separation, boundary-enforcement]
---

Path-bearing raw exports and run-scoped manifests stay isolated under `/mnt/ace/...` with no repo-facing references. Repo summaries use source IDs, canonical slugs, citations, and metadata only. Enforce with separate validator schemas: private manifests accept raw_local_path, repo-facing reject `/mnt/ace` patterns and raw payloads. Prevents accidental path leakage and maintains publication boundary.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
