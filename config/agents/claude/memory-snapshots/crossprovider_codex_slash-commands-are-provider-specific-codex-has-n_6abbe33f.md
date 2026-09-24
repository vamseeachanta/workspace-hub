---
name: crossprovider codex slash-commands-are-provider-specific-codex-has-n
description: Slash commands are provider-specific; Codex has no plugin equivalent
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [command-discovery, codex-limitation, cli-design]
---

Commands defined in `.claude/commands/` are Claude-only. Codex CLI explicitly lacks a slash-command plugin system; it uses skills (under `.codex/skills/`) and prompt templates instead. Automated command discovery and invocation routing must account for this fundamental difference—there is no universal `/command` surface across providers.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
