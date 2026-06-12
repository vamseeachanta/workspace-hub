---
name: crossprovider codex two-tier-legacy-exemption-for-phased-gate-enforc
description: Two-tier legacy exemption for phased gate enforcement
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [gate-enforcement, backward-compatibility, phased-rollout]
---

When rolling out new gate requirements to existing items, use WRK ID number as the primary discriminator (id < cutoff → legacy, skip gate) and created_at as secondary (for items ≥ cutoff, backfilled before rollout → skip if created_at < rollout-date). This pattern handles both pre-upgrade items (which lack created_at) and backfilled older items without breaking on upgrade.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
