---
name: crossprovider hermes long-running-benchmarks-300s-over-20k-files-need
description: Long-running benchmarks (300s+ over 20K files) need performance audit
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [performance, benchmarking]
---

Benchmark timeouts with slow file-iteration suggest O(n²) retrieval logic or unoptimized corpus scanning. Profile the retriever before declaring metrics valid. Synthetic input testing (e.g., nonsense queries) can expose ranking boost leakage early.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
