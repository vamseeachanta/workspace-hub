---
name: crossprovider gemini work-queue-workflow-6-stages-with-4-named-gates-
description: Work queue workflow: 6 stages with 4 named gates (capture → triage → plan → approval → execute → review → archive)
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [workflow, orchestration]
---

Each stage has exit codes: 1=hard block (Codex reject), 2=blocked (prerequisite unmet), 3=blocked (approval missing), 4=session collision. Gates check preconditions (plan existence, approval status, lock availability). Visualized in workflow-visual.html with Mermaid.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
