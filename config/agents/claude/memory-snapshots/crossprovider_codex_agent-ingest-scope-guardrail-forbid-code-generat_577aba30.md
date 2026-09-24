---
name: crossprovider codex agent-ingest-scope-guardrail-forbid-code-generat
description: Agent ingest scope guardrail: forbid code generation
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [prompt-design, agent-boundaries, scope-containment]
---

Hardened PDF-to-wiki ingest prompts must explicitly forbid agents from creating scripts, tests, or tooling code. Add phrasing like: 'If you feel you need a helper script, you are misreading the task — just write the wiki Markdown directly.' Agents tasked with extraction default to scaffolding helper code if not explicitly blocked.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
