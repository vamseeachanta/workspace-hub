---
name: crossprovider gemini interactive-gates-require-executable-stops-not-a
description: Interactive gates require executable stops, not artifact completion
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [workflow, gates, llm-bias]
---

Presenting an output artifact (HTML plan, design document, review summary) satisfies tool momentum but does not enforce an interactive gate. LLMs will treat artifact production as task completion and skip user-interactive review stages unless the executable path (shell scripts, verification tools) actively blocks progression to the next stage until structured evidence of interaction (YAML files, signed approvals) is present.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
