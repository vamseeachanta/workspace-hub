# Phase C — Dead Skill Audit

**Generated**: 2026-04-02 | **Issue**: #1720 | **Agent**: Hermes (Terminal 2)

---

## 1. Tier Distribution (skill-scores.yaml)

| Tier | Count | % of Scored |
|------|------:|------------:|
| dead | 303   | 55.4%       |
| hot  | 120   | 21.9%       |
| warm | 74    | 13.5%       |
| cold | 50    | 9.1%        |
| **Total** | **547** | **100%** |

> Over half (55.4%) of scored skills are classified as dead (zero usage, zero references).

## 2. Active Skill Inventory (on-disk, excluding _archive/_internal/_runtime/_core/session-logs)

| Repository | Active Skills |
|------------|-------------:|
| .claude/skills/ (workspace-hub root) | 387 |
| CAD-DEVELOPMENTS/.claude/skills/ | 182 |
| worldenergydata/.claude/skills/ | 20 |
| achantas-data/.claude/skills/ | 13 |
| assetutilities/.claude/skills/ | 3 |
| **Subtotal (5 repos)** | **605** |
| ~/.hermes/skills/ (Hermes) | 86 |
| **Grand total** | **691** |

### Unique skill names across repos: 457

## 3. Unscored Skills

**76 skills** exist on disk but have no entry in skill-scores.yaml.

These are either:
- Skills in non-root repos (CAD-DEVELOPMENTS, worldenergydata, achantas-data, assetutilities) not covered by the scoring pipeline
- Newly created skills added after the last scoring run (2026-04-02)

Full list at: `phase-c-data/unscored-skills.txt`

## 4. Phantom Scored Skills (scored but not in active inventory)

**166 skills** have scores but exist only in excluded directories:
- 118 from `_internal/` (auto-generated meta-skills)
- 48 from `_core/` (bash utility fragments)

These are numbered sub-skills (e.g., `1-always-use-set-e`, `3-json-report-generation`) created by internal skill builders. All scored as dead — correctly so, as they are not user-facing.

**Recommendation**: Remove these 166 phantom entries from skill-scores.yaml to reduce noise. They inflate the dead count artificially.

## 5. Dead Skill Classification (303 total)

### Breakdown by category

| Category | Count | Description |
|----------|------:|-------------|
| Internal fragments (_internal/) | 101 | Auto-generated meta-skills |
| Core fragments (_core/) | 45 | Bash utility sub-skills |
| GSD workflow skills | 41 | GSD framework commands |
| Regular domain skills | 116 | Standard user-facing skills |
| **Total** | **303** | |

### Regular dead skills (116) — deep classification

All 116 regular dead skills:
- **Exist on disk** (not orphaned)
- **Belong to active domains** (domain had git activity in last 90 days)

Classification:
| Sub-class | Count | Description |
|-----------|------:|-------------|
| dormant-but-needed | 116 | Skill exists, domain active, but zero usage recorded |
| truly-dead | 0 | No inactive domains found |
| orphaned | 0 | All skills have valid disk paths |

### GSD dead skills (41)

All 41 GSD skills are scored dead because `skill-scores.yaml` uses `calls_in_period` and `reference_count` metrics that don't capture GSD framework usage (GSD skills are loaded by the GSD orchestrator, not by direct `skill_view()` calls).

**Recommendation**: Either exclude GSD skills from scoring or add a GSD-aware usage tracker.

### Top dormant-but-needed skills (selected from 116)

These exist in active domains but show zero usage — likely candidates for trigger improvements:

| Skill | Domain | Likely Issue |
|-------|--------|-------------|
| code-review | development/github | Overlaps with code-reviewer, github-code-review |
| dspy | ai/prompting | Name collision with mlops/research/dspy |
| communication | business/communication | Overly generic name |
| d3js, chartjs, echarts | data/visualization | Overshadowed by plotly-visualization |
| blender, cad-engineering | engineering/cad | Niche use, rarely triggered |
| batch-manager | engineering/marine-offshore/orcaflex | Functionality overlaps with orcaflex skill |

## 6. Cross-Repo Skill Overlap

**134 skills** share names across multiple repositories.

### By repo pair

| Repo Pair | Duplicate Count |
|-----------|---------------:|
| CAD-DEVELOPMENTS ↔ workspace-hub | 116 |
| workspace-hub ↔ worldenergydata | 13 |
| achantas-data ↔ CAD-DEVELOPMENTS ↔ workspace-hub ↔ worldenergydata | 3 |
| assetutilities ↔ workspace-hub | 2 |
| **Total** | **134** |

The 116 CAD-DEVELOPMENTS ↔ workspace-hub overlaps are likely from bulk skill sync operations. Most are identical copies.

### Same-repo name collisions (different paths, same name)

| Repo | Skill Name | Occurrence |
|------|-----------|:---------:|
| CAD-DEVELOPMENTS | auto-sync-batch-update-2026-01 | 2 paths |
| CAD-DEVELOPMENTS | refactor-migrate-claude-md-to- | 2 paths |
| workspace-hub | analysis | 2 paths |
| workspace-hub | competitive-analysis | 2 paths |
| workspace-hub | naval-architecture | 2 paths |
| workspace-hub | pyproject-toml | 2 paths |
| workspace-hub | sync | 2 paths |
| workspace-hub | uv-package-manager | 2 paths |

**Recommendation**: Resolve same-repo collisions — when two skills share a name in the same repo, the skill loader may pick the wrong one.

## 7. Hermes vs Workspace-Hub Overlap

**6 skills** share names between `~/.hermes/skills/` and workspace-hub `.claude/skills/`:

| Skill | Hermes Lines | Repo Lines | MD5 Match | Verdict |
|-------|------------:|----------:|-----------:|---------|
| code-review | 81 | 64 | ❌ Different | Hermes version longer, likely more detailed |
| dspy | 593 | 123 | ❌ Different | Hermes version 4.8× larger (comprehensive) |
| github-code-review | 480 | — | N/A | Hermes-only (no active repo version found) |
| obsidian | 66 | 158 | ❌ Different | Repo version 2.4× larger |
| systematic-debugging | 366 | 175 | ❌ Different | Hermes version 2.1× larger |
| writing-plans | 296 | 185 | ❌ Different | Hermes version 1.6× larger |

All 5 overlapping skills have **divergent content** (different MD5 hashes, different sizes). This creates confusion when both agents work in workspace-hub — they may follow different procedures for the same task.

**Recommendation**: For each collision, compare content and keep the better version in both locations, or designate one as canonical (e.g., Hermes skills are canonical for Hermes, .claude/skills for Claude).

## 8. Summary & Recommendations

### Immediate actions
1. **Remove 166 phantom scores** (_internal/ + _core/) from skill-scores.yaml — reduces dead count from 303 to 137
2. **Resolve 8 same-repo name collisions** — prevents skill loader ambiguity
3. **Merge 5 divergent Hermes↔repo skill pairs** — pick best version for each

### Medium-term improvements
4. **Add GSD-aware usage tracking** — 41 GSD skills shouldn't be scored dead
5. **Consolidate 116 CAD-DEVELOPMENTS duplicates** — verify which are stale copies, archive redundant ones
6. **Improve triggers for 116 dormant-but-needed skills** — especially visualization skills (d3js, chartjs, echarts) and engineering niche skills
7. **Run skill-scores.yaml against all 5 repos** — currently only covers workspace-hub root (missing 76 unscored skills from other repos)

### Adjusted tier distribution (after removing phantoms)

| Tier | Count | % |
|------|------:|--:|
| dead (real) | 137 | 35.9% |
| hot | 120 | 31.5% |
| warm | 74 | 19.4% |
| cold | 50 | 13.1% |
| **Total** | **381** | **100%** |

With phantoms removed, the dead ratio drops from 55.4% to 35.9% — still high but more actionable.
