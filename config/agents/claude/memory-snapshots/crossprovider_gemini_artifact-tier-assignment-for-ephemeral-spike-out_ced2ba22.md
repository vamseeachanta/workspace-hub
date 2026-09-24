---
name: crossprovider gemini artifact-tier-assignment-for-ephemeral-spike-out
description: Artifact tier assignment for ephemeral spike outputs
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [artifact-lifecycle, planning, tier-assignment]
---

Ephemeral per-run artifacts (spike results, temporary data) must be tier-3 (local-cache, throwaway), not tier-1 (git-tracked); confusing tiers is a common planning mistake creating contradictory specs.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
