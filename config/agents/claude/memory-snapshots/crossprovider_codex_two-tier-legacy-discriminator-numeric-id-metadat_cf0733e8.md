---
name: crossprovider codex two-tier-legacy-discriminator-numeric-id-metadat
description: Two-tier legacy discriminator: numeric ID > metadata
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [gates, legacy, compatibility]
---

For legacy exemptions, numeric ID (always present, never absent) is more reliable than filesystem presence or timestamp fields. Use ID < cutoff as Tier 1 (simple, immune to missing created_at), then created_at as Tier 2 (secondary, for records created after cutoff). Eliminates brittle edge cases where legacy items fail because metadata is incomplete.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
