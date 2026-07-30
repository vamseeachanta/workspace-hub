---
name: crossprovider codex handover-state-precision-prevents-chasing-stale-
description: Handover state precision prevents chasing stale discrepancies
metadata:
  type: reference
  source: codex
  bridged: 2026-07-19
  tags: [handover, precision, state-management]
---

Pin data counts and thresholds to the post-merge state you're describing, and explicitly note when the described state isn't yet live (e.g., 'main is at E2 level, this describes post-#1037'). A silent mismatch sends the next agent chasing a phantom discrepancy.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
