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