---
name: multi-layer-stale-state-debugging
description: Detect and clear stale state persisting across multiple storage layers (auth files, cache, code logic)
version: 1.0.0
source: auto-extracted
extracted: 2026-04-10
metadata:
  tags: ["debugging", "state-management", "cache-invalidation", "multi-layer-systems"]
---

# Multi-Layer Stale State Debugging

When a system shows persistent error signals despite reset conditions being met, check for stale state in three layers: (1) persistent config files with error timestamps, (2) cache files with synthetic entries, (3) code logic without staleness checks. Clear each layer independently, then add staleness detection (e.g., 12-hour threshold) to prevent recurrence. Verify fixes end-to-end before marking complete.