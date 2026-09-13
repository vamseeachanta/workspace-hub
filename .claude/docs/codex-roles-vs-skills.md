# Codex Roles vs Skills

Skills contain reusable task instructions and resources. Agent roles configure
delegated execution. Keep domain methods in the canonical skill source and
provider-specific role configuration in the provider's supported configuration.
Neither a role name nor a skill grants additional permissions.

## Workspace ownership and discovery

The authored skill source is `.claude/skills/`. Provider-facing adapters should
reference that source rather than maintain rewritten copies. Codex repository
discovery uses `.agents/skills`; a `.codex/skills` link alone does not establish
loading or parity. See [official skill documentation](https://learn.chatgpt.com/docs/build-skills)
and the [Codex operating delta](../../config/agents/codex/SOUL.delta.md).

Resolve source references from the explicitly identified owning checkout. Inspect
the effective runtime, settings and available delegation tools before selecting
roles, thread limits or skill roots; historical version defaults are not current
capability evidence. Preserve native system skills and unrelated plugins/settings.

## Execution

- Select skills by task needs and delegate according to dependencies and ownership.
- Keep shared lifecycle and authority in
  [SHARED_SOUL.md](../../config/agents/SHARED_SOUL.md); do not copy gates into roles.
- Use supported shared tools where appropriate; a shared MCP interface does not
  establish equal provider permissions or require every tool to use MCP.
- Keep orchestrator context intact. Do not place `/clear` or session-reset commands
  in delegated task prompts for the orchestrator to execute.
- Verify provider limits independently; a Claude teammate limit does not configure
  Codex concurrency.
  The repository's `MAX_TEAMMATES` setting is in
  [`.claude/settings.json`](../settings.json); inspect its current value and consumer.

This replaces the dated February 2026 role/default-limit comparison. Current
installation and observed native loading remain separate verification steps.
