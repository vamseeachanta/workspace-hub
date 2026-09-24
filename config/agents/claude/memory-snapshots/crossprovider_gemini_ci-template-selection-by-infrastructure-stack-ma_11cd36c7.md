---
name: crossprovider gemini ci-template-selection-by-infrastructure-stack-ma
description: CI template selection by infrastructure stack match
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [ci-bootstrap, template-selection, infrastructure]
---

When bootstrapping CI for a new repo, choose a template from another repo with matching infrastructure stack (language, package manager, linting tools), not from proximity or domain similarity. Reject overly specialized templates with custom checker frameworks. Stack match (digitalmodel's uv+ruff+black+pytest) is more reliable than domain proximity (workspace-hub's pip+bandit+governance plugins are overkill for greenfield repos).

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
