---
name: agent-memory-bridge
description: Bidirectional sync between Hermes memory and Claude Code auto-memory, with licensed machine bootstrap. Use when context parity across agents is needed.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [memory-bridge, cross-agent, context-parity, claude-code]
    related_skills: [licensed-machine-prompt-orchestration, overnight-parallel-agent-prompts]
---

# Agent Memory Bridge

When corrections, context, or patterns learned in one agent (Hermes, Claude Code, Codex) need to propagate to all others.

## When to use

- User says something like "remember this" or gives a correction in Hermes that should apply to Claude Code
- You discover a workspace convention or pattern that other agents on other machines need
- Setting up a new machine to match existing agent context
- After an adversarial review reveals one agent knew something another didn't

## Locations

| System | Memory location | Type |
|--------|----------------|------|
| Hermes | Hermit memory tool (injected into every turn) | Compact, ~2153 chars, curated |
| Claude Code (Linux) | `~/.claude/projects/<path-hash>/memory/*.md` | Auto-accumulated, ~40 files |
| Claude Code (global) | `~/.claude/CLAUDE.md` | Manual, all-sessions baseline |
| Claude Code (Windows) | `C:\Users\<user>\.claude\projects\` | Empty until bootstrapped |
| Codex | Session-only (no persistent memory) | Must re-inject via prompt |
| Gemini | Session-only (no persistent memory) | Must re-inject via prompt |

## Skill Accessibility Across All Agents

Each agent accesses skills differently. A skill in `.claude/skills/` must also be
visible through each agent's mechanism. This was verified in #1949 (Codex symlink fix).

| Agent | Skill Source | Count (workspace-hub) | Verification Command |
|-------|-------------|----------------------|---------------------|
| Claude Code | `.claude/skills/` (native) | 696 | `find -L .claude/skills -name SKILL.md -not -path '*/_archive/*' \| wc -l` |
| Hermes | `~/.hermes/config.yaml` → `external_dirs` (6 repos) | 974 total | Python: check external_dirs paths exist and contain SKILL.md files |
| Codex | `.codex/skills/` → symlink to `../.claude/skills/` | 696 | `find -L .codex/skills -name SKILL.md -not -path '*/_archive/*' \| wc -l` |
| Gemini | `.gemini/skills/` → symlink to `../.claude/skills/` | 696 | `find -L .gemini/skills -name SKILL.md -not -path '*/_archive/*' \| wc -l` |

**CRITICAL VERIFICATION:** Run this after any skill changes to confirm all agents can see skills:

```bash
echo "=== Agent Skill Accessibility ==="
echo "CC:    $(find -L .claude/skills -name 'SKILL.md' -not -path '*/_archive/*' | wc -l)"
echo "Codex: $(find -L .codex/skills -name 'SKILL.md' -not -path '*/_archive/*' | wc -l)"
echo "Gemini: $(find -L .gemini/skills -name 'SKILL.md' -not -path '*/_archive/*' | wc -l)"
```

**Key Pitfall:** `.codex/skills/` should be a symlink to `../.claude/skills/` but was
accidentally a real directory with only 57 GSD skills (out of 696+). Always verify
it's a symlink: `ls -la .codex/skills` should show `-> ../.claude/skills`, not a directory.

**Sub-repo Behavior:** When working in sub-repos (CAD-DEVELOPMENTS/, digitalmodel/, etc.),
each agent sees that repo's local `.claude/skills/` (31-261 skills) PLUS the workspace-hub
skills (696) depending on working directory context. See #1951 for sub-repo skill visibility gap.

## Bridging Hermes → Claude Code

1. Hermes memory is always available in the system context — extract the consolidated facts
2. Write to `~/.claude/CLAUDE.md` (global) or `~/.claude/projects/<hash>/memory/` (project-scoped)
3. The GLOBAL CLAUDE.md is the single source of truth — write conventions, paths, user preferences, corrections
4. Project-scoped memory is for organic learnings accumulated over sessions

## Bridging Claude Code → Hermes

1. Read `~/.claude/projects/*/memory/*.md` — these are Claude's learned corrections and context
2. Feed into `delegate_task` context for subagents
3. Use `memory` tool to store critical corrections in Hermes memory (curate — Hermes memory is limited to 2200 chars)

## Bridging to Licensed Machines (Windows)

1. Export unified memory files to a tarball or git-tracked directory
2. Copy to Windows machine
3. Bootstrap with `.claude/CLAUDE.md` at project level
4. Use `python` not `uv run` on Windows

## Key Principles

- **Compact source of truth**: One global CLAUDE.md that any agent can load
- **Curate aggressively**: Claude's auto-memory grows organically and has duplicate/cross-cutting entries. Deduplicate before bridging.
- **Git-track everything**: Put the bridge scripts and export files in the repo so they survive machine loss
- **No agent loses context**: If Claude's OAuth session dies and starts fresh, it should still have the same baseline knowledge via CLAUDE.md

## Pitfalls

- Claude's auto-memory directory is at `~/.claude/projects/-<path>-hash/memory/` — the directory name is URL-encoded path with dashes, not a UUID
- Claude's auto-memory has a 25KB/200-line limit per project
- Multiple project directories exist in parallel (workspace-hub, digitalmodel, worldenergydata) — bridge ALL of them
- Windows path separators differ — test the bootstrap script on the target machine