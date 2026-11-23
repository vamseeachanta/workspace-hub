# Claude Plugin Audit — 2026-03-31

Issue: #1473 | Prior audit: #1469 (Superpowers only, 2026-03-28)

## Version Comparison

| Plugin | Marketplace | Installed Version | Commit SHA | Status |
|---|---|---|---|---|
| superpowers | claude-plugins-official | 5.0.7 | `e4a2375c` | **Current** (updated today) |
| frontend-design | claude-plugins-official | unknown | `205b6e0b` | Version not tracked |
| feature-dev | claude-plugins-official | unknown | `205b6e0b` | Version not tracked |
| code-review | claude-plugins-official | unknown | `205b6e0b` | Version not tracked |
| pr-review-toolkit | claude-plugins-official | unknown | `205b6e0b` | Version not tracked |
| hookify | claude-plugins-official | unknown | `205b6e0b` | Version not tracked |
| playground | claude-plugins-official | unknown | `205b6e0b` | Version not tracked |
| skill-creator | claude-plugins-official | unknown | `205b6e0b` | Version not tracked |
| claude-md-management | claude-plugins-official | 1.0.0 | `205b6e0b` | Current (no newer version in cache) |
| pyright-lsp | claude-plugins-official | 1.0.0 | `205b6e0b` | **Disabled** |
| codex | openai-codex | 1.0.2 | `8e403f9d` | Current (installed today) |

### Version: unknown Issue

8 of 11 plugins report `Version: unknown`. This happens when the plugin's `package.json` lacks a `version` field or the marketplace registry doesn't track semver for these plugins. Only `superpowers` (5.0.7), `claude-md-management` (1.0.0), `pyright-lsp` (1.0.0), and `codex` (1.0.2) have tracked versions.

All "unknown" plugins share commit SHA `205b6e0b` from initial install (2026-03-04) but have been refreshed via auto-update (last update: 2026-03-31). The marketplace snapshot SHA is `52e95f67`, and cached copies at that SHA exist for all plugins, indicating content has been updated even though the version label stays "unknown."

## Superpowers Changelog (since last audit at v5.0.6)

### v5.0.7 (2026-03-31)
- **Copilot CLI support** — SessionStart hook emits `additionalContext` for Copilot CLI v1.0.11+
- **Tool mapping** — added `references/copilot-tools.md` for Claude Code → Copilot equivalence
- **OpenCode fixes** — skills path consistency, bootstrap as user message (not system)

### v5.0.6 (2026-03-24) — highlights from last audit
- **Inline self-review** replaces subagent review loops (brainstorming, writing-plans)
- **Brainstorm server** session directory restructured (`content/` + `state/`)
- **Owner-PID lifecycle** fixes for cross-user PIDs and WSL
- **Codex App compatibility** — worktree-aware patterns, sandbox fallbacks

### Deprecated Skills (still registered, redirect to new names)
| Old Name | New Name | Status |
|---|---|---|
| `superpowers:brainstorm` | `superpowers:brainstorming` | Deprecated redirect |
| `superpowers:write-plan` | `superpowers:writing-plans` | Deprecated redirect |
| `superpowers:execute-plan` | `superpowers:executing-plans` | Deprecated redirect |

**Impact:** No custom skills in `.claude/skills/` reference the deprecated names (verified via grep). GSD skills `gsd-check-todos` and `gsd-execute-phase` reference `brainstorm` and `execute-plan` in prose but as concepts, not as direct skill invocations.

## Skills Inventory by Plugin

| Plugin | Type | Skills/Commands/Agents |
|---|---|---|
| superpowers | skills (14) | brainstorming, dispatching-parallel-agents, executing-plans, finishing-a-development-branch, receiving-code-review, requesting-code-review, subagent-driven-development, systematic-debugging, test-driven-development, using-git-worktrees, using-superpowers, verification-before-completion, writing-plans, writing-skills |
| frontend-design | skill (1) | frontend-design |
| feature-dev | command (1) + agents (3) | feature-dev; code-reviewer, code-architect, code-explorer |
| code-review | command (1) | code-review |
| pr-review-toolkit | command (1) + agents (6) | review-pr; code-simplifier, silent-failure-hunter, code-reviewer, pr-test-analyzer, type-design-analyzer, comment-analyzer |
| hookify | command (4) + agent (1) | hookify, help, list, configure; conversation-analyzer |
| playground | skill (1) + templates (6) | playground; diff-review, document-critique, code-map, data-explorer, concept-map, design-playground |
| skill-creator | skill (1) + agents (3) | skill-creator; comparator, grader, analyzer |
| claude-md-management | command (1) + skill (1) | revise-claude-md; claude-md-improver |
| codex | commands (7) + skill (3) + agent (1) | rescue, setup, adversarial-review, cancel, result, review, status; codex-cli-runtime, codex-result-handling, gpt-5-4-prompting; codex-rescue |

## Custom Skill Overlaps

| Plugin Skill | Custom Skill | Assessment |
|---|---|---|
| `frontend-design:frontend-design` | `.claude/skills/business/content-design/frontend-design/SKILL.md` (v2.0.0) | **Overlap.** Custom skill is domain-tailored (references theme-factory, canvas-design). Plugin is generic Anthropic version. Both active. Custom version adds project-specific typography and design direction. Keep both — plugin for general work, custom for branded output. |
| `code-review:code-review` | `.claude/skills/development/code-reviewer/SKILL.md` (v1.0.0) | **Overlap.** Custom skill is from alirezarezvani/claude-skills with detailed sub-stages (quality, severity, statistics). Plugin is lighter. Custom sub-skills mostly archived. Plugin is preferred for PR workflows; custom adds structured report format. |
| `skill-creator:skill-creator` | `.claude/skills/_internal/builders/skill-creator/SKILL.md` | **Overlap.** Custom skill has extensive sub-skills (30+), most archived. Plugin version is maintained by Anthropic with eval agents. Plugin is preferred. |
| `superpowers:systematic-debugging` | `.claude/skills/development/systematic-debugging/SKILL.md` | **Minimal overlap.** Custom version likely predates plugin adoption. Plugin is authoritative. |
| `superpowers:writing-plans` | `.claude/skills/development/planning/writing-plans/SKILL.md` | **Minimal overlap.** Custom version likely predates plugin adoption. Plugin is authoritative. |
| `superpowers:subagent-driven-development` | `.claude/skills/development/subagent-driven/SKILL.md` | **Minimal overlap.** Custom version likely predates plugin adoption. Plugin is authoritative. |
| `superpowers:verification-before-completion` | `.claude/skills/development/verification-loop/SKILL.md` | **Minimal overlap.** Custom version likely predates plugin adoption. Plugin is authoritative. |
| `superpowers:test-driven-development` | `.claude/skills/development/tdd-obra/SKILL.md` | **Minimal overlap.** Named after obra (superpowers author). Plugin is authoritative. |

## Available but Not Installed

These official plugins exist in the marketplace but are not installed:

| Plugin | Description | Recommendation |
|---|---|---|
| code-simplifier | Code simplification | Already available via pr-review-toolkit agent |
| commit-commands | Git commit/push/PR shortcuts | GSD handles this workflow |
| security-guidance | Security review guidance | Worth evaluating |
| agent-sdk-dev | Agent SDK scaffolding | Worth evaluating if building Agent SDK apps |
| mcp-server-dev | MCP server development | Worth evaluating if building MCP servers |
| plugin-dev | Plugin development | Only needed when authoring plugins |
| math-olympiad | Math competition problems | Not relevant |
| ralph-loop | Agent loop pattern | Not relevant |
| Various LSP plugins | Language server support | Install as needed per language |
| explanatory-output-style | Output style modifier | Preference-based |
| learning-output-style | Output style modifier | Preference-based |

## Disabled Plugins

- **pyright-lsp** (1.0.0) — installed but disabled. No Python LSP needed currently. Can be removed or re-enabled as needed.

## Duplicate Installations

- **frontend-design** — installed at both user and project scope (same cache path). No conflict, but the user-scope install is redundant since the project-scope install covers workspace-hub.
- **skill-creator** — same situation, dual user+project scope.

## Recommended Actions

1. **No upgrades needed** — superpowers is at 5.0.7 (latest), other plugins auto-update via marketplace SHA refresh
2. **Archive redundant custom skills** — consider archiving custom skills that are now fully covered by plugins:
   - `development/systematic-debugging/` → superpowers
   - `development/planning/writing-plans/` → superpowers
   - `development/subagent-driven/` → superpowers
   - `development/verification-loop/` → superpowers
   - `development/tdd-obra/` → superpowers
   - `_internal/builders/skill-creator/` → plugin skill-creator
3. **Keep dual custom skills** where domain-specific:
   - `business/content-design/frontend-design/` (project-specific design system)
   - `development/code-reviewer/` (structured report format)
4. **Evaluate for install** — `security-guidance` and `agent-sdk-dev` plugins
5. **Clean up** — remove user-scope duplicates of frontend-design and skill-creator (project scope is sufficient)
6. **Remove or re-enable** pyright-lsp based on Python usage
7. **Monitor** the 3 deprecated superpowers skills — they work now as redirects but may be removed in a future version

## Marketplace Metadata

- Marketplace: `claude-plugins-official`
- Snapshot SHA: `52e95f6756e577b6a788c941f994ca44de2cf2d6`
- Total available plugins: 32 (including LSP variants)
- External plugins: 17 (asana, context7, discord, firebase, github, gitlab, greptile, imessage, laravel-boost, linear, playwright, serena, slack, supabase, telegram, terraform, fakechat)
- Installed official: 10 (+ 1 disabled)
- Installed external: 1 (codex@openai-codex)

## Next Audit

Scheduled ~2026-06-28 or on next major Claude Code release.
