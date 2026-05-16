# Codex Agent Adapter
<!-- provider: codex | contract-version: 1.2.0 | updated: 2026-05-16 | generated-from: AGENTS.md | identity: config/agents/SHARED_SOUL.md -->
> Canonical contract: workspace-hub/AGENTS.md. Identity + per-message rules: `config/agents/codex/AGENTS.runtime.md` (which `~/.codex/AGENTS.md` symlinks to per #2719 Phase 4). Rules: `.claude/rules/`.

## Required Gates
Loaded via `config/agents/SHARED_SOUL.md` §Hard Gates §1-7 (Plan+approval, TDD, adversarial review at both stages, cross-review 3-agent, legal/security scan, security baseline) and Codex-specific extensions in `config/agents/codex/SOUL.delta.md` §Required Gates (WRK-* mapping, workflow lifecycle skills, coding-style guardrails, git workflow). This adapter file no longer duplicates the gate prose to avoid drift.

## Provider Profile
**Strengths**: focused code tasks — single-file changes, algorithms, testing, refactoring, config
**Skills**: `.codex/skills/` → `.claude/skills/` (symlink; workspace-hub canonical)
**Roles vs Skills**: see `.claude/docs/codex-roles-vs-skills.md` | **Parity audit**: `specs/architecture/work-queue-codex-parity.md`
**Thread cap**: `MAX_TEAMMATES=5` (`.claude/settings.json`); Codex default: 6 parallel agents
**Coding style**: max 400 lines/file, 50 lines/fn, snake_case Python, camelCase JS — `.claude/rules/coding-style.md`
**Git**: conventional commits, branch prefixes (feature/bugfix/chore) — `.claude/rules/git-workflow.md`
