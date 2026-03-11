# WRK-577 Plan: Normalize SKILL.md Frontmatter for 9 Skipped Skills

## Mission

Fix YAML frontmatter in 9 SKILL.md files so the skill loader reports 0 skipped skills.

## Steps

1. **Audit each target file** — identify specific failure mode (missing `---`, syntax error, missing `name`)
2. **Repair frontmatter** — add/fix YAML delimiters; infer `name`, `description`, `version`, `category`, `type` from sibling skills and directory slug
3. **Preserve body content** — only modify the frontmatter block; no behavior changes
4. **Validate incrementally** — run `scripts/skills/validate-skills.sh` after each batch; target: 503 files, 0 skipped
5. **Cross-review** — submit diff to Claude/Codex/Gemini; resolve any MAJOR verdicts

## Target Files

| File | Failure Mode |
|------|-------------|
| `.claude/skills/digitalmodel/module-lookup/SKILL.md` | Missing `name` field |
| `.claude/skills/workspace-hub/document-batch/SKILL.md` | Missing frontmatter |
| `.claude/skills/data/energy/bsee-data-extractor/SKILL.md` | YAML syntax error |
| `.claude/skills/data/energy/npv-analyzer/SKILL.md` | YAML syntax error |
| `.claude/skills/data/energy/production-forecaster/SKILL.md` | YAML syntax error |
| `.claude/skills/_diverged/worldenergydata/optimization/model-selection/SKILL.md` | Missing `name` |
| `.claude/skills/_diverged/worldenergydata/optimization/usage-optimization/SKILL.md` | Missing `name` |
| `.claude/skills/_diverged/worldenergydata/product/product-roadmap/SKILL.md` | Missing `name` |
| `.claude/skills/_diverged/worldenergydata/_internal/meta/python-code-refactor/SKILL.md` | Missing frontmatter |

## Test Strategy

- Gate: `scripts/skills/validate-skills.sh` → must report 0 skipped
- Before count: 9 skipped
- After count: 0 skipped
- No other skill files modified (verify via `git diff --name-only`)

## Acceptance Criteria

- All 9 files parse as valid YAML frontmatter
- Required `name` field present in all 9
- Skill validator reports 0 skipped
- No content regressions outside metadata
