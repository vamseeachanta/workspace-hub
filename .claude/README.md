# Project Memory & Guidelines

This directory (`.claude`) contains project-specific memory, guidelines, and configuration that Factory AI agents automatically load at session start.

## Files in This Directory

- **CLAUDE.md** - Primary project instructions and configuration
  - Loaded automatically by Factory AI (all variants including GPT-5 Codex)
  - Contains SPARC methodology, agent orchestration, and coding standards
  - Defines workflow patterns and best practices

- **settings.json** - Claude Code session settings
- **settings.local.json** - Local overrides (not committed to git)

## Subdirectories

- **agents/** - Agent-specific configurations and templates
- **checkpoints/** - Session checkpoints and state
- **commands/** - Custom slash commands
- **helpers/** - Helper utilities and scripts

## Quirk Logging

Use `.claude/agents/quirk-logger.md` whenever a session loses time to an undocumented tool, library, host, lane, or repository behavior. The quirk logger owns the GitHub issue lifecycle with no human approval loop: search for an existing `quirk` issue, comment if one exists, create one if it does not, and close it after the fix is merged and documented.

The helper is:

```bash
scripts/ai/gh_quirk.sh log --repo <owner/repo> --area <area> --symptom "<text>" --cause "<text>" --fix "<text>" --doc "<path-or-url>" --session "<id>"
scripts/ai/gh_quirk.sh list --repo <owner/repo>
scripts/ai/gh_quirk.sh close --repo <owner/repo> --number N --fixed-by <commit> --doc <path-or-url>
```

Routing rule: digitalmodel code/tool quirks go to `vamseeachanta/digitalmodel`; generic third-party software and documentation quirks go to `vamseeachanta/llm-wiki`; private host/lane/client infrastructure quirks go to `vamseeachanta/llm-wiki-acma`; public-safe workspace-hub infrastructure quirks go to `vamseeachanta/workspace-hub`. For OrcaFlex, AQWA, OpenFOAM, and similar program workflows, route the quirk to the repo that owns the fix or durable documentation, and sanitize public repo entries with `lane-A/B/C/D` and `<campaign>` instead of private identifiers.

## How It Works

### Automatic Loading

When you start a Factory AI session (droid) in this repository:

1. Factory AI reads `.claude/CLAUDE.md` automatically
2. All instructions, standards, and guidelines are loaded into context
3. Works with **all Factory agent variants** including GPT-5 Codex
4. No manual loading required - just start coding!

### Cross-Repository Consistency

- Each repository in workspace-hub has its own `.claude/` directory
- Sub-repositories reference workspace-hub parent configuration
- Ensures consistent guidelines across all 26+ repositories

### When to Update

Edit `.claude/CLAUDE.md` when you need to:

- Add new coding standards or best practices
- Define project-specific workflows
- Update agent orchestration patterns
- Add new tools or integrations
- Modify file organization rules

Changes take effect on the **next session start**.

## Git Integration

- `.claude/CLAUDE.md` - **Committed** (shared team instructions)
- `.claude/settings.json` - **Committed** (shared settings)
- `.claude/settings.local.json` - **Ignored** (personal overrides)
- `.claude/checkpoints/` - **Ignored** (session-specific state)

## Multi-Repository Setup

This workspace-hub uses a hierarchical configuration:

```
workspace-hub/
├── .claude/
│   └── CLAUDE.md (master guidelines)
│
├── aceengineer-admin/
│   └── .claude/
│       └── CLAUDE.md (inherits + repo-specific)
│
├── aceengineercode/
│   └── .claude/
│       └── CLAUDE.md (inherits + repo-specific)
│
└── [... 23 more repositories ...]
```

## Factory AI Compatibility

✅ **Works with all Factory AI variants:**
- Claude 3.5 Sonnet
- GPT-5 Codex
- GPT-5.5
- Claude 3 Opus
- Other supported models

The `.claude` project memory system is **model-agnostic** and works consistently across all agent types.

## Best Practices

1. **Keep CLAUDE.md focused** - Core instructions only
2. **Use subdirectories** - For specialized configs (agents/, commands/)
3. **Document decisions** - Add context for why guidelines exist
4. **Version control** - Commit shared guidelines, ignore session data
5. **Test changes** - Restart session after updating CLAUDE.md

## Support

- Factory AI Docs: https://docs.factory.ai
- Claude Code Docs: https://docs.claude.com/claude-code
- Workspace-hub: See main README.md
