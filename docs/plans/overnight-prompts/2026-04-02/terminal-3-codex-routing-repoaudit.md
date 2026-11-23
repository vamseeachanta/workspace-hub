# Terminal 3 — Codex: Agent Routing Intelligence + Per-Repo Ecosystem Audit

## Context
We are in /mnt/local-analysis/workspace-hub on ace-linux-1.
This is an analysis-only session for GH issue #1720.
Use `uv run` for all Python. Do NOT ask the user any questions.
Do NOT modify any skills, scripts, or source code.
Commit to main and push after each major deliverable.
`git pull origin main --rebase` before every push.

## YOUR WRITE TERRITORY
- `analysis/cross-agent-audit-20260402/phase-e-agent-routing.md`
- `analysis/cross-agent-audit-20260402/phase-g-repo-ecosystem.md`
- `analysis/cross-agent-audit-20260402/phase-e-data/`
- `analysis/cross-agent-audit-20260402/phase-g-data/`

## DO NOT WRITE TO
- `analysis/cross-agent-audit-20260402/phase-a-*` (Terminal 1)
- `analysis/cross-agent-audit-20260402/phase-b-*` (Terminal 1)
- `analysis/cross-agent-audit-20260402/phase-c-*` (Terminal 2)
- `analysis/cross-agent-audit-20260402/phase-d-*` (Terminal 2)
- `analysis/cross-agent-audit-20260402/phase-f-*` (Terminal 2)
- Any file outside `analysis/`

---

## TASK 1: Phase E — Agent Routing Intelligence

### Data sources
1. Claude orchestrator: `logs/orchestrator/claude/session_*.jsonl` — 153,884 tool calls
   Fields: ts, hook, tool, project, repo, cmd (for Bash), file (for Read/Edit/Write)

2. Hermes orchestrator: `logs/orchestrator/hermes/session_*.jsonl` — 13,554 tool calls
   Fields: ts, hook, tool, hermes_tool, project, repo, model, cmd, file, skill_name, etc.

3. Codex orchestrator: `logs/orchestrator/codex/` — 410 files
   Mix of WRK review logs (WRK-*.log) and session logs (session_*.log)
   WRK logs contain cross-review verdicts (APPROVE/MINOR/MAJOR)

4. Gemini orchestrator: `logs/orchestrator/gemini/` — 219 files
   Similar mix of WRK review logs and session logs

5. Existing routing config: `config/agents/routing-config.yaml`
6. Existing capabilities: `config/agents/provider-capabilities.yaml`

### Analysis to produce

1. **Per-agent domain affinity**: For each agent, which repos/directories does it work on most?
   - Claude: parse repo field + file paths
   - Hermes: parse file paths + cmd working directories
   - Codex: parse WRK titles and file references in review logs
   - Gemini: parse WRK titles and file references in review logs

2. **Per-agent tool profile**: What's the tool distribution for each agent?
   - Claude: heavy Bash user? Read-heavy (research) vs Write-heavy (implementation)?
   - Hermes: terminal-heavy? More skill_view usage? More delegate_task?
   - Codex: review-focused? What percentage of activity is cross-review vs direct work?

3. **Per-agent task complexity**: Infer from tool-call sequences:
   - Average tool calls per session/WRK item
   - Ratio of Read/Grep (research) to Write/Edit (implementation)
   - Use of Agent/Task/delegate_task (decomposition capability)
   - Session length distribution

4. **Cross-review patterns**: From Codex and Gemini WRK logs:
   - Verdict distribution (APPROVE/MINOR/MAJOR per reviewer)
   - Which types of work get MAJOR verdicts? (extract from WRK title/content)
   - Reviewer agreement rate (when both review the same WRK)

5. **Routing recommendations**: Based on the above, produce a table:

   | Task Type | Recommended Agent | Reason |
   |-----------|-------------------|--------|
   | High-context synthesis | ? | ? |
   | Bounded implementation | ? | ? |
   | Cross-review | ? | ? |
   | Documentation | ? | ? |
   | Data analysis | ? | ? |
   | Skill creation | ? | ? |

6. **Capability gap**: Things no agent handles well (high correction rate, many retries).

### Output
Write `analysis/cross-agent-audit-20260402/phase-e-agent-routing.md`:
- Per-agent domain affinity tables
- Per-agent tool profiles
- Task complexity metrics
- Cross-review verdict analysis
- Routing recommendation table
- Capability gaps

Compare findings against existing `config/agents/routing-config.yaml` and `provider-capabilities.yaml` — flag any mismatches between current config and observed behavior.

### Commit
```
chore(analysis): Phase E — agent routing intelligence from session corpus (#1720)
```

---

## TASK 2: Phase G — Per-Repo Ecosystem Audit

### Data sources
1. All 24 repos with `.claude/` directories:
   ```
   find /mnt/local-analysis/workspace-hub -maxdepth 2 -name '.claude' -type d
   ```
2. For each repo, check:
   - `.claude/skills/` — count, categories
   - `.claude/commands/` — count, list
   - `.claude/docs/` — count, list
   - `.claude/memory/` — exists?
   - `.claude/state/` — exists?
   - `.claude/rules/` — exists?
   - `.claude/work-queue/` — exists, pending items?
   - `AGENTS.md` — exists, is it a pointer or standalone?
   - `CLAUDE.md` — exists, line count, is it a pointer or standalone?
3. Git activity per repo: `git log --since=2026-01-01 --oneline` (count commits in last 90 days)
4. Tier classification from `scripts/readiness/harness-config.yaml`:
   ```yaml
   tier1_repos:
     - assetutilities
     - digitalmodel
     - worldenergydata
     - assethold
   ```

### Analysis to produce

1. **Ecosystem inventory table**: For each of 24 repos:

   | Repo | Skills | Cmds | Docs | Rules | WQ | AGENTS | CLAUDE | Git Activity (90d) | Tier |
   |------|--------|------|------|-------|----|--------|--------|--------------------|------|

2. **AGENTS.md consistency check**: For each repo:
   - Is it a pointer (`inherits the canonical contract`) or standalone?
   - If standalone: does `entry_points` match actual source structure?
   - If standalone: does `test_command` actually work? (don't run it, just check if the test dir exists)
   - Does `depends_on` list match actual imports?

3. **CLAUDE.md freshness**: For each repo:
   - Last modification date
   - Does it reference WRK items? Are they stale (done/archived)?
   - Does `## Repo Overrides` section contain any content?

4. **Command staleness**: For repos with commands:
   - Do commands reference files/paths that still exist?
   - Are any commands duplicated across repos?

5. **Skill promotion candidates**: Skills in nested repos that should be promoted to workspace-hub:
   - Skills in CAD-DEVELOPMENTS that are domain-general (not CAD-specific)
   - Skills in worldenergydata that could serve digitalmodel too
   - Skills in achantas-data that are data-analysis patterns

6. **Repos needing attention**:
   - High git activity but no skills/docs (under-served)
   - Many skills but zero git activity (over-invested/stale)
   - Tier-1 repos missing any ecosystem component

### Output
Write `analysis/cross-agent-audit-20260402/phase-g-repo-ecosystem.md`:
- Full 24-repo inventory table
- AGENTS.md consistency findings
- CLAUDE.md freshness findings
- Command staleness flags
- Skill promotion candidates
- Repos needing attention (prioritized list)

### Commit
```
chore(analysis): Phase G — per-repo ecosystem audit across 24 repos (#1720)
```

---

Post a brief progress comment on GH issue #1720 when done:
```
Terminal 3 (Codex) complete:
- Phase E: agent routing intelligence at analysis/cross-agent-audit-20260402/phase-e-agent-routing.md
  - Routing recommendations for [N] task types
  - [N] capability gaps identified
- Phase G: per-repo ecosystem audit at analysis/cross-agent-audit-20260402/phase-g-repo-ecosystem.md
  - [N] repos audited, [N] needing attention
  - [N] skill promotion candidates
```
