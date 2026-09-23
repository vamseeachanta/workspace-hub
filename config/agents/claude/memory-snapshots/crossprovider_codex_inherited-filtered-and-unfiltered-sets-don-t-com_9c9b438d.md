---
name: crossprovider codex inherited-filtered-and-unfiltered-sets-don-t-com
description: Inherited filtered and unfiltered sets don't compose uniformly
metadata:
  type: reference
  source: codex
  bridged: 2026-07-19
  tags: [data-composition, release-management, consistency]
---

If v1 derives a set from all records (no release filter) and v3 tightens only *new* output sets, inherited base sets retain unfiltered membership. This allows orphan/unreleased records into logical-release commitments. Release membership filtering must apply uniformly across all composed sources.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
