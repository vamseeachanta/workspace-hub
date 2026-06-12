---
name: crossprovider gemini tool-health-checks-must-exceed-version
description: Tool health checks must exceed --version
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [tooling, health-checks, post-deployment-verification]
---

AI tools (Hermes, Claude Code, etc.) can report version successfully but remain broken if dependencies are missing, configs corrupted, or auth credentials expired. Post-update verification requires functional tests beyond version flags.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
