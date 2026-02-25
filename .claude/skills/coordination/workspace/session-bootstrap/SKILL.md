---
name: session-bootstrap
description: One-time historical session analysis per machine — mines all sessions to produce initial skill scorecard baseline; run once per machine after WRK-231 is delivered
version: 1.0.0
category: workspace-hub
type: skill
trigger: manual
cadence: once-per-machine
auto_execute: false
capabilities:
  - historical_session_mining
  - skill_scorecard_bootstrap
  - gap_wrk_creation
  - machine_stamping
tools: [Read, Write, Edit, Bash, Grep, Glob]
related_skills: [session-analysis, work-queue, agentic-horizon]
scripts:
  - scripts/analysis/session-analysis.sh
see_also:
  - .claude/work-queue/working/WRK-232.md
  - .claude/state/skill-scores.yaml
  - .claude/state/session-analysis/
---

# Session Bootstrap Skill

> One-time per-machine skill. Mines all historical sessions to produce the initial skill performance scorecard. Run once after WRK-231 is delivered; never needs to run again unless `--force` is passed.

## When to Run

Run once on every machine where Claude Code has been used:
```bash
/session-bootstrap
```

Check idempotency stamp first:
```bash
cat .claude/state/session-analysis/bootstrap.json 2>/dev/null || echo "not yet run"
```

## What It Does

1. Discovers all sessions on the current machine (`~/.claude/state/sessions/` + `~/.claude/projects/*/sessions/`)
2. Mines for skill invocations, correction events, tool patterns, knowledge gap indicators
3. Writes baseline skill scorecard to `skill-scores.yaml`
4. Produces human-readable report at `.claude/state/session-analysis/bootstrap-YYYY-MM-DD.md`
5. Auto-creates WRK items for knowledge gaps recurring 3+ times
6. Stamps the machine with `bootstrap.json` — re-running skips unless `--force` is passed

## Output Files

| File | Contents |
|------|----------|
| `.claude/state/skill-scores.yaml` | Baseline skill scorecard (usage, one-shot, corrections) |
| `.claude/state/session-analysis/bootstrap-YYYY-MM-DD.md` | Human-readable findings report |
| `.claude/state/session-analysis/bootstrap.json` | Idempotency stamp with session count and stats |

## Run Protocol

After WRK-231 is delivered, run on every machine:
```bash
# On each machine:
/session-bootstrap

# Check output:
cat .claude/state/session-analysis/bootstrap-$(date +%Y-%m-%d).md
```

Known machines with session data:
- `ace-linux-1` (primary — 241+ sessions)
- Any other machines where Claude Code has been run

## Re-running

If `bootstrap.json` already exists, the skill prints a summary and exits. To force a full re-run:
```bash
rm .claude/state/session-analysis/bootstrap.json && /session-bootstrap
```
