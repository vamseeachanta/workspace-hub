---
name: crossprovider hermes test-assertions-can-mask-wrong-source-data
description: Test assertions can mask wrong source data
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [testing, review-rigor, validation-gap]
---

When assertions are loosened (e.g., allowing "Analytical" OR "AceEngineer" instead of pinning exact strings), tests pass while still reading from stale/wrong sources. Reviewers must verify test read-paths (what file/surface is actually being tested) match the intended source (canonical content, built output), not just that assertions pass.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
