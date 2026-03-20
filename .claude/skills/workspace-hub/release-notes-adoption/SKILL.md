---
name: release-notes-adoption
description: 'Use when new Claude Code, Codex, or Gemini release notes are available
  and you need to identify ecosystem improvements, capture WRK items, and keep config/ai-tools/release-scan-state.yaml
  current. Start with Claude provider.

  '
version: 1.0.0
updated: 2026-03-12
category: workspace-hub
triggers:
- release notes
- new cc version
- claude code update
- codex update
- gemini update
- what's new in claude
- adopt release improvements
related_skills:
- work-queue
- work-queue-workflow
capabilities:
- release-notes-analysis
- wrk-capture
- version-state-tracking
requires: []
invoke: release-notes-adoption
tags:
- automation
- release
- work-queue
---

# Release Notes Adoption

> Scan new AI-tool release notes for ecosystem improvements → create WRK items
> → update version state → commit + push. Runs manually or via nightly cron.

## Quick Start

```bash
# 1. Get latest notes
claude /release-notes          # for Claude Code releases

# 2. Check last-seen version
cat config/ai-tools/release-scan-state.yaml

# 3. Run this skill with the new content → WRK items are created
# 4. Commit + push (always push immediately after commit)
```

## Step 1 — Get Release Notes

| Provider | Command | Cadence |
|---|---|---|
| Claude Code | `claude /release-notes` | On demand or nightly cron |
| Codex | `codex changelog` / `--version` | Monthly |
| Gemini | `gemini --version` / changelog | Monthly |

Start with **Claude** first. Codex and Gemini are lower priority.

## Step 2 — Diff Against Last-Seen Version

```bash
cat config/ai-tools/release-scan-state.yaml
# last_seen_version: { claude: "2.1.71", codex: "...", gemini: "..." }
```

Filter release notes to versions **after** `last_seen_version`. Ignore older entries.

## Step 3 — Analysis: What Is Actionable?

Flag items that require a config change, script update, or workflow adjustment:

| Category | Flag if… |
|---|---|
| `settings.json` / env vars | New setting we should adopt |
| CLAUDE.md behaviour | Change to injection, parsing, or comment handling |
| Hooks | New hook events relevant to session-start/end/merge hooks |
| Skills / slash commands | New built-in capability we can wire into a skill |
| Memory / auto-memory | Path, directory, or behaviour change |
| Worktrees | Fix or feature relevant to our worktree workflow |
| Performance | Opt-in optimisation worth enabling |
| Security | Any security fix → priority `high` |

**Skip automatically:** Bug fixes that apply without config change, UX polish,
Windows-only fixes, IDE-only fixes, Bedrock/Vertex/Foundry-specific items.

## Step 4 — Create WRK Items

For each actionable group (batch related items into one WRK when possible):

```bash
NEXT_ID=$(bash scripts/work-queue/next-id.sh)
# write .claude/work-queue/pending/WRK-${NEXT_ID}.md (see template below)
uv run --no-project python .claude/work-queue/scripts/generate-index.py
```

**WRK frontmatter defaults for release-adoption items:**

```yaml
category: harness
subcategory: tooling
priority: medium          # high for security fixes
complexity: simple        # medium if script changes needed
computer: dev-primary
release_notes_source: claude-X.Y.Z-A.B.C   # version range covered
```

## Step 5 — Update State File

```yaml
# config/ai-tools/release-scan-state.yaml
last_seen_version:
  claude: "2.1.74"     # bump to latest processed version
  codex: "..."
  gemini: "..."
last_scan_at: "2026-03-12T00:00:00Z"
```

## Step 6 — Commit and Push

```bash
git add .claude/work-queue/pending/WRK-*.md \
        .claude/work-queue/INDEX.md \
        config/ai-tools/release-scan-state.yaml
git commit -m "chore(release-scan): capture CC vX.Y.Z–A.B.C improvements as WRK items"
git push
```

**Always push immediately after commit** — never leave commits unpushed.

## Nightly Automation

This skill is the manual path. The automated path (WRK-1140) will call
`scripts/automation/nightly-release-scan.sh` which runs the same logic
unattended. The state file is the shared handoff point between both paths.

## Example Output (v2.1.72–2.1.74)

Three actionable items → one WRK (WRK-1139):
- CLAUDE.md HTML comments hidden from auto-injection → reduce injected tokens
- `autoMemoryDirectory` setting → align auto-memory with existing memory dir
- `CLAUDE_CODE_SESSIONEND_HOOKS_TIMEOUT_MS` → prevent silent hook kill at 1.5s

Skipped: ~40 bug fixes, VSCode-only items, Windows-only items.
