---
name: crossprovider gemini github-actions-cannot-run-codex-gemini-ai-review
description: GitHub Actions cannot run Codex/Gemini AI reviews; multi-AI workflows use workflow_dispatch only
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [ci-routing, cross-provider, constraints]
---

Codex and Gemini agent integrations are unavailable in GitHub Actions CI context. Multi-AI review workflows must remove PR-trigger automation and keep only workflow_dispatch for manual invocation. This is a hard constraint, not a configuration choice.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
