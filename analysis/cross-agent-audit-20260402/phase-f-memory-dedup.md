# Phase F — Memory Deduplication & AGENTS.md Audit

**Generated**: 2026-04-02 | **Issue**: #1720 | **Agent**: Hermes (Terminal 2)

---

## 1. Per-Agent Memory Inventory

### Hermes (~/.hermes/memories/)

**MEMORY.md** — 8 entries (§-separated):

| # | Category | Summary |
|---|----------|---------|
| 1 | project_knowledge | AI provider usage order: Claude > OpenAI > Gemini |
| 2 | environment_fact | ace-linux-1 workspace path, sparse overlay warning |
| 3 | convention | `uv run` always — user-corrected |
| 4 | project_knowledge | aceengineer-strategy/ GTM repo, $120K retainer model |
| 5 | convention | Hermes ecosystem integration (#1712,#1719), external_dirs, nightly cron |
| 6 | project_knowledge | OrcaWave/OrcaFlex ecosystem details (DiffractionSpec, solver queue, features) |
| 7 | project_knowledge | Data pipeline: malformed catalog.yaml, safe_yaml_load() pattern, unified registry |
| 8 | project_knowledge | digitalmodel/ is separate nested git repo |

**USER.md** — 6 entries:

| # | Category | Summary |
|---|----------|---------|
| 1 | user_preference | Maximize weekly AI subscription usage |
| 2 | user_identity | Subscriptions: Claude Max $200, 2× Codex $20, Gemini $19.99 |
| 3 | user_preference | Adversarial cross-review by ALL agents |
| 4 | user_preference | Overnight batch execution — 3 terminal prompts, zero git contention |
| 5 | user_preference | Adversarial review at BOTH plan + code stages |
| 6 | user_identity | Vamsee, ACE Engineer, P.E., 23yr exp, OrcaFlex/mooring/FEA/API 579 |

### Claude (~/.claude/projects/-mnt-local-analysis-workspace-hub/)

**MEMORY.md** — structured with sections:
- **User Preferences & Feedback** (11 tagged entries + 4 bullet items)
  - Referenced via linked .md files (feedback_*.md, working-style.md, shell-git-patterns.md)
  - Key: no local task IDs, check parallel work, comment on issues, queue git-tracked files
- **Project Context** (9 entries)
  - GSD migration, cross-review policy, mooring knowledge, nightly researchers, AI harness evals, Hermes installation, workflow tips, solver queue, overnight batch runs
- **User Tips** (1 entry) — voice prompt curation
- **References** (2 entries) — achantas-data repo, Google CLI paid account

**cc-user-insights.yaml** — Claude Code release notes insights (versions 2.1.20–2.1.39)
- 8 general insights (Opus 4.6 launch, Agent Teams, auto memory, fast mode, etc.)
- 11 specific insights (subagent MCP fix, task metrics, memory frontmatter, etc.)

**learned-patterns.json** — Mostly empty pattern entries from session 4dcdc762 (Feb 24)

### Codex (~/.codex/)

**config.toml**:
- Model: gpt-5.4
- Reasoning effort: medium
- Workspace trust: `/mnt/local-analysis/workspace-hub` = trusted
- Status line: model, project, branch, context %, limits

**rules/default.rules**:
- 12+ prefix_rule patterns — all permitting specific `uv run` commands
- Encodes work-queue scripts, test commands, cross-review scripts
- No general knowledge — purely permission rules

## 2. Cross-Agent Fact Overlap Matrix

| Fact | Hermes | Claude | Codex | AGENTS.md | Consistent? |
|------|:------:|:------:|:-----:|:---------:|:-----------:|
| `uv run` convention | ✅ MEM | ✅ AGENTS | ✅ rules | ✅ | ✅ Yes |
| Workspace path | ✅ MEM | implicit | ✅ config | — | ✅ Yes |
| Cross-review policy | ✅ USER | ✅ MEM+AGENTS | — | ✅ | ⚠️ Partial |
| User identity (Vamsee/ACE) | ✅ USER | ✅ project files | — | — | ✅ Yes |
| Overnight batch pattern | ✅ USER | ✅ project file | — | — | ✅ Yes |
| digitalmodel/ nested repo | ✅ MEM | — | — | ✅ sub-AGENTS | ✅ Yes |
| AI subscriptions | ✅ USER | — | — | — | N/A (Hermes only) |

### Contradiction Flags

**1 partial contradiction identified:**

> **Cross-review policy**: Hermes USER says "adversarial cross-review by ALL available agents" (emphasis on all, always). Claude AGENTS.md says "Claude orchestrates, Codex reviews, Gemini on triggers only." The Hermes version is stricter — it requires all three agents review everything. The AGENTS.md version is selective (Gemini only on triggers).

**Resolution recommendation**: The AGENTS.md version is the authoritative ecosystem policy. Hermes USER.md should be softened to match, or AGENTS.md should be strengthened if the user actually wants all-agent review always.

## 3. AGENTS.md Freshness Audit (23 repos)

| Repo | AGENTS.md Lines | Type | Freshness |
|------|---------------:|------|-----------|
| **workspace-hub (root)** | 18 | Canonical | ✅ Current |
| aceengineer-admin | 9 | Pointer | ✅ v1.0.0 |
| aceengineer-website | 9 | Pointer | ✅ v1.0.0 |
| achantas-data | 9 | Pointer | ✅ v1.0.0 |
| achantas-media | 9 | Pointer | ✅ v1.0.0 |
| acma-projects | 9 | Pointer | ✅ v1.0.0 |
| assethold | 11 | Adapted (frontmatter) | ✅ v1.0.0 |
| assetutilities | 11 | Adapted (frontmatter) | ✅ v1.0.0 |
| client_projects | 9 | Pointer | ✅ v1.0.0 |
| digitalmodel | 11 | Adapted (frontmatter) | ✅ v1.0.0 |
| doris | 9 | Pointer | ✅ v1.0.0 |
| frontierdeepwater | 9 | Pointer | ✅ v1.0.0 |
| hobbies | 9 | Pointer | ✅ v1.0.0 |
| investments | 9 | Pointer | ✅ v1.0.0 |
| OGManufacturing | 11 | Adapted (frontmatter) | ✅ v1.0.0 |
| rock-oil-field | 9 | Pointer | ✅ v1.0.0 |
| sabithaandkrishnaestates | 9 | Pointer | ✅ v1.0.0 |
| saipem | 9 | Pointer | ✅ v1.0.0 |
| sd-work | 9 | Pointer | ✅ v1.0.0 |
| seanation | 9 | Pointer | ✅ v1.0.0 |
| simpledigitalmarketing | 9 | Pointer | ✅ v1.0.0 |
| teamresumes | 9 | Pointer | ✅ v1.0.0 |
| worldenergydata | 12 | Adapted (frontmatter) | ✅ v1.0.0 |

**Note**: CAD-DEVELOPMENTS has no AGENTS.md (only CLAUDE.md).

AGENTS.md ecosystem is well-maintained. All 22 subrepos either point to canonical or add repo-specific frontmatter. No stale content detected.

## 4. CLAUDE.md Freshness Audit (24 repos)

| Repo | Lines | Type | Issue |
|------|------:|------|-------|
| workspace-hub (root) | 7 | Canonical | ✅ OK (tracked in git) |
| CAD-DEVELOPMENTS | 98 | Standalone | ⚠️ Untracked in workspace-hub git |
| aceengineer-admin | 8 | Pointer | ✅ OK |
| aceengineer-website | 8 | Pointer | ✅ OK |
| achantas-data | 43 | Adapted | ❌ **MERGE CONFLICT** |
| achantas-media | 8 | Pointer | ✅ OK |
| acma-projects | 8 | Pointer | ✅ OK |
| **assethold** | **745** | **Standalone** | **❌ MERGE CONFLICT** |
| assetutilities | 14 | Adapted | ✅ OK |
| client_projects | 8 | Pointer | ✅ OK |
| digitalmodel | 14 | Adapted | ✅ OK |
| doris | 8 | Pointer | ✅ OK |
| frontierdeepwater | 8 | Pointer | ✅ OK |
| **hobbies** | **751** | **Standalone** | **❌ MERGE CONFLICT** |
| **investments** | **739** | **Standalone** | **❌ MERGE CONFLICT** |
| OGManufacturing | 8 | Pointer | ✅ OK |
| rock-oil-field | 31 | Adapted | ⚠️ Untracked |
| **sabithaandkrishnaestates** | **739** | **Standalone** | **❌ MERGE CONFLICT** |
| saipem | 8 | Pointer | ✅ OK |
| sd-work | 8 | Pointer | ✅ OK |
| seanation | 8 | Pointer | ✅ OK |
| simpledigitalmarketing | 31 | Adapted | ⚠️ Untracked |
| **teamresumes** | **739** | **Standalone** | **❌ MERGE CONFLICT** |
| worldenergydata | 18 | Adapted | ✅ OK |

### Critical Finding: 6 CLAUDE.md files have unresolved merge conflicts

The 739-751 line CLAUDE.md files in assethold, hobbies, investments, sabithaandkrishnaestates, teamresumes, and achantas-data all contain `<<<<<<< Updated upstream` / `=======` / `>>>>>>>` markers. These are broken and Claude Code will parse them incorrectly.

All CLAUDE.md files (except root) are untracked in workspace-hub git — they exist in their respective subrepo git trees.

## 5. Promotion Candidates

Facts that should move from agent-private memory to shared ecosystem config:

| Fact | Current Location | Proposed Destination | Priority |
|------|-----------------|---------------------|----------|
| `uv run` convention | Hermes MEM + Claude AGENTS + Codex rules | ✅ Already in AGENTS.md | Done |
| User identity (Vamsee/ACE) | Hermes USER + Claude project files | New: `config/user-profile.yaml` | Medium |
| AI subscriptions | Hermes USER only | New: `config/user-profile.yaml` | Medium |
| Overnight batch pattern | Hermes USER + Claude project file | New: `docs/workflows/overnight-batch.md` | Low |
| Cross-review policy | Hermes USER (strict) + AGENTS.md (selective) | Reconcile in AGENTS.md | High |
| Workspace path | Hermes MEM + Codex config | Already in harness-config.yaml | Done |
| digitalmodel/ nested repo | Hermes MEM + digitalmodel/AGENTS.md | Already in AGENTS.md frontmatter | Done |

## 6. Summary & Recommendations

### Immediate actions (fix broken state)
1. **Resolve 6 CLAUDE.md merge conflicts** — assethold, hobbies, investments, sabithaandkrishnaestates, teamresumes, achantas-data. These actively confuse Claude Code.
2. **Reconcile cross-review policy contradiction** — align Hermes USER.md with AGENTS.md routing policy, or update AGENTS.md to match the stricter "all agents" requirement.

### Medium-term improvements
3. **Create shared user profile** — `config/user-profile.yaml` with user identity, subscriptions, preferences. Eliminates need for each agent to store user identity separately.
4. **Add CAD-DEVELOPMENTS AGENTS.md** — only repo with CLAUDE.md but no AGENTS.md.
5. **Clean up Claude learned-patterns.json** — contains only empty pattern entries from Feb 24. Provides no value.
6. **Prune Codex rules** — 12+ highly-specific prefix_rule entries for individual scripts. Consider switching to broader `trusted` project trust instead.

### Memory efficiency stats
| Agent | Memory Store | Entries | Estimated chars | Efficiency |
|-------|-------------|--------:|----------------:|------------|
| Hermes | MEMORY.md | 8 | ~2,100 | Good — compact, actionable |
| Hermes | USER.md | 6 | ~1,178 | Good — focused on preferences |
| Claude | MEMORY.md | ~27 | ~3,500+ | Medium — uses linked files (adds latency) |
| Claude | cc-user-insights.yaml | 19 | ~2,000 | Low — release notes not operationally useful |
| Claude | learned-patterns.json | 3 | ~500 | Very low — empty patterns, should be pruned |
| Codex | rules + config | 14 | ~2,500 | Low — over-specific rules |

### Cross-agent overlap summary
- **7 facts** appear in ≥2 agent stores
- **1 partial contradiction** (cross-review policy strictness)
- **0 hard contradictions** (all overlapping facts are consistent)
- **3 facts** already properly shared via AGENTS.md
- **2 facts** are candidates for a new shared user profile
- **2 facts** could move to shared workflow docs
