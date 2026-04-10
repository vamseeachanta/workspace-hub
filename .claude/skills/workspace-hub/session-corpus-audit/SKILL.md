---
name: session-corpus-audit
description: Analyze orchestrator session JSONL logs across Claude/Hermes/Codex to produce cross-agent baselines, tool/file frequency analysis, and skill gap detection. Use when auditing agent activity patterns or identifying skill gaps from session data.
version: 1.0.0
author: Hermes Agent
metadata:
  hermes:
    tags: [analysis, session-logs, skill-gaps, cross-agent, frequency, orchestrator]
    related_skills: [claude-reflect, skill-eval, repo-architecture-analysis]
prerequisites:
  commands: [python3]
---

# Session Corpus Audit

Analyze orchestrator session JSONL logs across multiple AI agents to produce cross-agent baselines, tool/file frequency analysis, repeating workflow detection, and skill gap identification.

## When to Use

- Auditing agent activity patterns across Claude, Hermes, and Codex
- Identifying skill gaps from repeated manual workflows
- Producing tool/file frequency baselines for planning
- Assessing skill-to-work alignment (are hot skills actually being used?)
- Cross-agent comparison of work patterns

## Data Sources

### 1. Claude Orchestrator Logs
- Location: `logs/orchestrator/claude/session_*.jsonl`
- Format: `{"ts":"...","hook":"post","tool":"Bash","project":"...","repo":"...","cmd":"..."}`
- Tool field: Bash, Read, Edit, Write, Grep, Glob, Agent, Skill, WebFetch, Task
- `cmd` present for Bash, `file` present for Read/Edit/Write
- **IMPORTANT**: Filter `hook == "post"` only — each call has pre+post entries

### 2. Hermes Orchestrator Logs
- Location: `logs/orchestrator/hermes/session_*.jsonl`
- Format: `{"ts":"...","hook":"post","tool":"Bash","hermes_tool":"terminal","project":"...","cmd":"..."}`
- Has `hermes_tool` field with native names: terminal, read_file, search_files, write_file, patch, skill_view, skills_list, skill_manage
- Also has `model` field (e.g. "gpt-5.4", "claude-opus-4-6")
- **IMPORTANT**: Filter `hook == "post"` only

### 3. Codex Orchestrator Logs
- Location: `logs/orchestrator/codex/` — mixed formats
- `session_*.log`: Timestamped `[YYYY-MM-DDTHH:MM:SSZ] WRK-NNNN ...` entries
- `unknown-*.log`: Mostly code review verdicts (`### Verdict: APPROVE/MINOR/MAJOR`)
- **NOT structured JSONL** — parse as plain text, extract timestamps and verdicts
- Codex is primarily a review bot; exclude from file-frequency and command analyses

### 4. Skill Scores
- Location: `.claude/state/skill-scores.yaml`
- Structure: `skills:` key containing entries with `tier`, `calls_in_period`, `baseline_usage_rate`, `reference_count`, `path`
- **Tiers are: hot, warm, cold, dead** (NOT active/inactive)

## Phase A: Cross-Agent Baseline

### 7 Analyses to Produce

1. **Top 50 files by read frequency** — per agent and combined
2. **Top 50 files by write/edit frequency** — per agent and combined
3. **Top 20 bash commands** — per agent, normalized (strip paths/args, cluster similar)
4. **Tool call distribution** — per agent: {tool: count, pct}
5. **Temporal pattern** — tool calls per day per agent
6. **Repo distribution** — Claude uses `repo` field; Hermes infer from file/cmd paths
7. **Co-occurrence matrix** — which modules are always worked together in same session

### File Path Normalization
```python
def normalize_file_path(path):
    return path.replace('/mnt/local-analysis/workspace-hub/', '')
```

### Command Normalization Strategy
- Take first line, first command (before pipes/semicolons)
- Map common commands: cat/head/tail → `<cmd> <file>`, git → `git <subcommand>`
- Group grep/rg as `grep/search`

### Output
- `phase-a-baseline.md` — markdown report with all tables
- `phase-a-data/` — CSV/JSON intermediate files for downstream use

## Prompt-Focused Analysis Addendum

When the task is specifically about **Claude session prompts** rather than general session frequency, add this focused pass before Phase B.

### Prompt Inventory

From Claude JSONL logs, filter `hook == "post"` and `tool == "Read"`, then classify prompt-like paths into:
- `stage_prompt` — `.claude/work-queue/assets/<WRK>/stage-N-prompt.md`
- `planning_template` — `scripts/planning/prompts/*.md`
- `review_template` — `scripts/review/prompts/*.md`
- `plugin_prompt` — plugin cache prompt assets (for example subagent prompt files)
- `other_prompt_like` — other files with `prompt` in the path

Useful metrics:
1. Count prompt-like reads by class
2. Sessions containing prompt reads
3. Stage-number frequency (`stage-2`, `stage-4`, `stage-10`, etc.)
4. Top neighboring reads/commands within ±8 to ±12 post-hook records in the same session

### What prompt adjacency usually reveals

Prompt reads are most useful when interpreted together with nearby artifacts. Common supporting reads/calls to look for:
- work item markdown under `.claude/work-queue/working/` or `pending/`
- plan artifacts such as `plan.md` or `plan_claude.md`
- evidence files under `.claude/work-queue/assets/<WRK>/evidence/`
- checkpoint / routing yaml files
- stage exit / verification scripts such as `exit_stage.py`, `verify-gate-evidence.py`, `generate-html-review.py`
- skill reads under `.claude/skills/.../SKILL.md`

### Practical migration pattern discovered in historical Claude corpus

When the corpus shows very hot reads of paths that no longer exist in the current checkout, do NOT immediately recreate the deleted files. First classify each hot path into one of four buckets:
1. **Replaced by current docs/hooks/governance** — fix with a redirect/index document
2. **Replaced by a renamed live script** — update docs/examples to the new path
3. **Bootstrap-safe / intentionally minimal** — leave alone unless policy explicitly changes
4. **Historical noise only** — document and ignore

A high-leverage concrete output is a **legacy reference map** document that translates stale Claude-session paths to current repo surfaces. This is often better than compatibility shims because old workflow executables may have been intentionally removed.

For command-policy drift (for example `python3` vs `uv run ... python`), separate targets into:
- **active automation surfaces** — patch first
- **agent-facing docs/templates** — patch second because they propagate bad examples
- **bootstrap/setup scripts** — patch only if the repo explicitly wants to require the newer runtime tool there
- **tests/fixtures/evidence** — do not rewrite unless the purpose of the file is not historical/audit preservation

Interpretation pattern:
- prompt + evidence + exit script => prompts are acting as workflow contracts, not free-form instructions
- heavy Stage 2 / Stage 4 concentration => planning and resource-intelligence dominate the workflow
- cross-provider prompt templates (`claude-*`, `codex-*`, `gemini-*`) => model-role specialization is deliberate and should be preserved

### Reconstructing stage meaning when prompt files are gone

A recurring real-world issue: historical session logs often reference prompt packages or builders that are no longer present in the current checkout. When that happens:
- use tests mentioning `stage-N-prompt.md` to recover generation behavior
- use stage-evidence tests/fixtures to map stage numbers to stage names
- use docs that describe the repo workflow contract (`user_prompt -> YAML -> pseudocode -> TDD -> implementation`)

Do NOT assume missing prompt files mean the workflow was unimportant; often they were generated artifacts or existed in an earlier repo state.

### Ecosystem strengthening follow-through for Claude corpus audits

When the analysis shows many hot reads to deleted workflow files, treat this as a repo-ecosystem drift problem, not just a historical curiosity.

Common high-signal patterns:
- repeated reads of deleted `scripts/work-queue/*` files
- repeated reads of removed stage YAML contracts
- repeated reads of removed skill paths like legacy work-queue or session-start skills
- a substantial minority of Bash calls still using bare `python3` or `uv run ... python3`

Recommended remediation sequence:
1. **Build a legacy-reference map** — create a doc mapping hot deleted paths to current canonical workflow surfaces (for example `AGENTS.md`, `.planning/`, governance docs, hooks, `scripts/review/cross-review.sh`, queue refresh scripts).
2. **Patch misleading docs first** — if current docs still claim deleted helpers exist, fix those before adding shims.
3. **Prefer redirect/index docs over executable compatibility shims** for deleted stage/work-queue scripts unless there is evidence of a live integration still invoking them.
4. **Patch active automation surfaces before templates** for runtime drift. Highest priority is agent-facing launchers, hooks, dashboards, and shell wrappers; only then fix broader docs/templates.
5. **Separate active drift from intentional exceptions** — exclude Windows-specific prompts, drift-detection fixtures/tests, and historical evidence artifacts from `python3` cleanup.

A good concrete output from this follow-through is:
- one generated audit report (`docs/reports/...` + optional JSON)
- one legacy-path redirect map in docs
- a first patch wave on active shell automation replacing bare `python3` / `uv run ... python3` with `uv run ... python`

## Phase B: Skill Gap Detection

### 1. Multi-Step Workflow Extraction

Find sequences of >=5 consecutive post-hook tool calls that:
- Don't include a skill invocation (no `tool: Skill` or `hermes_tool: skill_view`)
- Touch related files (same directory or shared prefix >= 2 path components)
- Repeat across >= 2 sessions

**Algorithm**: Sliding window (size 5-15), extract directory from file/cmd fields, check relatedness, cluster by (tool_sequence, dir_prefix), filter to cross-session repeats, deduplicate overlapping windows keeping longest.

### 2. Skill Coverage Map

For each top directory from Phase A:
- Search all skill repos for matching skills by name, description, triggers, domains
- Score matches: name match (+3), description match (+1), domain overlap (+2), trigger match (+3)
- Flag directories with score < 2 as gaps

### 3. Skill-to-Work Alignment

From skill-scores.yaml:
- Which `tier: hot` skills are invoked in session logs? (look for skill file reads)
- Which `tier: dead` skills cover domains with active work?
- **Key finding pattern**: Most hot skills are NOT directly invoked — they work via auto-loading (AGENTS.md, hooks). Only explicit `tool:Read` of `/skills/` paths counts as invocation.

### 4. Gap Candidates (4 sources, ranked by priority score)

| Source | Priority Formula |
|--------|-----------------|
| Coverage gap | frequency from Phase A |
| Workflow pattern | occurrences × sessions_count |
| Dead skill resurrection | fixed score (5) |
| Discoverability gap | calls_in_period × 2 |

Deduplicate by domain prefix, sort descending.

### Output
- `phase-b-skill-gaps.md` — markdown report
- `phase-b-data/` — intermediate JSON files

## Skill Repo Scanning

When cataloging skills across repos, scan these locations:
```
.claude/skills/           (workspace-hub, exclude _archive/_internal/_runtime/_core/session-logs)
CAD-DEVELOPMENTS/.claude/skills/
worldenergydata/.claude/skills/
achantas-data/.claude/skills/
assetutilities/.claude/skills/
~/.hermes/skills/         (Hermes local skills)
```

Extract metadata from YAML frontmatter (name, description, triggers) and domain keywords from content body.

## Phase C: Dead Skill Audit

Classify all skills by tier, find unscored/orphaned/phantom skills, and detect cross-repo overlaps.

### Data Sources
- `skill-scores.yaml`: `.claude/state/skill-scores.yaml` — YAML with `skills:` key, each entry has `tier`, `path`
- Skill inventory: `find <repo>/.claude/skills/ -name "SKILL.md"` across all repos, excluding `_archive/_internal/_runtime/_core/session-logs`
- Git log for domain activity: `git log --since=<90d> --name-only`
- Hermes skills: `~/.hermes/skills/`

### Key Analyses

1. **Tier distribution** — `grep "tier:" skill-scores.yaml | sort | uniq -c`
2. **Phantom scores** — skills scored but living in excluded dirs (_internal/_core). Extract with:
   ```bash
   awk '/^  [a-zA-Z0-9]/ { name=$1; gsub(/:/, "", name) } /tier:/ { tier=$2 } /path:/ { print name "|" $2 "|" tier }' skill-scores.yaml
   ```
   Filter where path starts with `_internal/` or `_core/`. These inflate dead counts.
3. **Unscored skills** — `comm -23 <(all_repo_names | sort -u) <(scored_names | sort)` 
4. **Dead classification**: For each dead skill NOT in _internal/_core:
   - Check if skill dir exists on disk → if missing = orphaned
   - Check if domain had git activity in 90d → if no = truly-dead, if yes = dormant-but-needed
5. **Cross-repo overlaps** — `cut -d'|' -f2 all-repo-skills.csv | sort | uniq -d`
6. **Hermes collisions** — `comm -12 <(hermes_names) <(repo_names)`, then compare MD5 and line counts

### Pitfall: GSD Skills
41 GSD framework skills will always score dead — they're loaded by the GSD orchestrator, not via `skill_view()`. Either exclude `gsd-*` or add framework-aware tracking.

## Phase D: Correction Hotspot Analysis

Mine `.claude/state/corrections/*.jsonl` for quality improvement targets.

### Data Source
- Format: `{"timestamp":"...","file":"...","basename":"...","tool":"Edit|Write","correction_gap_seconds":N,"type":"correction"}`
- No `description` field exists — classify patterns from file paths/extensions only

### Key Analyses

1. **Top files** — `grep -oP '"file":"[^"]*"' *.jsonl | sort | uniq -c | sort -rn`
   - Normalize paths: strip `/mnt/github/workspace-hub/`, `/mnt/local-analysis/workspace-hub/`, `/mnt/workspace-hub/`
2. **Top modules** — group normalized paths by parent directory (`rev | cut -d/ -f2- | rev`)
3. **File extension distribution** — `basename | sed 's/.*\.//'`
4. **Tool type distribution** — `grep -oP '"tool":"[^"]*"'`
5. **Temporal trend** — corrections per file per day, aggregate by half-month
6. **Test coverage gaps** — for each top Python hotspot, derive test path:
   - `src/pkg/module.py` → `tests/pkg/test_module.py`
   - `scripts/dir/script.py` → `scripts/dir/tests/test_script.py`
   - Check `test -f` for each
7. **Cross-agent overlap** — compare file sets between Claude corrections and Hermes logs (note: Hermes currently lacks correction tracking)

### Pitfall: Hermes Has No Correction Tracking
Hermes orchestrator logs record tool invocations but NOT file-level corrections. Cross-agent comparison requires implementing Hermes correction hooks first.

## Phase F: Memory Deduplication

Compare knowledge stored across all agent memory systems.

### Data Sources
- Hermes: `~/.hermes/memories/MEMORY.md` and `USER.md` (§-separated entries)
- Claude: `~/.claude/projects/-mnt-local-analysis-workspace-hub/memory/MEMORY.md` (structured with sections + linked .md files)
- Claude state: `.claude/state/cc-user-insights.yaml`, `.claude/state/learned-patterns.json`
- Codex: `~/.codex/rules/default.rules` (prefix_rule patterns), `~/.codex/config.toml`
- AGENTS.md: `find <workspace> -maxdepth 2 -name AGENTS.md`
- CLAUDE.md: `find <workspace> -maxdepth 2 -name CLAUDE.md`

### Key Analyses

1. **Hermes memory inventory** — parse §-separated entries, categorize: environment_fact, convention, project_knowledge, tool_quirk, user_preference, user_identity
2. **Cross-agent fact overlap** — identify facts stated in >=2 stores. Check consistency.
3. **AGENTS.md audit** — classify each as:
   - Pointer (9 lines, references `../AGENTS.md`)
   - Adapted (11-50 lines, YAML frontmatter + pointer)
   - Standalone (50+ lines, independent content)
4. **CLAUDE.md merge conflict scan** — CRITICAL:
   ```bash
   for f in $(find . -maxdepth 2 -name CLAUDE.md); do
     grep -c "^<<<<<<< " "$f" && echo "CONFLICT: $f"
   done
   ```
   In practice, ~25% of repos had unresolved merge conflicts inflating CLAUDE.md from 8 lines to 740+ lines. Agents get garbled instructions.
5. **Promotion candidates** — facts in agent-private memory that should move to shared config (AGENTS.md, user-profile.yaml, harness-config.yaml)

### Pitfall: CLAUDE.md Untracked in Workspace-Hub Git
Subrepo CLAUDE.md files are NOT tracked in workspace-hub git — they live in their respective repo git trees. Can't use `git log` from workspace-hub root to check modification dates.

## Pitfalls

1. **Double-counting**: Always filter `hook == "post"` — every tool call generates both pre and post entries
2. **Codex format mismatch**: Codex logs are NOT JSONL. Plain text with timestamps and review verdicts. Parse accordingly.
3. **skill-scores.yaml structure**: Skills nested under `skills:` key, not top-level. Tiers are hot/warm/cold/dead.
4. **Skill invocation detection**: Most skills are auto-loaded, not explicitly read. Low invocation counts don't mean low usage — it means the auto-loading works.
5. **Path normalization**: Strip `/mnt/local-analysis/workspace-hub/` prefix for clean display
6. **Workflow window overlap**: Sliding windows produce massive candidate counts (82K+). Deduplicate by (tool_sequence, dir_prefix) and keep longest patterns.
7. **Git push with unstaged changes**: `git pull --rebase` fails with unstaged changes. Commit first, then push. If remote rejects, stash → pull rebase → stash pop.
8. **Historical-log metrics do NOT improve just because you patched the repo**: a refreshed audit over the same Claude session corpus will usually show the same missing-path counts and python3 counts, because those metrics are properties of historical logs. Use the audit to identify current remediation targets, then search the live repo for still-active references to those missing paths.
9. **Best remediation for hot missing paths is often a compatibility redirect, not file resurrection**: when a legacy path is still referenced by current entrypoints, add a thin stub/wrapper that fails clearly or redirects to canonical docs/workflows. This reduces future agent confusion without reviving obsolete workflow semantics.

9. **Git push with unstaged changes**: `git pull --rebase` fails with unstaged changes. Commit first, then push. If remote rejects, stash → pull rebase → stash pop.

## Phase E: Agent Routing Intelligence

Analyze per-agent domain affinity, tool profiles, task complexity, and cross-review patterns to produce routing recommendations.

### Data Collection Pattern
Write separate `/tmp/phase_e_*.py` scripts (one per agent) rather than inline python — JSONL parsing of 150K+ records times out with inline `uv run python3 -c "..."`. Always use `uv run python /tmp/script.py` from the workspace dir.

### Claude Analysis (session_*.jsonl)
- Filter `hook == "post"` only
- Extract: tool distribution, repo field, file paths (normalize to top-level dir)
- Classify sessions by read/write/exec/delegation percentages
- R/W ratio reveals agent posture: >1.5 = research-heavy, <1.0 = implementation-heavy

### Hermes Analysis (session_*.jsonl)
- Same post-hook filter, but also has `hermes_tool` and `model` fields
- Track skill engagement: skill_view + skill_manage + skills_list per session
- Hermes uses skills ~18x more intensively per session than Claude

### Codex/Gemini Analysis (WRK-*.log + unknown-*.log)
- WRK files: JSON with `verdict`, `issues_found[]`, `suggestions[]`
- unknown-*.log: Also review verdicts (same JSON format), NOT session logs
- Verdict strings are NOT standardized — 7+ variants observed (APPROVE, REVISE, REVISION NEEDED, changes-requested, Request changes, REQUEST_CHANGES, changes_requested)
- Gemini logs often have no structured `issues_found` — simpler review format
- Cross-review agreement: find shared WRK numbers between codex/ and gemini/ dirs

### Routing Recommendation Table
Compare observed agent behavior against `config/agents/routing-config.yaml` and `config/agents/provider-capabilities.yaml`. Flag:
- Capabilities claimed but NOT observed in logs
- Agents active in logs but MISSING from config (e.g., Hermes)
- Tier assignments that don't match actual usage

## Phase G: Per-Repo Ecosystem Audit

Scan all repos with `.claude/` directories for ecosystem health.

### Scan Script Pattern
Write `/tmp/phase_g_scan.py` that outputs JSON array with per-repo:
- skills_count, commands_count, docs_count (from .claude/ subdirs)
- memory/state/rules/work_queue existence and counts
- AGENTS.md: exists, lines, is_pointer, has_entry_points, has_test_command, has_depends_on
- CLAUDE.md: exists, lines, last_modified, references_wrk, has_repo_overrides
- git_activity_90d: `git log --since=<date> --oneline | wc -l`
- tier from `scripts/readiness/harness-config.yaml`

### Critical Check: Merge Conflicts in CLAUDE.md
```bash
for repo in */CLAUDE.md; do
    if grep -q '<<<<<<' "$repo" 2>/dev/null; then
        echo "MERGE CONFLICT: $repo"
    fi
done
```
This was a major discovery — 25% of repos had unresolved merge conflicts inflating CLAUDE.md from 9-15 lines to 740+ lines. Agents get malformed instructions.

### Command Staleness Detection
For each command file, regex-extract file paths (`scripts/`, `docs/`, `tests/`, `config/` prefixes) and check `os.path.exists()`. Flag missing references as stale.

### Skill Promotion Analysis
Compare skills in nested repos (CAD-DEVELOPMENTS, worldenergydata, achantas-data) against workspace-hub. Flag:
- Domain-critical skills absent from workspace-hub → PROMOTE
- 100% duplicate skill sets → DEDUPLICATE (use external_dirs or remove)
- Skills that appear in both but may have drifted → CHECK SYNC

### Repos Needing Attention Heuristics
- High git activity (>50 commits) + 0 skills = under-served
- Many skills + 0 git activity = over-invested/stale
- Tier-1 missing any ecosystem component = contract gap
- Standalone AGENTS.md claiming test_command but tests/ has 0 files = broken contract

## Pitfalls

7. **Git push with unstaged changes**: `git pull --rebase` fails with unstaged changes. Use: `git stash && git pull origin main --rebase && git stash pop && git push origin main`
8. **Inline python timeout**: Large JSONL parsing (>50K records) times out at 60s when run via `uv run python3 -c "..."`. Always write to `/tmp/script.py` and run with `uv run python /tmp/script.py` with `timeout=120`.
9. **Codex "other" files**: The 321 `unknown-*.log` files in codex/ are NOT junk — they're review verdicts in JSON format, same as WRK files. Include them in analysis.
10. **Parallel terminal sessions dirty worktree**: When running as Terminal 3 in an overnight batch, other terminals may create untracked files. Always stash before pull-rebase.
11. **gh issue create with nonexistent labels**: `gh issue create --label "chore,skills"` will FAIL SILENTLY (no issue created) if those labels don't exist on the repo. Always create issues WITHOUT labels first, then add labels separately if needed: `gh issue create --title "..." --body "..."`.
12. **CLAUDE.md merge conflicts**: Check ALL subrepo CLAUDE.md files for `<<<<<<<` markers. This is a recurring problem — auto-sync scripts create conflicts that go unresolved because the files are gitignored in workspace-hub.

## Lightweight Claude-Only Drift Audit

When the task is specifically: "review Claude work session logs and strengthen the repo ecosystem," a full multi-phase corpus audit may be overkill. Use the lightweight path first:

1. Run a focused Claude-only audit against `logs/orchestrator/claude/session_*.jsonl`
2. Compare `tool == Read` file paths against the current checkout
3. Split missing reads into:
   - repo-local missing paths (deleted/renamed scripts, skills, work-queue assets)
   - external missing paths (`/tmp`, other mount points, plugin cache)
4. Count prompt-like reads and missing stage-prompt assets
5. Count Bash calls using bare `python3` vs `uv run ... python`
6. Build a stage-prompt package index by work item from `.claude/work-queue/assets/<WRK>/` that records:
   - stages referenced in historical logs
   - prompt file paths and whether they still exist
   - associated evidence files under `evidence/`
7. Emit both machine-readable JSON and a markdown report

Reference implementation added in this repo:
- `scripts/analysis/claude_session_ecosystem_audit.py`
- test: `tests/analysis/test_claude_session_ecosystem_audit.py`

Recommended command:

```bash
uv run python scripts/analysis/claude_session_ecosystem_audit.py \
  --output-md docs/reports/claude-session-ecosystem-audit-$(date +%F).md \
  --output-json analysis/claude-session-ecosystem-audit-$(date +%F).json
```

What this lightweight audit is good at surfacing:
- hot legacy references after repo refactors (for example `scripts/work-queue/*` paths that no longer exist)
- missing prompt/stage assets that were important in historical Claude workflow
- which specific WRK/workspace-hub prompt packages have surviving evidence artifacts but missing prompt files
- policy drift where Claude Bash calls still use bare `python3`

Additional practical follow-through learned from implementation:
- add the stage-prompt package index directly into the markdown report, not only JSON, so humans can triage missing prompt assets quickly
- do not assume state artifacts are machine-local just because they live under `.claude/state/`; verify `.gitignore` and tracked-file status first. In this repo, `.claude/state/portfolio-signals.yaml` is intentionally tracked shared state and tests should assert tracked+not-ignored behavior rather than the opposite.

Use this lightweight pass before the full Phase A/B/C/F/G process when the user wants fast ecosystem-strengthening recommendations rather than the full cross-agent program.

## Commit Convention

```
chore(analysis): Phase A — cross-agent tool/file frequency baseline (#ISSUE)
chore(analysis): Phase B — skill gap detection from session corpus (#ISSUE)
chore(analysis): Phase E — agent routing intelligence from session corpus (#ISSUE)
chore(analysis): Phase C — dead skill audit across N skills (#ISSUE)
chore(analysis): Phase D — correction hotspot analysis from N corrections (#ISSUE)
chore(analysis): Phase E — agent routing intelligence from session corpus (#ISSUE)
chore(analysis): Phase F — memory dedup + AGENTS.md audit across N repos (#ISSUE)
chore(analysis): Phase G — per-repo ecosystem audit across N repos (#ISSUE)
```
