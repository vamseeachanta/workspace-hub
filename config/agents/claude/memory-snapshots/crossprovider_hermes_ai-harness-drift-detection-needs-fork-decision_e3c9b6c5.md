---
name: crossprovider hermes ai-harness-drift-detection-needs-fork-decision
description: AI harness drift detection needs fork decision
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [infrastructure, decision-point, multi-tool-coordination, config-sync]
---

Post-update changes (shebangs, lock files, configs) in third-party tools (Hermes/Codex) require classification: machine-specific = auto-revert, portable = commit/sync. For upstream repos you can't push to (NousResearch/hermes-agent), choose fork-to-user (vamseeachanta/hermes-agent) OR config-in-primary-repo (workspace-hub/config/agents/hermes/ + deploy script) BEFORE allowing updates. Deferring this decision leads to stash/restore drift cycles.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
