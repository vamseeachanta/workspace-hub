---
name: agent-learnings-portability
version: "1.1"
description: Git-track AI agent learnings so they survive machine loss — memory snapshots, corrections, patterns, insights across Claude, Hermes, Codex, and Gemini.
tags: [harness, git, portability, memory, agent-state, gitignore]
trigger: When auditing agent state portability, setting up a new machine, or investigating why gitignore exceptions aren't working
effort: medium
---

# Agent Learnings Portability

## Problem

AI agents (Claude Code, Hermes, Codex, Gemini) accumulate valuable learnings in machine-local directories (~/.claude/, ~/.hermes/, ~/.codex/, ~/.gemini/). Without explicit git tracking, these are lost on machine failure.

## Architecture: Three Tiers

1. **Git-committed in `.claude/memory/`** (survives `git clone`, PRIMARY): Memory facts, conventions, user context — travels with the repo
2. **Rsync backup** (survives single-machine failure): Large files — session transcripts, SQLite databases, full Claude project memory dirs
3. **Regenerable** (no backup needed): Caches, plugins, debug logs

### The `.claude/memory/` Pattern (issue #1886)

The primary mechanism for cross-machine context parity is writing canonical memory facts directly into `.claude/memory/` inside the repo. This directory is already git-tracked and read by Claude Code at session start on every machine.

**How it works:**
1. Hermes memory (`~/.hermes/memories/MEMORY.md + USER.md`) is the authoritative source
2. Bridge script (`scripts/memory/bridge-hermes-claude.sh`) reads Hermes memory + Claude auto-memory
3. Writes unified entries into `.claude/memory/agents.md` and `context.md`
4. `git commit + push` → every machine that pulls gets the same context
5. Windows (no Hermes): `git pull` → done. No manual copying, no tarballs, no installers.

**Key files:**
- `.claude/memory/context.md` — Machine conventions, paths, Python commands, workspace layout
- `.claude/memory/agents.md` — User profile, AI subscriptions, workflow rules, GSD facts
- `.claude/memory/claude-auto-memory.md` — Snapshot of Claude's auto-generated MEMORY.md
- `scripts/memory/bridge-hermes-claude.sh` — The bridge script, run with `--commit` flag

**Why not tarballs or export/import scripts?** One-time snapshots go stale immediately. Git gives version history, diffs, rollback, and automatic updates on every `git pull`. The bridge should run daily via cron, not manually.

**Return enrichment flow:** Non-Hermes machines (Windows) enrich `KNOWLEDGE.md` or topic files → git commit/push → Linux pulls → bridge script picks up on next run via Claude auto-memory snapshot capture.

This pattern REPLACES the older `config/agents/` snapshot approach for memory (keep `config/agents/` for large state files like session exports, but use `.claude/memory/` for human-readable context).

## What to Git-Track (by agent)

### Hermes (~/.hermes/)
- `memories/MEMORY.md` + `USER.md` → snapshot to `config/agents/hermes/memories/`

### Claude Code (~/.claude/)
- `projects/<encoded-path>/memory/*.md` → snapshot to `config/agents/claude/memory-snapshots/`
  - Especially `feedback_*.md` (user corrections) and `project_*.md` (context)
- `.claude/state/` directories (in-repo): corrections/, patterns/, reflect-history/, cc-insights/, trends/, candidates/, session-signals/, skill-eval-results/
- `.claude/state/` files: learned-patterns.json, skill-scores.yaml, cc-user-insights.yaml, hermes-insights.yaml, cross-agent-memory.yaml, drift-summary.yaml, portfolio-signals.yaml

### Codex (~/.codex/)
- `rules/default.rules` (learned permissions — CRITICAL)
- `history.jsonl`, `session_index.jsonl`
→ snapshot to `config/agents/codex/state-snapshots/`

### Gemini (~/.gemini/)
- `state.json`, `projects.json`
→ snapshot to `config/agents/gemini/state-snapshots/`

## CRITICAL PITFALL: Gitignore Directory vs Glob

This is the #1 gotcha that makes gitignore exceptions silently fail.

### The Bug Pattern
```gitignore
# THIS IS BROKEN — exceptions below are DEAD CODE
.claude/state/        # <-- trailing slash = ignores the DIRECTORY
!.claude/state/corrections/   # <-- NEVER WORKS
```

When git ignores a **directory** (trailing `/`), it never looks inside it, so child exceptions cannot un-ignore anything.

### The Fix (three layers required)
```gitignore
# Layer 1: Top-level ignore with glob (not directory)
.claude/*

# Layer 2: Un-ignore the parent directory itself
!.claude/state/

# Layer 3: Re-ignore contents, THEN add specific exceptions
.claude/state/*
!.claude/state/corrections/
!.claude/state/patterns/
!.claude/state/learned-patterns.json
```

### Verification
```bash
# Check if a file is ignored (should show NO output for tracked files)
git check-ignore -v .claude/state/corrections/foo.jsonl

# If it shows a rule, the exception is NOT working
# The -v flag shows WHICH rule is blocking
```

### Debugging Workflow (when exceptions don't work)
```bash
# Step 1: Check which rule is blocking
git check-ignore -v .claude/state/corrections/foo.jsonl

# Output shows the EXACT line: ".gitignore:127:.claude/*"
# Step 2: Check if there are MULTIPLE blocking rules
git check-ignore -v .claude/state/corrections/ .claude/state/learned-patterns.json

# Step 3: After fixing, verify files CAN be staged
git add .claude/state/corrections/ 2>&1
# If you see "ignored by .gitignore" there's still a blocking rule
```

### Common Failure Modes
1. Parent dir ignored with `/` instead of `/*` — children can never be excepted
2. **Multiple ignore rules at different levels** — e.g., `.claude/*` at line 127 AND `.claude/state/` at line 157. You fix one but the other still blocks. Always run `git check-ignore -v` AFTER each fix to verify
3. Exception added but files never `git add`-ed — the gitignore exception alone doesn't track files
4. **Cron uses inline command instead of script** — after updating a backup script, verify the crontab actually calls the script (not an old inline rsync)

## Nightly Pipeline Integration

Script: `scripts/cron/commit-learning-artifacts.sh`

Steps:
1. Snapshot agent memories from home dirs to `config/agents/*/`
2. `git add` all state directories and snapshot directories
3. Run `legal-sanity-scan.sh --diff-only` (MANDATORY — corrections and session data can contain client names)
4. Commit and push if changed

Wire into: `comprehensive-learning-nightly.sh` as final step.

## Session-Signal Redaction

`session-signals/*.jsonl` files contain a `last_assistant_message` field with full LLM response text. This text often references client project names (from doc-intelligence classification outputs). The field must be redacted before git-add.

Script: `scripts/cron/redact-session-signals.sh`
- Scans all `.claude/state/session-signals/*.jsonl`
- Replaces `last_assistant_message` with `[REDACTED]` using Python JSON parsing
- Preserves all metadata fields (session_id, hook_event_name, permission_mode, etc.)
- Must run BEFORE `git add` in the nightly pipeline

## Codex Session Export

Codex sessions live at `~/.codex/sessions/YYYY/MM/DD/rollout-*.jsonl` in a different format than Claude/Hermes.

Key Codex JSONL types:
- `session_meta` — session ID, cwd, model provider
- `response_item` with `payload.type == "function_call"` — tool calls
- `response_item` with `payload.type == "function_call_output"` — results
- Tool names: `exec_command`, `read_file`, `write_file`, `apply_diff`, `write_stdin`, `list_directory`

Script: `scripts/cron/codex-session-export.sh`
- Exports to `logs/orchestrator/codex/session_YYYYMMDD.jsonl`
- Maps Codex tool names to orchestrator conventions (exec_command→Bash, etc.)
- Incremental via `.last-export-ts` timestamp file

## Legal Risk

Session signals, corrections, and memory files can contain client project names. The legal scan MUST gate all commits. If it finds violations, skip the commit rather than pushing sensitive data.

Key mitigation: run `redact-session-signals.sh` before staging. The session-signals directory is the #1 source of legal violations (522 hits in first attempt without redaction).

## Backup Coverage (Tier 2)

`scripts/cron/memory-backup.sh` rsyncs to ace-linux-2 daily:
- Claude project memory (`~/.claude/projects/`)
- Hermes memories + sessions (`~/.hermes/memories/`, `~/.hermes/sessions/`)
- Codex sessions + rules (`~/.codex/sessions/`, `~/.codex/rules/`)
- Gemini sessions (`~/.gemini/tmp/`)

Use `ssh -o ConnectTimeout=10 -o BatchMode=yes` for non-interactive cron. Non-critical agents use `|| true` to not abort.

## Restore on New Machine

Script: `scripts/_core/sync-agent-configs.sh` (restore section)

Behavior: only copies if target files are MISSING (safe on existing machines). Use `--force` to overwrite.

- Hermes: copies `.snapshot` files → `~/.hermes/memories/` (strips .snapshot suffix)
- Claude: copies `config/agents/claude/memory-snapshots/*.md` → encoded project path, additive (skips existing)
- Codex: copies `default.rules`, `history.jsonl`, `session_index.jsonl`
- Gemini: copies `state.json`, `projects.json`

Claude project path encoding: `/mnt/local-analysis/workspace-hub` → `-mnt-local-analysis-workspace-hub`
