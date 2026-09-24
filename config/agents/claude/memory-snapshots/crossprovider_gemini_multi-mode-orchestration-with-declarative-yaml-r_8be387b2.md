---
name: crossprovider gemini multi-mode-orchestration-with-declarative-yaml-r
description: Multi-mode orchestration with declarative YAML routing
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [orchestration, yaml-driven, workflow-design]
---

Single entry point (`start_stage.py` pattern) reads a YAML contract to route execution: task_agent mode (writes prompt for dispatch), human_interactive mode (emits checklist), or chained_agent mode (sequences multiple stages). Declarative routing enables flexible workflow composition without code changes.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
