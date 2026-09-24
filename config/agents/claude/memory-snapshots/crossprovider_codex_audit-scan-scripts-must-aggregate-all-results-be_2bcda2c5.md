---
name: crossprovider codex audit-scan-scripts-must-aggregate-all-results-be
description: Audit/scan scripts must aggregate all results before deciding exit status, never abort early
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [audit-automation, exit-semantics, governance]
---

Multi-repo audits that abort on first failure hide later failures and lose the complete report needed for governance. Collect results from all repos, write the full manifest, then set exit status based on aggregate findings. This ensures downstreams (CI gates, dashboards) see the complete picture.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
