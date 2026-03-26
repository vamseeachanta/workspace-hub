# WRK-1263: Restore aqwa-analysis lost content + split oversized skill

## Context

WRK-1244 identified that 46 lines of AQWA Solver Stages & Backend Mapping content were lost during WRK-639 diverged cleanup. The canonical skill at `.claude/skills/engineering/marine-offshore/aqwa-analysis/SKILL.md` is 718 lines — violating the 400-line hard limit. This WRK restores the lost content and splits the skill to comply.

## Plan

### Step 1: Create `aqwa-reference` sub-skill

Create `.claude/skills/engineering/marine-offshore/aqwa-reference/SKILL.md` containing:

**From current file (move these sections):**
- `## Configuration Examples` (lines 400-448) — Complete AQWA Workflow yaml
- `## Output Formats` (lines 450-477) — CSV and JSON format examples
- `## MCP Tool Integration` (lines 543-592) — Swarm/Memory coordination
- `## Benchmark Validation Criteria` (lines 677-693) — Engineering standard practice
- `### 5. Benchmark Comparison vs OrcaWave` (lines 593-675) — Full benchmark section

**Restored content (from git `50998a85^` diverged path):**
- `## AQWA Solver Stages & Backend Mapping` — RESTART stage table, OPTIONS keyword reference, OPTIONS card ordering, FIDP/FISK cards, backend bug note (46 lines)

### Step 2: Trim main `aqwa-analysis/SKILL.md`

Remove the sections moved to `aqwa-reference`. Add a cross-reference:
```
- [aqwa-reference](../aqwa-reference/SKILL.md) - Solver stages, OPTIONS keywords, config examples, output formats, benchmarks
```

### Step 3: Verify

- `wc -l` on both files — main must be <400, reference should be <400
- `eval-skills.py` passes on both skills

## Files

| File | Action |
|------|--------|
| `.claude/skills/engineering/marine-offshore/aqwa-analysis/SKILL.md` | Edit — remove moved sections, add cross-ref |
| `.claude/skills/engineering/marine-offshore/aqwa-reference/SKILL.md` | Create — new sub-skill with moved + restored content |

## Verification

```bash
wc -l .claude/skills/engineering/marine-offshore/aqwa-analysis/SKILL.md   # must be <400
wc -l .claude/skills/engineering/marine-offshore/aqwa-reference/SKILL.md  # must be <400
uv run --no-project python .claude/skills/development/skill-eval/scripts/eval-skills.py .claude/skills/engineering/marine-offshore/aqwa-analysis/SKILL.md
uv run --no-project python .claude/skills/development/skill-eval/scripts/eval-skills.py .claude/skills/engineering/marine-offshore/aqwa-reference/SKILL.md
```
