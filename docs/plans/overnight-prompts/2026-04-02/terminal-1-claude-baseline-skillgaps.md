# Terminal 1 — Claude Code: Cross-Agent Baseline + Skill Gap Detection

## Context
We are in /mnt/local-analysis/workspace-hub on ace-linux-1.
This is an analysis-only session for GH issue #1720.
Use `uv run` for all Python. Do NOT ask the user any questions.
Do NOT write to any path outside `analysis/cross-agent-audit-20260402/`.
Do NOT modify any skills, scripts, or source code.
Commit to main and push after each major deliverable.
`git pull origin main --rebase` before every push.

## YOUR WRITE TERRITORY
- `analysis/cross-agent-audit-20260402/phase-a-baseline.md`
- `analysis/cross-agent-audit-20260402/phase-b-skill-gaps.md`
- `analysis/cross-agent-audit-20260402/phase-a-data/` (intermediate data)
- `analysis/cross-agent-audit-20260402/phase-b-data/` (intermediate data)

## DO NOT WRITE TO
- `analysis/cross-agent-audit-20260402/phase-c-*` (Terminal 2)
- `analysis/cross-agent-audit-20260402/phase-d-*` (Terminal 2)
- `analysis/cross-agent-audit-20260402/phase-f-*` (Terminal 2)
- `analysis/cross-agent-audit-20260402/phase-e-*` (Terminal 3)
- `analysis/cross-agent-audit-20260402/phase-g-*` (Terminal 3)
- Any file outside `analysis/`

---

## TASK 1: Phase A — Cross-Agent Tool & File Frequency Baseline

### Data sources
1. Claude orchestrator: `logs/orchestrator/claude/session_*.jsonl` — 24 files, 153,884 lines
   Format per line: `{"ts":"...","hook":"post","tool":"Bash","project":"workspace-hub","repo":"workspace-hub","cmd":"..."}`
   Tool field is one of: Bash, Read, Edit, Write, Grep, Glob, Agent, Skill, etc.
   `cmd` present for Bash, `file` present for Read/Edit/Write.

2. Hermes orchestrator: `logs/orchestrator/hermes/session_*.jsonl` — 2 files, 13,554 lines
   Format: `{"ts":"...","hook":"post","tool":"Bash","hermes_tool":"terminal","project":"workspace-hub","cmd":"..."}`
   Has `hermes_tool` field with native tool name (terminal, read_file, search_files, etc.)

3. Codex orchestrator: `logs/orchestrator/codex/` — 410 files (WRK logs + session logs)
   Format varies: some are JSONL, some are plain text logs.

### Analysis to produce

1. **Top 50 files by read frequency** — per agent and combined. Parse `file` fields from Read/read_file tool calls.
2. **Top 50 files by write/edit frequency** — per agent and combined. Parse `file` fields from Write/Edit/write_file/patch calls.
3. **Top 20 bash commands** — per agent. Parse `cmd` fields, normalize (strip paths, args), cluster similar commands.
4. **Tool call distribution** — per agent and combined: {tool: count, pct}
5. **Temporal pattern** — tool calls per day, per agent
6. **Repo distribution** — for Claude: `repo` field; for Hermes: infer from `file`/`cmd` paths
7. **Co-occurrence matrix** — which repos/files are always worked on together in the same session?

### Output
Write `analysis/cross-agent-audit-20260402/phase-a-baseline.md` with all tables and findings.
Save intermediate parsed data to `analysis/cross-agent-audit-20260402/phase-a-data/` as CSV or JSON for other terminals to use.

### Commit
```
chore(analysis): Phase A — cross-agent tool/file frequency baseline (#1720)
```

---

## TASK 2: Phase B — Skill Gap Detection

### Data sources
1. Phase A output (from Task 1 above) — file frequency, command patterns
2. All skills across 5 repos:
   - `/mnt/local-analysis/workspace-hub/.claude/skills/` (387 active, skip `_archive/`,`_internal/`,`_runtime/`,`_core/`,`session-logs/`)
   - `/mnt/local-analysis/workspace-hub/CAD-DEVELOPMENTS/.claude/skills/` (182 active)
   - `/mnt/local-analysis/workspace-hub/worldenergydata/.claude/skills/` (20 active)
   - `/mnt/local-analysis/workspace-hub/achantas-data/.claude/skills/` (13 active)
   - `/mnt/local-analysis/workspace-hub/assetutilities/.claude/skills/` (3 active)
3. skill-scores.yaml: `.claude/state/skill-scores.yaml` (547 skills with usage stats)
4. Hermes local skills: `~/.hermes/skills/` (86 skills)

### Analysis to produce

1. **Multi-step workflow extraction**: From the Claude/Hermes JSONL, find sequences of ≥5 consecutive tool calls that:
   - Don't include a skill invocation (no `tool: Skill` or `hermes_tool: skill_view`)
   - Touch related files (same directory or module)
   - Repeat across ≥2 sessions
   These are manual workflows that should be skills.

2. **Skill coverage map**: For each directory/module frequently worked on (from Phase A top-50 files):
   - Is there a matching skill? (check skill `triggers`, `name`, `description` fields)
   - If no skill: flag as gap

3. **Skill-to-work alignment**: From skill-scores.yaml, which skills with `tier: active` are actually being used in sessions? Which `tier: dead` skills cover domains that ARE being worked on?

4. **Gap candidates**: Produce a ranked list of skill gap candidates with:
   - Domain/directory they cover
   - Frequency of manual work
   - Suggested skill name
   - Example tool-call sequences from the data

### Output
Write `analysis/cross-agent-audit-20260402/phase-b-skill-gaps.md` with findings.
Save intermediate data to `analysis/cross-agent-audit-20260402/phase-b-data/`.

### Commit
```
chore(analysis): Phase B — skill gap detection from session corpus (#1720)
```

---

Post a brief progress comment on GH issue #1720 when done:
```
Terminal 1 (Claude) complete:
- Phase A: cross-agent baseline at analysis/cross-agent-audit-20260402/phase-a-baseline.md
- Phase B: skill gap analysis at analysis/cross-agent-audit-20260402/phase-b-skill-gaps.md
- [N] skill gap candidates identified
- [N] files analyzed across [N] sessions
```
