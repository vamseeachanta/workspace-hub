# Gemini Agent Adapter
<!-- provider: gemini | contract-version: 1.1.0 | updated: 2026-02-24 | generated-from: AGENTS.md -->
> Canonical contract: workspace-hub/AGENTS.md. Rules: `.claude/rules/`. CLI: `echo content | gemini -p "prompt" -y`

## Required Gates
1. Every task maps to WRK-* in `.claude/work-queue/`
2. Plan + explicit approval before implementation
3. Route B/C requires cross-review before completion
4. Code must pass `scripts/legal/legal-sanity-scan.sh`; secrets via env vars; TDD mandatory
5. No client identifiers in code — see `.claude/rules/legal-compliance.md` and `.legal-deny-list.yaml`
6. Input validation, parameterized queries, no hardcoded secrets — see `.claude/rules/security.md`

## Provider Profile
**Strengths**: research + content tasks — data analysis, summarization, documentation, large context
**Skills**: `.gemini/skills/` → `.claude/skills/` (symlink; workspace-hub canonical)
**Prompts**: `.gemini/prompts/` — Gemini-specific templates (pipe via `-p` flag)
**Coding style**: max 400 lines/file, 50 lines/fn, snake_case Python, camelCase JS — `.claude/rules/coding-style.md`
**Git**: conventional commits, branch prefixes (feature/bugfix/chore) — `.claude/rules/git-workflow.md`
