---
name: crossprovider codex scheduler-data-paths-diverge-from-job-output-pat
description: Scheduler data paths diverge from job output paths
metadata:
  type: reference
  source: codex
  bridged: 2026-07-05
  tags: [scheduler, path-normalization, data-resolver]
---

get_module_data_safe(module) resolves to data/modules/<module>/..., but job config and output paths may differ. Requires normalization test to prevent manifest/output/source mismatch.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
