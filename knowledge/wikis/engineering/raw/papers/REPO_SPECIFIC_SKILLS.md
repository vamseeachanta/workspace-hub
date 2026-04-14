# Repository-Specific Skills Guide

> How to create and use Claude Code skills scoped to individual repositories.
>
> Version: 1.0.0
> Last Updated: 2025-12-23

## Overview

While user-level skills (in `~/.claude/skills/`) are available across all projects, **repository-specific skills** allow you to define specialized capabilities that only apply to a particular codebase.

## When to Use Repo-Specific Skills

### Use Repository-Specific Skills When:

- **Domain expertise is needed**: Skills specific to a codebase's domain (e.g., structural analysis for `digitalmodel/`)
- **Project conventions exist**: Custom workflows, naming patterns, or architectural decisions unique to the repo
- **Sensitive context**: Skills that reference proprietary APIs, internal systems, or project-specific configurations
- **Team standards**: Skills that enforce team-specific coding standards or review processes

### Use User-Level Skills When:

- **Universal applicability**: Skills work the same way regardless of project (PDF handling, Excel creation)
- **Common workflows**: Standard development patterns (MCP servers, web testing)
- **Personal productivity**: Skills you want in every project you work on

## Creating Repository-Specific Skills

### Step 1: Create the Directory Structure

In your repository root, create:

```
your-repo/
└── .claude/
    └── skills/
        └── your-skill-name/
            └── SKILL.md
```

### Step 2: Write the SKILL.md File

Follow the standard skill format with YAML frontmatter:

```markdown
---
name: skill-name
description: Trigger description that tells Claude when to activate this skill
---

# Skill Title

## Purpose

[Explain what this skill does and when to use it]

## Instructions

[Detailed instructions for Claude to follow]

## Examples

[Provide concrete examples of skill usage]
```

### Step 3: Make It Specific

Unlike user-level skills, repo-specific skills should reference:

- Specific file paths within the repository
- Project-specific conventions and patterns
- Local configuration files
- Custom tooling or scripts in the repo

## Example: Structural Analysis Skill

For a marine structural engineering repository like `digitalmodel/`:

```
digitalmodel/
└── .claude/
    └── skills/
        └── structural-analysis/
            └── SKILL.md
```

**SKILL.md content:**

```markdown
---
name: structural-analysis
description: Perform marine structural analysis calculations following DNV and ABS standards. Use for hull stress, buckling, fatigue, and stability calculations.
---

# Marine Structural Analysis

## Purpose

Perform structural engineering calculations for marine vessels and offshore structures following industry standards.

## Standards Reference

- **DNV GL**: Rules for Classification of Ships
- **ABS**: Rules for Building and Classing Steel Vessels
- **ISO 19902**: Fixed Steel Offshore Structures

## Analysis Types

### 1. Hull Stress Analysis

Calculate von Mises stress in hull plating:

```python
# Use src/modules/stress/hull_stress.py
from modules.stress import HullStressCalculator

calculator = HullStressCalculator(
    material=steel_grade,
    thickness=plate_thickness,
    load_case=load_combination
)
```

### 2. Buckling Check

Reference: `config/buckling_criteria.yaml` for allowable limits.

### 3. Fatigue Assessment

Use S-N curves from `data/reference/sn_curves/`.

## Output Requirements

- Generate HTML reports in `reports/structural/`
- Use Plotly for interactive stress visualizations
- Export results to CSV in `data/results/`

## Project-Specific Notes

- All calculations must use safety factors from `config/safety_factors.yaml`
- Units are metric (N, mm, MPa) unless specified
- Reference vessel particulars from `data/vessel/particulars.yaml`
```

## Skill Precedence

Claude Code discovers skills in this order (later overrides earlier):

1. **User-level**: `~/.claude/skills/` (available everywhere)
2. **Workspace-level**: Parent directory skills (if configured)
3. **Repository-level**: `.claude/skills/` (most specific)

This means:
- A repo-specific skill with the same name as a user-level skill will take precedence in that repo
- Repo skills only activate when working within that repository

## Best Practices

### 1. Clear Trigger Descriptions

Write descriptions that clearly indicate when the skill should activate:

```yaml
# Good - specific trigger
description: Calculate NPV and IRR for oil and gas well economics using BSEE data

# Bad - too vague
description: Do financial calculations
```

### 2. Reference Local Resources

Point to specific files and directories in the repo:

```markdown
## Configuration

Load well parameters from `config/wells/` directory.
Use price decks from `data/economics/price_forecasts/`.
```

### 3. Include Examples

Show concrete examples with actual file paths:

```markdown
## Example Usage

To analyze Well #12345:

1. Load well data: `data/wells/12345/production.csv`
2. Apply type curve: `config/type_curves/lower_tertiary.yaml`
3. Output report: `reports/economics/well_12345_npv.html`
```

### 4. Document Dependencies

List any required tools, libraries, or configurations:

```markdown
## Dependencies

- Python 3.11+ with UV environment
- Plotly for visualizations
- pandas for data processing

Setup: Run `uv sync` in repository root.
```

### 5. Keep Skills Focused

One skill per specific capability:

```
.claude/skills/
├── stress-analysis/     # Hull stress calculations
├── buckling-check/      # Buckling assessment
├── fatigue-analysis/    # Fatigue life prediction
└── stability-check/     # Vessel stability
```

Rather than one monolithic "structural-engineering" skill.

## Integration with User-Level Skills

Repo-specific skills can complement user-level skills:

| User-Level Skill | Repo-Specific Extension |
|------------------|------------------------|
| `pdf` (universal) | `report-generator` (uses pdf + repo templates) |
| `xlsx` (universal) | `data-export` (exports to specific Excel format) |
| `webapp-testing` (universal) | `e2e-tests` (tests repo's specific UI flows) |

## Workspace-Hub Repositories

For the 26+ repositories in workspace-hub, consider:

### Candidates for Repo-Specific Skills

| Repository | Potential Skills |
|------------|------------------|
| `digitalmodel` | structural-analysis, marine-codes, vessel-design |
| `worldenergydata` | bsee-analysis, well-economics, production-forecasting |
| `aceengineer-website` | content-management, blog-workflow |
| `energy` | energy-calculations, emissions-tracking |

### Shared via Workspace-Hub

Skills that apply to multiple repos should stay in workspace-hub's user-level skills (already symlinked to `~/.claude/skills/`).

## Troubleshooting

### Skill Not Activating

1. **Check file location**: Must be `.claude/skills/skill-name/SKILL.md`
2. **Verify YAML frontmatter**: Requires `name` and `description` fields
3. **Review description**: Must match the task context

### Skill Conflicts

If a user-level and repo-level skill have the same name:
- Repo-level takes precedence within that repository
- Rename one if you need both behaviors

### Testing Skills

Test activation by referencing the skill explicitly:

```
"Using the structural-analysis skill, calculate the stress in this plate"
```

If it activates correctly, the description trigger is working.

## Related Documentation

- [Claude Code Skills Library](../../../.claude/skills/README.md) - User-level skills
- [Claude Code Skills Documentation](https://docs.anthropic.com/en/docs/claude-code/skills) - Official docs
- [AI Agent Guidelines](AI_AGENT_GUIDELINES.md) - Development workflow

---

*Repository-specific skills enable domain expertise while maintaining the universal capabilities of user-level skills.*
