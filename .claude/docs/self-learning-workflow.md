# Self-Learning Workflow
*The single canonical reference for how the ecosystem improves itself.*
*WRK-233 | Updated: 2026-02-20*

## The Loop (linear)

SESSION RUNS
  ↓
SESSION ENDS
  → session-signals.sh fires (<2s, lightweight)
  → writes raw signals to state/session-signals/
  ↓
3AM CRON — session-analysis.sh
  → reads previous day's signals
  → scores skills → skill-scores.yaml
  → routes candidates:
      script-candidates.md  → scripts
      skill-candidates.md   → skills curation (WRK-229)
      hook-candidates.md    → hooks
      agent-candidates.md   → agent library
      mcp-candidates.md     → MCP servers
  → deep gaps → new WRK items (auto-created)
  → anti-patterns → preflight hook (WRK-226)
  → writes session-analysis/YYYY-MM-DD.md
  ↓
5AM — claude-reflect
  → reads session-analysis output
  → cross-repo git history reflection
  ↓
WEEKLY — agentic-horizon skill
  → reassesses all active WRK item dispositions
  → surfaces park dates elapsed, stale do-now items
  → mines newly-archived items for follow-ups
  ↓
NEXT SESSION STARTS
  → preflight loads session-analysis/YYYY-MM-DD.md
  → better skills, fresh gaps queued, noise reduced
  ↓
REPEAT — system improves with every session

## Skill Positions in the Loop

| Skill | Position | Responsibility |
|-------|----------|----------------|
| `session-signals` | Session end (hook) | Raw signal capture only |
| `session-analysis` | 3AM cron | Heavy analysis + routing |
| `claude-reflect` | 5AM cron | Git history + cross-repo patterns |
| `skills-curation` | Weekly | New skills from signals + online research |
| `agentic-horizon` | Weekly | Horizon reassessment of all WRK items |
| `session-bootstrap` | Once per machine | Historical baseline |
| `work-queue` | Per session | WRK item creation and processing |
| `claude-reflect` | Daily/weekly | Feeds into session-analysis context |
| `improve` | Session end | Prompted improvement, feeds candidates |

## Document Status

Each existing workflow document slots into the loop as follows:

| Document | Location | Position in loop | Status |
|----------|----------|-----------------|--------|
| process.md | .claude/work-queue/ | WRK item lifecycle | Current |
| session-lifecycle.md | .claude/docs/ | Full session flow | Needs update for WRK-230/231 |
| claude-reflect SKILL.md | .claude/skills/.../ | 5AM cron step | Current |
| skill-learner SKILL.md | .claude/skills/.../ | Consumer of session-analysis | Review needed |
| improve SKILL.md | .claude/skills/.../ | Session-end contributor | Review needed |
| hooks/ scripts | .claude/hooks/ | Session-end triggers | Simplified by WRK-231 |

## What Is Not In This Document

Complexity lives elsewhere:
- Knowledge graphs: `.claude/skills/SKILLS_GRAPH.yaml`
- Skill scorecards: `.claude/state/skill-scores.yaml`
- Candidate queues: `.claude/state/candidates/`
- WRK item detail: `.claude/work-queue/`

This document is the map. The detail is in the territory.
