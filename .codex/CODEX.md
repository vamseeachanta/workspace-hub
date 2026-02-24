# Codex Agent Adapter
<!-- provider: codex | contract-version: 1.1.0 | updated: 2026-02-24 | generated-from: AGENTS.md -->
> Canonical contract: workspace-hub/AGENTS.md. Rules: `.claude/rules/`.

## Required Gates
1. Every task maps to WRK-* in `.claude/work-queue/`
2. Plan + explicit approval before implementation
3. Route B/C requires cross-review before completion
4. Code must pass `scripts/legal/legal-sanity-scan.sh`; secrets via env vars; TDD mandatory
5. No client identifiers in code — see `.claude/rules/legal-compliance.md` and `.legal-deny-list.yaml`
6. Input validation, parameterized queries, no hardcoded secrets — see `.claude/rules/security.md`

## Provider Profile
**Strengths**: focused code tasks — single-file changes, algorithms, testing, refactoring, config
**Skills**: `.codex/skills/` → `.claude/skills/` (symlink; workspace-hub canonical)
**Roles vs Skills**: see `.claude/docs/codex-roles-vs-skills.md`
**Thread cap**: `MAX_TEAMMATES=5` (`.claude/settings.json`); Codex default: 6 parallel agents
**Coding style**: max 400 lines/file, 50 lines/fn, snake_case Python, camelCase JS — `.claude/rules/coding-style.md`
**Git**: conventional commits, branch prefixes (feature/bugfix/chore) — `.claude/rules/git-workflow.md`
