---
name: crossprovider codex two-tier-legacy-exemption-for-enforcing-gates-ac
description: Two-tier legacy exemption for enforcing gates across versioned work
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [gates, versioning, backward-compatibility, enforcement-patterns]
---

When rolling out a new gate/contract to historical work items, use ID-based versioning (e.g., WRK-NNN < cutoff ID → exempt) combined with timestamp-based cutoff (created_at < CUTOFF_DATE → exempt). Parse ID suffix as integer to fail on malformed IDs. This avoids breaking backfilled items while enforcing on new work without new infrastructure.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
