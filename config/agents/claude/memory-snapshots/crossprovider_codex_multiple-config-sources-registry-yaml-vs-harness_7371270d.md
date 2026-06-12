---
name: crossprovider codex multiple-config-sources-registry-yaml-vs-harness
description: Multiple config sources (registry.yaml vs harness-config.yaml) diverge; need single authority
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [config-drift, authority, readiness]
---

workspace-hub has two overlapping repo/path authorities: `config/workstations/registry.yaml` (sibling layout, tier1_repo_root=/mnt/local-analysis, comprehensive repo list) and `scripts/readiness/harness-config.yaml` (ws_hub_path only, divergent dev-secondary path, subset of repos). #2775 must make registry.yaml canonical and add validation gates that fail if harness-config diverges.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
