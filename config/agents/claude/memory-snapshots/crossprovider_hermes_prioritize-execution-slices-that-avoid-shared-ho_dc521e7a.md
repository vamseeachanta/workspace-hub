---
name: crossprovider hermes prioritize-execution-slices-that-avoid-shared-ho
description: prioritize execution slices that avoid shared hotspots over task sequence
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [parallel-execution, git-contention, slice-selection]
---

When selecting the next bounded execution slice for parallel work, prioritize slices that avoid shared/central files (e.g., adapter layers, core utilities) even if task dependencies suggest different order. Git lock contention from shared-file races is costlier than task sequencing delays. Pick the smallest independent unit first.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
