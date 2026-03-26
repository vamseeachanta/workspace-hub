# WRK-1272: Enforce 200-line Skill Limit

## Context

`coding-style.md` hard limit changed from 400→200 lines. 293 of 408 SKILL.md files (72%) now violate the limit. WRK-1263 proved the nested sub-skill pattern (aqwa-analysis: 718→5 files, all <200 lines). Infrastructure is mature: `eval-skills.py` detects violations, `new-feature.sh` scaffolds children.

## Strategy

**Scripts over LLM judgment.** Create `split-oversized-skill.py` that detects H2/H3 section boundaries and mechanically splits skills into hub + sub-skill directories. Children run the script on tier batches.

## Scripts to Create

| Script | Inputs | Outputs | Created by |
|--------|--------|---------|------------|
| `scripts/skills/split-oversized-skill.py` | SKILL.md path or `--batch` | Hub SKILL.md + sub-skill dirs | child-a |
| `scripts/skills/find-oversized-skills.py` | `--min-lines N` | Sorted list with line counts, categories | child-a |

### Split Script Behavior

- **Hub retains**: frontmatter (+ `see_also:`), When to Use, Prerequisites, condensed API table, Related Skills
- **Sub-skills created for**: Core Capabilities (by H3 groups), Integration Examples, Best Practices, Troubleshooting
- **Modes**: `--dry-run` (preview), `--trim` (Tier 4: extract appendix only), `--batch` (bulk)
- **Sub-skill frontmatter**: inherits category, adds `type: reference`
- **Flags** any single H3 section >200 lines for manual review

## Decomposition

| Child key | Title | Scope (one sentence) | Depends on | Agent | wrk_ref |
|-----------|-------|----------------------|------------|-------|---------|
| child-a | Build skill-split tooling | Create split-oversized-skill.py and find-oversized-skills.py with TDD (8+ tests) | — | claude | |
| child-b | Adopt eval-skills.py limit update | Link existing WRK-1273 as child | — | claude | WRK-1273 |
| child-c | Split Tier 1+2 skills (67 files over 800 lines) | Run split script on all 67 skills over 800 lines and verify all hubs and sub-skills under 200 lines | child-a | claude | |
| child-d | Split Tier 3 batch 1 — engineering, science, core, internal (55 files) | Run split script on 401-800 line skills in engineering, science, _core, _internal categories | child-a | claude | |
| child-e | Split Tier 3 batch 2 — data, business, dev, ops, coord, hub, ai (70 files) | Run split script on 401-800 line skills in remaining categories | child-a | claude | |
| child-f | Trim Tier 4 skills (101 files, 201-400 lines) | Run split script in trim mode to extract appendix sections from marginally-oversized skills | child-a | claude | |
| child-g | Final verification and cleanup | Run eval-skills.py full scan confirming 0 violations and fix any stragglers | child-c, child-d, child-e, child-f | claude | |

### Child: child-a

**Files/skills needed (entry_reads):**
- `.claude/skills/engineering/marine-offshore/aqwa/SKILL.md` (hub pattern reference)
- `.claude/skills/development/skill-eval/scripts/eval-skills.py` (validation reference)
- `.claude/rules/coding-style.md` (200-line rule)

**Acceptance Criteria:**
- [ ] `find-oversized-skills.py` lists all skills >N lines with count and category
- [ ] `split-oversized-skill.py` splits a 1200+ line fixture into hub <200 lines + sub-skills <200 lines
- [ ] `--dry-run` mode previews without writing
- [ ] `--trim` mode extracts only appendix sections
- [ ] `--batch` mode processes all skills in a category above threshold
- [ ] 8+ TDD tests pass against fixture skills

### Child: child-b

**Files/skills needed (entry_reads):**
- `.claude/work-queue/pending/WRK-1273.md`

**Acceptance Criteria:**
- [ ] WRK-1273 adopted with `parent: WRK-1272`

### Child: child-c

**Files/skills needed (entry_reads):**
- `scripts/skills/split-oversized-skill.py`
- `scripts/skills/find-oversized-skills.py`

**Acceptance Criteria:**
- [ ] All 67 skills over 800 lines split into hub + sub-skills
- [ ] Every hub SKILL.md under 200 lines
- [ ] Every sub-skill SKILL.md under 200 lines
- [ ] `eval-skills.py` shows no `line_count_exceeded` critical issues for processed skills

### Child: child-d

**Files/skills needed (entry_reads):**
- `scripts/skills/split-oversized-skill.py`

**Acceptance Criteria:**
- [ ] All 55 Tier 3 engineering/science/_core/_internal skills split
- [ ] All resulting files under 200 lines
- [ ] eval-skills.py clean for these categories

### Child: child-e

**Files/skills needed (entry_reads):**
- `scripts/skills/split-oversized-skill.py`

**Acceptance Criteria:**
- [ ] All 70 Tier 3 data/business/development/operations/coordination/workspace-hub/ai skills split
- [ ] All resulting files under 200 lines
- [ ] eval-skills.py clean for these categories

### Child: child-f

**Files/skills needed (entry_reads):**
- `scripts/skills/split-oversized-skill.py`

**Acceptance Criteria:**
- [ ] All 101 Tier 4 skills trimmed (appendix extraction)
- [ ] All resulting files under 200 lines

### Child: child-g

**Files/skills needed (entry_reads):**
- `scripts/skills/split-oversized-skill.py`
- `.claude/skills/development/skill-eval/scripts/eval-skills.py`

**Acceptance Criteria:**
- [ ] `eval-skills.py` full scan: 0 skills over 200 lines
- [ ] No duplicate skill names from splits
- [ ] All sub-skill `see_also` cross-references valid

## Verification

```bash
# After all children complete:
uv run --no-project python .claude/skills/development/skill-eval/scripts/eval-skills.py --severity warning --format json | python -c "
import json, sys
data = json.load(sys.stdin)
violations = [r for r in data['results'] if any(i['check']=='line_count_exceeded' for i in r.get('issues',[]))]
print(f'{len(violations)} skills over 200 lines')
sys.exit(1 if violations else 0)
"
```
