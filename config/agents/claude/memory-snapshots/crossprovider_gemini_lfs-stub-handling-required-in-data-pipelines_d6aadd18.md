---
name: crossprovider gemini lfs-stub-handling-required-in-data-pipelines
description: LFS stub handling required in data pipelines
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [git-lfs, data-pipeline, constraint-handling]
---

When large binary datasets are LFS-tracked, 129/133 files may be pointers (stubs) rather than materialized data. Pipelines must detect stubs, gracefully fall back to partial analysis or cached derivatives, and document missing data. Treating all bins as available silently fails when data is not fetched.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
