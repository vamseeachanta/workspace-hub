# Nightly GSD Researcher — Design Spec

**Issue:** #1434 — Set up nightly GSD researcher agents
**Date:** 2026-03-25
**Status:** Approved

## Goal

Enrich PROJECT.md with continuously discovered patterns, standards updates, and ecosystem changes via automated nightly research using the Claude CLI.

## Architecture

```
crontab (1:30 AM daily, dev-primary only)
  └─ scripts/cron/gsd-researcher-nightly.sh
       ├─ Picks domain by day-of-week
       ├─ Pipes PROJECT.md + ROADMAP.md as stdin context
       ├─ echo "$CONTEXT" | timeout 180 claude -p "$PROMPT" > output
       ├─ Writes .planning/research/YYYY-MM-DD-<domain>.md
       ├─ Best-effort git commit + push
       ├─ Logs to logs/research/YYYY-MM-DD.log
       └─ Notifies via scripts/notify.sh

daily_today.sh (6 AM, existing)
  └─ Scans .planning/research/ for files modified in last 24h
  └─ Appends "Research Highlights" section to morning digest
```

## Domain Rotation

| Day       | Domain             | Focus                                                        |
|-----------|--------------------|--------------------------------------------------------------|
| Mon, Thu  | `standards`        | Offshore/subsea standards (API, DNV, ABS, ISO) updates       |
| Tue, Fri  | `python-ecosystem` | Dependencies, uv changes, packaging, tier-1 package impacts  |
| Wed, Sat  | `ai-tooling`       | Claude/Codex/Gemini CLI changes, MCP, agent patterns         |
| Sunday    | `synthesis`        | Review week's findings, flag top insights for promotion       |

## Script: gsd-researcher-nightly.sh

### Structure

1. **Preflight:** hostname guard (`dev-primary` only), `set -euo pipefail`, `git pull`
2. **Domain selection:** `case $(date +%u)` maps day number to domain name + prompt
3. **Context assembly:** `cat .planning/PROJECT.md .planning/ROADMAP.md` into `$CONTEXT`
4. **Research call:** `echo "$CONTEXT" | timeout 180 claude -p "$PROMPT" > $OUTPUT_FILE`
5. **Output:** `.planning/research/YYYY-MM-DD-<domain>.md`
6. **Commit:** best-effort `git add + commit + push` (failure logged, not fatal)
7. **Log:** `logs/research/YYYY-MM-DD.log` via `tee -a`
8. **Notify:** `bash scripts/notify.sh` with pass/fail status

### Domain Prompts

Each domain prompt instructs the researcher to:
- Search for recent developments in the domain
- Evaluate relevance to the project (using PROJECT.md context)
- Output structured findings in the standard format

**Sunday synthesis** prompt reads all `.planning/research/` files from the past week and produces a ranked list of actionable insights.

### Output Format (researcher produces)

```markdown
# Research: <domain> — YYYY-MM-DD

## Key Findings
- Finding with source/reference
- ...

## Relevance to Project
- How finding affects specific package/workflow

## Recommended Actions
- [ ] Actionable item (promote to PROJECT.md / create issue / ignore)
```

## Morning Summary Integration

Extend `scripts/productivity/daily_today.sh` to:
1. Scan `.planning/research/` for files modified in the last 24h
2. Extract `## Key Findings` section from each
3. Append a "Research Highlights" block to the morning digest

## Schedule Configuration

Add to `config/scheduled-tasks/schedule-tasks.yaml`:

```yaml
- name: gsd-researcher
  schedule: "30 1 * * *"
  command: bash scripts/cron/gsd-researcher-nightly.sh
  log: logs/research/$(date +%Y-%m-%d).log
  is_claude_task: true
  description: Nightly domain research rotating standards/python/AI
```

## Files to Create/Modify

| Action | File                                           |
|--------|------------------------------------------------|
| Create | `scripts/cron/gsd-researcher-nightly.sh`       |
| Create | `.planning/research/` directory (with .gitkeep) |
| Create | `logs/research/` directory                      |
| Modify | `config/scheduled-tasks/schedule-tasks.yaml`   |
| Modify | `scripts/productivity/daily_today.sh`          |

## Cost & Safety

- **Token cost:** 1 Claude call per night (~180s timeout)
- **Failure mode:** Best-effort — logged and notified, does not block other cron jobs
- **Host guard:** Only runs on `dev-primary`
- **Retention:** Research files accumulate; weekly synthesis provides rollup

## Success Criteria (from #1434)

- [ ] Nightly job running reliably
- [ ] Research artifacts accumulating in `.planning/research/`
- [ ] At least one insight actioned within the first week
