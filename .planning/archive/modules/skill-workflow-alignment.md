# Skill-Workflow Alignment

> Unify skills, scripts, and workflows into a single co-located structure.

## Problem

Today, three concerns are split across three directory trees:

| Concern | Current location | What it does |
|---------|-----------------|--------------|
| Knowledge | `.claude/skills/<domain>/<skill>/SKILL.md` | Tells the agent what to do |
| Execution | `scripts/<category>/` | Runs the actual work |
| Orchestration | Implicit (agent reasoning) or `workflows/` | Sequences the steps |

When a skill triggers, the agent has no idea where the related scripts live. When a script exists, there's no skill to provide context. Workflows are ad-hoc.

## Target Structure

```
.claude/skills/<domain>/<tool>/
  SKILL.md              <- hub skill (<200 lines)
  <sub>/SKILL.md        <- micro-skill per concern (<200 lines each)
  scripts/              <- co-located execution scripts
    <verb>_<noun>.py    <- one script per discrete operation
  workflow.yaml         <- orchestration sequence (optional)
```

### Exemplar: AQWA (implemented)

```
marine-offshore/aqwa/
  SKILL.md              <- hub: when to use, Python API, key classes
  input/SKILL.md        <- configs, file formats, DAT conventions, mesh quality
  output/SKILL.md       <- output formats, validation, benchmarks
  reference/SKILL.md    <- solver stages, OPTIONS keywords, FIDP/FISK cards
  batch-execution/SKILL.md <- batch run orchestration
  scripts/              <- (future: co-located scripts)
```

## Principles

1. **Co-location over separation** — if a script serves a skill, it lives under that skill
2. **Hub + micro-skills** — hub is the entry point (<200 lines), micro-skills split by input/output/reference/tips
3. **200-line hard limit** — forces clean decomposition into single-responsibility units
4. **Workflow = sequence of micro-skills** — `workflow.yaml` declares the order, each step points to a micro-skill + script
5. **Scripts follow skills** — not the other way around. The skill defines what; the script executes how

## Migration Strategy

### Phase 1: High-value tool families (flat prefix -> nested)

| Family | Current flat count | Target structure |
|--------|-------------------|------------------|
| aqwa-* | 5 skills | `aqwa/` (DONE) |
| orcaflex-* | 20+ skills | `orcaflex/` |
| orcawave-* | 6 skills | `orcawave/` |

### Phase 2: Script consolidation

Move scripts from `scripts/` into co-located `<skill>/scripts/` where the relationship is 1:1.
Scripts shared across multiple skills stay in `scripts/lib/`.

### Phase 3: Workflow alignment

Add `workflow.yaml` to skill families that have a natural sequence (e.g., aqwa: input -> analysis -> output -> validation).

## File Size Rules

| File type | Hard limit | Soft target |
|-----------|-----------|-------------|
| Hub SKILL.md | 200 lines | 100 lines |
| Micro-skill SKILL.md | 200 lines | 100 lines |
| Script | 200 lines | 100 lines |
| workflow.yaml | 50 lines | 30 lines |

## What NOT to Nest

- Generic utilities (`scripts/lib/`, `scripts/legal/`) — shared across domains, stay centralized
- Cross-cutting skills (debugging, TDD, brainstorming) — not tool-specific
- One-off skills with no sub-concerns — flat is fine if under 200 lines

## Eval Tooling Impact

`eval-skills.py` already handles nested skills (tested with `cad/blender/`, `cfd/openfoam/`). The `--skill` flag does path substring matching, so `--skill aqwa` finds all nested skills.

## Success Criteria

- Zero flat `<tool>-*` prefix clusters with 3+ siblings in `marine-offshore/`
- All skill files under 200 lines
- Scripts co-located with their parent skill where relationship is 1:1
- `--skill <tool>` finds the full family in eval
