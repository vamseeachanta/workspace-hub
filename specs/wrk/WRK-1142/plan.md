# WRK-1142 Plan — Migrate Stage Rules into Stage Micro-Skills

## Mission
Move all stage-specific rules from `work-queue-workflow/SKILL.md` into the 20 per-stage
micro-skill files, and wire `start_stage.py` to auto-load the relevant micro-skill at entry.

## What
1. Audit current micro-skills vs SKILL.md — identify gaps per stage
2. Write `scripts/work-queue/migrate-stage-rules.py` (bulk extraction helper; 25% rule)
3. Flesh out all 20 micro-skills (≥5 content lines; scripts-over-LLM rules in stage-04 + stage-10)
4. Patch `start_stage.py` to resolve stage micro-skill glob and print content in resume block
5. Slim `work-queue-workflow/SKILL.md` to ≤150 lines (remove migrated stage-specific sections)
6. Tests: `tests/scripts/test_stage_micro_skills.sh` (≥3 test cases)
7. Commit + push

## Scripts to Create (25% rule)
- `scripts/work-queue/migrate-stage-rules.py` — extracts stage-specific sections from
  SKILL.md by heading pattern; outputs per-stage patch content. Input: SKILL.md path +
  stage number. Output: migration content to append to stage micro-skill.
  Recurrence: likely useful for future SKILL.md splits.

## Pseudocode

```python
# start_stage.py patch — _load_stage_micro_skill(stage, repo_root) → str
def _load_stage_micro_skill(stage: int, repo_root: str) -> str:
    glob_pattern = f"{repo_root}/.claude/skills/workspace-hub/stages/stage-{stage:02d}-*.md"
    matches = sorted(glob.glob(glob_pattern))
    if len(matches) == 0:
        return f"[stage micro-skill not found: {glob_pattern}]"
    if len(matches) > 1:
        raise RuntimeError(f"Multiple micro-skills matched: {matches}")
    return Path(matches[0]).read_text()

# 1. In route_stage() — print for human operator (all invocation types):
micro_skill = _load_stage_micro_skill(stage, repo_root)
print(f"\n--- Stage {stage} Micro-Skill ---\n{micro_skill}\n---")

# 2. In build_prompt() — inject into prompt package for dispatched agents:
#    Add after "## Entry reads" section:
lines.append(f"\n## Stage Micro-Skill (rules for this stage)\n```\n{micro_skill}\n```")
```

```python
# migrate-stage-rules.py — explicit section-to-stage mapping (not raw heading extraction)
# inputs: skill_path
# 1. Read SKILL.md
# 2. Use explicit SECTION_MAP: {section_heading: [stage_nums]} to route content
#    e.g. "Stage 4 — Plan Draft Creation" → [4]
#         "Stage 5 — Plan Draft (Human-in-Loop)" → [5]
#         "Stage 6 — Cross-Review" → [6]
#         "Stage 10 — Work Execution" → [10]
# 3. Cross-cutting sections (terminology, gate policy table, orchestrator pattern) → stay in SKILL.md
# 4. Print per-stage migration content to stdout for review/append
# Note: shared tables (Stage Gate Policy, Plan-Mode Gates) are NOT extracted — manually curated
```

```python
# migrate-stage-rules.py
# inputs: skill_path, stage_num
# 1. Read SKILL.md
# 2. Find sections matching "Stage <N>" headings
# 3. Extract those sections
# 4. Print extraction to stdout for review/append
```

## Tests / Evals
| what | type | expected |
|------|------|----------|
| start_stage.py WRK-test 4 — stdout includes stage-04 content | happy | stdout contains "Plan Draft" |
| start_stage.py WRK-test 10 — stage-N-prompt.md includes stage-10 micro-skill | happy | prompt file contains "Work Execution" |
| valid stage contract + absent micro-skill file | edge | prints "[stage micro-skill not found: ...]", continues without crash |
| valid stage contract + 2 micro-skill files for same stage | edge | raises RuntimeError / exits non-zero |
| All 20 micro-skills have ≥5 content lines | happy | wc -l each ≥5 |
| SKILL.md ≤150 lines after migration | happy | wc -l ≤150 |

## Out of Scope
- Modifying the 20 stage contract YAMLs in `scripts/work-queue/stages/`
- Changes to exit_stage.py
- New stages beyond 20

## Risks
- start_stage.py glob must match filenames exactly — use existing format (stage-NN-*.md)
- SKILL.md slim must preserve cross-cutting sections: terminology, gate policy table,
  orchestrator pattern, practical lessons
