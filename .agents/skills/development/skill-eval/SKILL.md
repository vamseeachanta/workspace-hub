---
name: skill-eval
description: Evaluate all workspace-hub skills for structural validity, content quality,
  cross-reference integrity, and registry consistency. Runs 18 checks across critical,
  warning, and info severity levels with actionable fix suggestions.
type: reference
version: 1.0.0
category: development
last_updated: 2026-01-29
capabilities:
- structural_validation
- content_quality_analysis
- cross_reference_integrity
- report_generation
tools:
- Bash
- Read
- Glob
- Grep
related_skills:
- skill-creator
- verification-loop
requires: []
see_also: []
tags: []
---

# Skill Eval

## Quick Start

```bash
# Full evaluation of all skills
uv run .Codex/skills/development/skill-eval/scripts/eval-skills.py

# JSON output
uv run .Codex/skills/development/skill-eval/scripts/eval-skills.py --format json

# Single skill
uv run .Codex/skills/development/skill-eval/scripts/eval-skills.py --skill testing-tdd-london

# Only critical issues
uv run .Codex/skills/development/skill-eval/scripts/eval-skills.py --severity critical
```

## When to Use

- Auditing skill quality after bulk creation or migration
- Pre-release validation of the skills library
- CI/CD quality gate for skill changes
- Identifying broken cross-references after renaming skills
- Checking compliance with v2 SKILL.md template format

## Core Concepts

### Evaluation Dimensions

The evaluator runs 18 checks organized into three severity levels:

**Critical** (blocks skill usage):
- YAML frontmatter exists and parses
- Required fields present: `name`, `description`

**Warning** (degrades quality):
- Version follows semver, category matches directory
- Required content sections present (Quick Start, When to Use, etc.)
- Code blocks in key sections, no TODO/FIXME markers
- Cross-references in `related_skills` resolve to real skills

**Info** (improvement opportunities):
- Uses v2 template format, has optional sections (Metrics, etc.)
- No duplicate skill names across the library

### Report Output

Reports include:
- Summary with pass/fail counts and percentages
- Issues grouped by severity with counts
- Per-category breakdown
- Top 10 most common issues
- Per-skill details with actionable fix suggestions

## Usage Examples

### Full Evaluation

```bash
uv run .Codex/skills/development/skill-eval/scripts/eval-skills.py
```

Output:
```
================================================================
  SKILL EVALUATION REPORT
  Generated: 2026-01-29T14:30:00+00:00
================================================================

SUMMARY
----------------------------------------
  Total skills evaluated:  230
  Passed (no critical):    187  (81.3%)
  Warnings only:           102  (44.3%)
  Critical failures:        43  (18.7%)
```

### JSON for CI/CD

```bash
uv run .Codex/skills/development/skill-eval/scripts/eval-skills.py \
  --format json --severity critical \
  --output reports/skill-eval.json
```

### Filter by Category

```bash
uv run .Codex/skills/development/skill-eval/scripts/eval-skills.py --category development
```

### Summary Only

```bash
uv run .Codex/skills/development/skill-eval/scripts/eval-skills.py --summary-only
```

## Audit Scripts

Run these scripts as part of skill evaluation to catch structural violations and coverage gaps:

```bash
# Check for structural violations (README presence, word count, description length, XML tags)
bash scripts/skills/audit-skill-violations.sh

# Validate skill structure (name conventions, required fields)
bash scripts/skills/validate-skills.sh

# Check which skills lack any script call reference
bash scripts/skills/skill-coverage-audit.sh
```

## Housekeeping Issue Workflow

When asked to review the entire skill ecosystem and create a housekeeping GitHub issue, use a layered audit rather than relying on one script:

1. Run the evaluator summary for the whole ecosystem:
   ```bash
   uv run .Codex/skills/development/skill-eval/scripts/eval-skills.py --summary-only
   ```
2. Check cross-agent visibility/parity before claiming ecosystem health:
   ```bash
   find -L .Codex/skills -name SKILL.md -not -path '*/_archive/*' | wc -l
   find -L .codex/skills -name SKILL.md -not -path '*/_archive/*' | wc -l
   find -L .gemini/skills -name SKILL.md -not -path '*/_archive/*' | wc -l
   test -L .codex/skills && echo codex_symlink_ok || echo codex_symlink_bad
   test -L .gemini/skills && echo gemini_symlink_ok || echo gemini_symlink_bad
   ```
3. Add a targeted active-skill inventory that excludes `_archive` but deliberately reports grouping/taxonomy drift, including:
   - top-level category counts and categories with <=2 skills
   - missing `category` frontmatter
   - frontmatter category vs directory mismatches
   - duplicate frontmatter names
   - oversized `SKILL.md` files
   - missing `## Quick Start` / `## When to Use`
   - skills without linked `scripts/`, `references/`, `templates/`, or `assets/`
4. Search existing GitHub issues before creating a new one, and reference related open/closed skill-curation issues to avoid duplication.
5. Frame the issue as a recurring housekeeping umbrella when the user asks for periodic review: weekly deterministic report, monthly semantic/grouping review, quarterly adversarial taxonomy review.
6. Include acceptance criteria for reports, trend deltas, archive handling (`_archive` and `_archived`), category alias/waiver policy, and no issue spam.

## Best Practices

- Run after creating new skills with `/skill-creator` to validate structure
- Use `--format json` in CI pipelines for machine-readable output
- Address critical issues first (missing frontmatter, invalid YAML)
- Use `--severity warning` to focus on actionable improvements
- Run `--category` filters for focused audits of specific skill areas
- If skills or index markdown changes, regenerate derived skills summary artifacts: `uv run --no-project python scripts/skills/generate-skill-summary.py`

## Error Handling

| Exit Code | Meaning |
|-----------|---------|
| 0 | All skills pass (no critical issues) |
| 1 | Critical failures found |
| 2 | Script error (missing directory, invalid arguments) |

| Common Issue | Cause | Fix |
|-------------|-------|-----|
| `frontmatter_missing` | Skill uses legacy heading format | Add `---` delimited YAML frontmatter |
| `yaml_invalid` | Syntax error in frontmatter | Fix YAML syntax (check colons, indentation) |
| `related_skill_unresolved` | Referenced skill name doesn't exist | Correct the name or remove the reference |
| `section_missing` | Missing required H2 section | Add the section heading and content |

## Metrics & Success Criteria

| Metric | Target |
|--------|--------|
| Skills passing all critical checks | 100% |
| Skills with complete v2 sections | >80% |
| Resolved cross-references | 100% |
| No TODO/FIXME in skills | 100% |

## Version History

- **1.0.0** (2026-01-29): Initial release with 18 checks, human + JSON output, category/skill filtering
