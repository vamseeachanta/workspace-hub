---
name: crossprovider codex drift-vs-per-host-status-are-distinct-schema-con
description: Drift vs per-host status are distinct schema concepts
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [schema-design, infrastructure-audit]
---

Infrastructure audit schemas must distinguish status (per-machine: is tool present/parseable?) from drift (cross-machine: how different are versions?). Conflating them in examples or YAML causes implementation ambiguity. Example: 'status: missing' on one machine produces 'severity: block' drift only when other machines have the tool; status is local, drift is fleet-wide.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
