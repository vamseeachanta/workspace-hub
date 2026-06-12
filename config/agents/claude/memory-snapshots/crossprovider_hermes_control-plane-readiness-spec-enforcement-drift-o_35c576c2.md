---
name: crossprovider hermes control-plane-readiness-spec-enforcement-drift-o
description: Control-plane readiness spec/enforcement drift on .codex files
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [specification-drift, control-plane-contract, codex-governance]
---

MODEL_RELEASE_READINESS_CONTRACT.md states .codex/** files are governed by a 20-line limit from .claude/rules/coding-style.md, but the actual coding-style.md only limits CLAUDE.md, MEMORY.md, AGENTS.md, GEMINI.md—.codex files are not mentioned. Actual repo contains many .codex files far exceeding 20 lines. Contract and enforcement rule have drifted; coordinated audit/fix needed to resolve MAJOR contradiction.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
