---
name: crossprovider hermes pyyaml-missing-in-cron-execution-environment
description: PyYAML missing in cron execution environment
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [cron, environment, dependencies, yaml]
---

agent-radar and yaml-parsing scripts fail in cron context with "PyYAML not installed" despite working in interactive shells. Scripts import yaml but cron runtime does not have it available. Affects cron-health validation and compliance/knowledge scripts. Environment issue, not code.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
