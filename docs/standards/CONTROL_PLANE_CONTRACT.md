# Control-Plane Contract

> Canonical standard for how AI agents and humans discover context in any workspace-hub repository.
>
> Version: 1.0.0 | Date: 2026-03-31 | Issue: #1532

---

## Entry Point

**`AGENTS.md`** is the canonical entry point for every repository. It tells both humans and AI agents:
- What the repo does
- How to work in it (workflow, commands, policies)
- Hard gates and constraints

Every repo MUST have an `AGENTS.md` at the root.

## Provider Adapters

Provider-specific configuration lives in dedicated directories. These are **adapters**, not alternatives to `AGENTS.md`.

| Path | Provider | Role | Required? |
|------|----------|------|-----------|
| `.claude/` | Claude Code | CLAUDE.md, rules/, skills/, docs/ | YES — all repos |
| `.claude/CLAUDE.md` | Claude Code | Claude-specific config (imports AGENTS.md context) | YES |
| `.codex/` | OpenAI Codex | Codex adapter (instructions, settings) | YES — can be minimal/empty |
| `.gemini/` | Google Gemini | Gemini adapter (GEMINI.md, settings) | YES — can be minimal/empty |
| `.mcp.json` | MCP | Model Context Protocol server config | WHERE APPLICABLE |

### Adapter Rules

1. Adapters MUST NOT contradict `AGENTS.md`
2. Adapters MAY add provider-specific detail (e.g., Claude skills, Codex instructions)
3. Empty adapter directories are acceptable — they signal provider awareness
4. `CLAUDE.md` at repo root is Claude's auto-loaded config; `.claude/` holds extended config

## Legacy Paths

| Path | Status | Disposition |
|------|--------|-------------|
| `.agent-os/` | **Legacy** | Present in 3 of 4 starter repos (worldenergydata, assethold, assetutilities). NOT at workspace-hub root. Content (mission, tech-stack, roadmap, decisions) should migrate to `AGENTS.md` or `docs/`. No new repos should create `.agent-os/`. |
| `.hive-mind/` | **Legacy** | Claude Flow Hive Mind system. Frozen — see `LEGACY.md` in directory. Do not extend. |
| `.swarm/` | **Legacy** | Swarm coordination data. Frozen — see `LEGACY.md` in directory. Do not extend. |
| `.SLASH_COMMAND_ECOSYSTEM/` | **Legacy** | Slash command registry and modules. Frozen — see `LEGACY.md` in directory. Slash commands are optional frontends, not core architecture. |
| `.specify/` | **Retired** | Not found in any active repo. Do not create. |
| SPARC methodology refs | **Historical** | Replaced by GSD workflow. |
| Claude Flow / swarm refs | **Historical** | Replaced by direct provider adapter model. |

See also: [AI Review Routing Policy](AI_REVIEW_ROUTING_POLICY.md) for provider roles and review defaults.

## Reading Order for AI Agents

When entering any repo:

1. `AGENTS.md` — workflow contract (always first)
2. `CLAUDE.md` (or equivalent provider config) — provider-specific rules
3. `README.md` — project overview
4. `docs/` — detailed documentation
5. `src/` — code structure
6. `tests/` — test patterns

## Starter Repo Convergence Status

| Repo | AGENTS.md | .claude/ | .codex/ | .gemini/ | .agent-os/ | Notes |
|------|:---------:|:--------:|:-------:|:--------:|:----------:|-------|
| digitalmodel | OK | OK | OK | OK | — | Fully converged |
| worldenergydata | OK | OK | OK | OK | Legacy | Migrate .agent-os/ content to AGENTS.md/docs |
| assethold | OK | OK | OK | OK | Legacy | Migrate; also fix merge conflicts in .gitignore and README.md |
| assetutilities | OK | OK | OK | OK | Legacy | Migrate .agent-os/ content |

## Rollout Plan

1. **Phase 1** (starter repos): Validate contract against digitalmodel, worldenergydata, assethold, assetutilities
2. **Phase 2** (remaining work repos): Apply contract to all work repos
3. **Phase 3** (personal repos): Apply contract to personal repos
4. **.agent-os/ migration**: For each repo with .agent-os/, migrate useful content to AGENTS.md or docs/, then remove

## Exceptions

- `.mcp.json` is only required where MCP servers are actually configured (currently digitalmodel, worldenergydata)
- Repos with no AI agent usage may have minimal adapters (empty .codex/, .gemini/)
- `.agent-os/` may remain temporarily until content is migrated — track via issue comments
