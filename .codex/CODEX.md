---
provider: codex
generated-from: AGENTS.md
contract-version: 1.0.0
generated-at: 2026-02-20T00:00:00Z
---

# Codex Agent Adapter

> Adapter for OpenAI Codex / codex CLI. Canonical contract: workspace-hub/AGENTS.md.

## Required Gates

1. Every task maps to WRK-* in `.claude/work-queue/`
2. Plan + explicit approval before implementation
3. Route B/C requires cross-review before completion
4. Code must pass `scripts/legal/legal-sanity-scan.sh`; secrets via env vars; TDD mandatory

## Provider Profile

**Strengths**: focused code tasks — single-file changes, algorithms, testing, refactoring, config
**Skills**: `.codex/skills/` → `.claude/skills/` (symlink; workspace-hub canonical)
**Roles vs Skills**: see `.claude/docs/codex-roles-vs-skills.md`
**Thread cap**: `MAX_TEAMMATES=5` (`.claude/settings.json`); Codex default: 6 parallel agents
