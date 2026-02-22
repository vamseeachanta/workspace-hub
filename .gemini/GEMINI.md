---
provider: gemini
generated-from: AGENTS.md
contract-version: 1.0.0
generated-at: 2026-02-20T00:00:00Z
---

# Gemini Agent Adapter

> Adapter for Google Gemini / gemini CLI. Canonical contract: workspace-hub/AGENTS.md.

## Required Gates

1. Every task maps to WRK-* in `.claude/work-queue/`
2. Plan + explicit approval before implementation
3. Route B/C requires cross-review before completion
4. Code must pass `scripts/legal/legal-sanity-scan.sh`; secrets via env vars; TDD mandatory

## Provider Profile

**Strengths**: research + content tasks — data analysis, summarization, documentation, large context
**Skills**: `.gemini/skills/` → `.claude/skills/` (symlink; workspace-hub canonical)
