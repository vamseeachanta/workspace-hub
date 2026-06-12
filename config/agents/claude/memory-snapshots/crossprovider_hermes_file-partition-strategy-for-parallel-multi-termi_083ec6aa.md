---
name: crossprovider hermes file-partition-strategy-for-parallel-multi-termi
description: File-partition strategy for parallel multi-terminal workstreams
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [workflow, parallel-work, git-strategy, multi-agent]
---

Design N concurrent work streams (terminals/agents) by partitioning file ownership with explicit contention map: T1→fileA/, T2→fileB/, T3→fileC/. Each terminal owns non-overlapping files/directories, enabling true parallel work without git rebasing/merging. Example: cathodic_protection/ for T1, ansys/ for T2, fatigue/ for T3. Requires upfront planning but eliminates lock contention.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
