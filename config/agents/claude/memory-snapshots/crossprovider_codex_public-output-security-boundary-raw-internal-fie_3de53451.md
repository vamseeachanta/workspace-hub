---
name: crossprovider codex public-output-security-boundary-raw-internal-fie
description: Public output security boundary: raw internal fields always hidden
metadata:
  type: reference
  source: codex
  bridged: 2026-07-03
  tags: [security, data-governance, contracts]
---

Public outputs must never publish raw source_id, source_sha256, private_lookup_key, private_lookup_map, share_relative_path_private_only, source_hash, provenance_pointer, or literal public_source_token values — even though contract prose and policy may reference them. This is a hard firewall between external-facing data and internal plumbing.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
