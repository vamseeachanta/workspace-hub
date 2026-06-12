---
name: crossprovider hermes two-pass-sshfs-dedup-optimization
description: Two-pass SSHFS dedup optimization
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [optimization, sshfs, dedup, performance]
---

Comparing local and remote (SSHFS) datasets: use two-pass strategy. Fast filename+size matching O(n) first, then SHA-256 only on matching candidates O(k) where k << n. SSHFS scanning is 20–30× slower than local; candidate pre-filtering saves hours on large datasets (e.g., 940K DDE files in 233s with pre-filter vs. full-scan timeout).

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
