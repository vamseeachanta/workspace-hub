# Claude Provider Delta
> Inherits identity, gates, and must-fire rules from [`../SHARED_SOUL.md`](../SHARED_SOUL.md). This file carries only Claude-specific operating-model differences.
> Runtime artifact: [`./SOUL.runtime.md`](./SOUL.runtime.md) (built by `scripts/agents/build-soul-runtime.sh`).

# Claude-Specific Operating Model

## Authentication and Subscription

- **Subscription mode only.** Use `claude auth login` (browser flow). **NEVER** use API key auth (`ANTHROPIC_API_KEY`) without explicit user permission. Claude Max subscription is the paid surface; API-key fallback bypasses the rate-limit budgeting the user actively manages.
- Verify auth before load planning. Claude Code CLI is the primary client; Claude Desktop wraps the same CLI via Agent Mode (`~/.config/Claude/claude-code/<v>/`).

## MCP Tool Scope

Claude MCP integrations are scoped narrowly to limit blast radius:

- **`claude_ai_Gmail`** — read + compose + label only. **NO `gmail.modify`**; archive/delete/unsubscribe require browser-in-chrome or user-UI action. (`feedback_gmail_filter_first_over_per_thread`, `reference_gmail_mcp_scope`)
- **`claude_ai_Google_Calendar`** — full CRUD available.
- **`claude_ai_Google_Drive`** — read/create/search; permissions read-only.

When the user asks for Gmail mutations beyond compose/label, surface the scope gap and route to browser-in-chrome or wait for the [#2423](https://github.com/vamseeachanta/workspace-hub/issues/2423) scope bump.

## Browser Automation Constraints

- **`mcp__claude-in-chrome__*` is session-scoped to the main Claude session.** Subagents (`Agent` tool) cannot drive Chrome — partition work: main = browser, subagents = research. (`feedback_claude_in_chrome_session_scoped`)
- Before any chrome tool call, load it via `ToolSearch select:mcp__claude-in-chrome__<name>` — schemas are not preloaded.
- Gmail bulk-archive is dialog-free; delete/empty-trash/unsubscribe DO trigger dialogs and break the session — avoid. (`feedback_gmail_bulk_archive_no_confirm`)
- `gif_creator` captures 50 frames + click indicators for proof-of-action sequences; export to `docs/sessions/`. (`feedback_gif_creator_as_proof_pattern`)

## Subagent Behavior

- **`Agent` tool dispatch** = fresh-context subagent; cannot see this conversation. Brief like a smart colleague who just walked in.
- **Subagent isolation** is intentional — fresh context per `docs/standards/SUBAGENT_CONTEXT_ISOLATION.md`. Use for parallelizing independent queries or protecting main context.
- **Worktree isolation cost**: `isolation: worktree` triggers ~33K-file checkout on workspace-hub, 60% timeout risk. Reserve for commit/push agents, not general work. (`feedback_worktree_isolation_large_repo_cost`)

## Output Style System

Claude Code supports output-style adapters (`/output-style` switches voice). Current active style governs response shape. When the user invokes a style, follow its content guidelines but **never override** the gates and must-fire rules in SHARED_SOUL.md.

## Skill Loader

- `.claude/skills/` is the workspace-hub canonical skills tree (~50+ families).
- User-global plugins under `~/.claude/plugins/cache/` are NOT in the repo tree; `git mv` cannot operate on them. (`feedback_plugin_cache_not_repo_tracked`)
- Skill conflicts: workspace `.claude/skills/` wins over `.agents/skills/` and `~/.claude/plugins/`. Verify before invoking.

## Memory Surfaces

- `~/.claude/projects/.../memory/` is auto-memory — Claude writes feedback files automatically (`feedback_*.md`, `project_*.md`, `reference_*.md`). Index at `MEMORY.md`.
- `.claude/memory/agents.md` is bridge-managed — Hermes writes via `scripts/memory/bridge-hermes-claude.sh`. Don't hand-edit.
- `.claude/memory/topics/` is the auto-memory mirror — synchronized from `~/.claude/projects/`.
- Auto-memory rules (when to save user/feedback/project/reference) are in the harness `auto memory` block; not in this file.

## Known Hazards

- **Edit tool freshness window**: after a `Write`, the harness may not immediately reflect the new file via `Read` if cached. Verify with `ls` if uncertain. (`feedback_edit_tool_freshness_window_after_writes`)
- **Read tool requirement before Edit**: harness enforces a Read-before-Edit gate. Pre-load files via `Read` even if you've seen them via Bash/grep earlier in the session.
- **Tool call narration**: do NOT use colons before tool calls in user-visible text (gates rendering of tool blocks).

## Quota and Cost

- Claude Max base + overage quota pools are consumed by main-session work. Subagents use the same pool.
- The user explicitly tracks "zero waste" across Anthropic Max base + Anthropic Max overage + OpenAI pools. Brain/hands delegation to Hermes routes execution-heavy work away from main-session Claude when appropriate. See `goal-invocation.md` Step 4.5.
