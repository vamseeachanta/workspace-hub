---
title: Claude Reflect - RAGS Loop with Correction Learning
description: Automated learning from AI/user interactions via git history and correction patterns
version: 1.0.0
module: claude-reflect
created: 2026-01-21
session:
  id: 2026-01-21-eod
  agent: claude-opus-4.5
review:
  status: implemented
  iterations: 1
---

# Claude Reflect - RAGS Loop with Correction Learning

## Overview

Claude Reflect implements a RAGS (Reflect → Abstract → Generalize → Store) loop that learns from:
1. Git commit history across all workspace-hub submodules
2. AI/user correction patterns captured via hooks

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         CORRECTION CAPTURE LAYER                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Any Repo                          workspace-hub                            │
│  ┌─────────────────┐              ┌─────────────────────────────────────┐  │
│  │ .claude/hooks/  │              │ .claude/state/ (gitignored)         │  │
│  │ capture-        │──────────────│ ├── corrections/                    │  │
│  │ corrections.sh  │   writes to  │ │   ├── session_YYYYMMDD.jsonl     │  │
│  └─────────────────┘              │ │   └── .recent_edits              │  │
│                                   │ ├── patterns/                       │  │
│  Claude Code                      │ ├── reflect-history/                │  │
│  PostToolUse Hook                 │ ├── trends/                         │  │
│  (Edit/Write)                     │ └── reports/                        │  │
│                                   └─────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
                                         │
                                         ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                            RAGS LOOP (5 AM Cron)                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  PHASE 1: REFLECT                 PHASE 2: ABSTRACT                         │
│  ┌─────────────────────┐          ┌─────────────────────┐                  │
│  │ analyze-history.sh  │          │ extract-patterns.sh │                  │
│  │ • 26+ submodules    │────────▶ │ • Commit patterns   │                  │
│  │ • 30-day git log    │          │ • Cross-repo trends │                  │
│  │ • Commits, authors  │          └─────────────────────┘                  │
│  └─────────────────────┘                    +                               │
│                                   ┌─────────────────────┐                  │
│                                   │extract-corrections  │                  │
│                                   │ • Re-edit patterns  │                  │
│                                   │ • Quick fix vs      │                  │
│                                   │   iterative refine  │                  │
│                                   └─────────────────────┘                  │
│                                             │                               │
│                                             ▼                               │
│  PHASE 3: GENERALIZE              PHASE 4: STORE                           │
│  ┌─────────────────────┐          ┌─────────────────────┐                  │
│  │ analyze-trends.sh   │          │ create-skills.sh    │                  │
│  │ • 7-day rolling     │────────▶ │ • Score >= 0.8:     │                  │
│  │ • Velocity trends   │          │   Create skill      │                  │
│  │ • Quality indicators│          │ • Score 0.6-0.79:   │                  │
│  └─────────────────────┘          │   Enhance existing  │                  │
│                                   └─────────────────────┘                  │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Components

### 1. Correction Capture Hook

**File:** `.claude/hooks/capture-corrections.sh`

**Trigger:** PostToolUse hook in `.claude/settings.json`

**Logic:**
- Tracks all file edits in `.recent_edits`
- If same file edited within 10 minutes → logged as "correction"
- Captures: timestamp, file, tool, gap_seconds, diff_stat

**Performance:** ~35ms per edit, non-blocking

**Data Format (JSONL):**
```json
{
  "timestamp": "2026-01-21T22:17:30-06:00",
  "file": "/path/to/file.py",
  "basename": "file.py",
  "tool": "Edit",
  "correction_gap_seconds": 11,
  "diff_stat": "1 file changed, 5 insertions(+)",
  "type": "correction"
}
```

### 2. RAGS Scripts

| Script | Phase | Input | Output |
|--------|-------|-------|--------|
| `daily-reflect.sh` | Orchestrator | - | Runs all phases |
| `analyze-history.sh` | Reflect | Git repos | `analysis_*.json` |
| `extract-patterns.sh` | Abstract | Analysis | `patterns_*.json` |
| `extract-corrections.sh` | Abstract | Corrections | Correction patterns |
| `analyze-trends.sh` | Generalize | Patterns | `trends_*.json` |
| `create-skills.sh` | Store | Patterns | Auto-generated skills |

### 3. State Directory Structure

```
workspace-hub/.claude/state/
├── corrections/           # Hook captures (cross-repo)
│   ├── session_YYYYMMDD.jsonl
│   └── .recent_edits
├── patterns/              # Extracted patterns
│   ├── patterns_*.json
│   └── corrections_*.json
├── reflect-history/       # Raw git analysis
│   ├── analysis_*.json
│   └── reflect.log
├── trends/                # Cross-day trends
│   └── trends_*.json
├── reports/               # Weekly digests
│   └── weekly_digest_*.md
└── memory/                # Learnings storage
    └── patterns/
```

### 4. Cron Schedule

| Time | Job | Purpose |
|------|-----|---------|
| 5 AM | `daily-reflect.sh` | Full RAGS loop |
| 6 AM | `context-management` | CLAUDE.md health |
| 6 AM | `repo-maintenance` | Repo cleanup |

## Configuration

### Environment Variables

| Variable | Default | Purpose |
|----------|---------|---------|
| `WORKSPACE_HUB` | `/mnt/github/workspace-hub` | Central state location |
| `WORKSPACE_STATE_DIR` | `$WORKSPACE_HUB/.claude/state` | Override state path |
| `CLAUDE_CAPTURE_CORRECTIONS` | `true` | Enable/disable hook |
| `REFLECT_DAYS` | `30` | Git history window |
| `DRY_RUN` | `false` | Preview without creating skills |

### Skill Creation Thresholds

In `create-skills.sh`:
```bash
THRESHOLD_CREATE=0.8    # Create new skill
THRESHOLD_ENHANCE=0.6   # Enhance existing
```

**Scoring Formula:**
```
score = (frequency × 0.3) + (cross_repo × 0.3) + (complexity × 0.2) + (time_savings × 0.2)
```

## Multi-Machine Usage

### Scenario: Work on Machine A, RAGS on Machine B

1. **Machine A:** Work in any repo with hooks installed
   - Corrections saved to `workspace-hub/.claude/state/`

2. **Sync:** Push workspace-hub to git

3. **Machine B:** Pull workspace-hub
   - 5 AM cron runs RAGS loop
   - Analyzes corrections from Machine A

### Installing Hooks in Other Repos

```bash
/mnt/github/workspace-hub/.claude/skills/workspace-hub/claude-reflect/install-hooks.sh /path/to/other-repo
```

This installs:
- `.claude/hooks/capture-corrections.sh` (points to workspace-hub state)
- Updates `.claude/settings.json` with PostToolUse hook

## Future Enhancements

### Phase 2: Enhanced Correction Learning

- [ ] Capture prompt context (what user said to trigger correction)
- [ ] Track correction chains (file A → B → C)
- [ ] Detect correction patterns by file type
- [ ] ML-based pattern scoring

### Phase 3: Active Learning

- [ ] Suggest improvements during editing (pre-emptive)
- [ ] Auto-generate templates for high-correction areas
- [ ] Integration with IDE for real-time hints

### Phase 4: Cross-Team Learning

- [ ] Anonymized pattern sharing across teams
- [ ] Skill marketplace from learned patterns
- [ ] Benchmark correction rates across projects

### Technical Debt

- [ ] Lower skill creation thresholds (0.8 → 0.6)
- [ ] Add cleanup for old correction files
- [ ] Add metrics dashboard for RAGS insights
- [ ] Support for non-git repos

## Testing

### Manual Hook Test
```bash
# Clear state
rm -f workspace-hub/.claude/state/corrections/*

# Make two edits to same file within 10 min
# Check: workspace-hub/.claude/state/corrections/session_*.jsonl
```

### Manual RAGS Test
```bash
DRY_RUN=true REFLECT_DAYS=7 ./daily-reflect.sh
```

## References

- **Hook Script:** `.claude/hooks/capture-corrections.sh`
- **RAGS Scripts:** `.claude/skills/workspace-hub/claude-reflect/scripts/`
- **Install Script:** `.claude/skills/workspace-hub/claude-reflect/install-hooks.sh`
- **Settings:** `.claude/settings.json` (PostToolUse hooks)
- **Cron Setup:** `.claude/skills/workspace-hub/claude-reflect/scripts/setup_cron.sh`
