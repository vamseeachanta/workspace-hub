---
name: crossprovider hermes taxonomy-reporting-silently-under-reports-with-t
description: Taxonomy reporting silently under-reports with truncated diffs
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [reporting, taxonomy, digitalmodel]
---

summarize_semantic_equivalence() ignores payload_taxonomy_counts when any diffs present, recomputing counts from diff categories only. If producer sends authoritative aggregate counts + partial/truncated diff list, HTML/executive summary will silently under-report taxonomy classes.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
