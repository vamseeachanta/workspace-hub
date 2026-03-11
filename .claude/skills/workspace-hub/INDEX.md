# Workspace Hub Skills

> 14 subcategories in this domain.

## Subcategories

- [Agent Teams](agent-teams/INDEX.md) — 2 skills
- [Clean Code](clean-code/SKILL.md) — 1 skill (v2.1.0)
- [Comprehensive Learning](comprehensive-learning/SKILL.md) — 1 skill
- [Ecosystem Health](ecosystem-health/INDEX.md) — 1 skill
- [File Taxonomy](file-taxonomy/SKILL.md) — 1 skill (v1.6.0)
- [Improve](improve/INDEX.md) — 1 skill
- [Infrastructure Layout](infrastructure-layout/SKILL.md) — 1 skill (v1.0.0)
- [Interoperability](interoperability/INDEX.md) — 1 skill
- [Repo Sync](repo-sync/INDEX.md) — 1 skill
- [Repo Structure](repo-structure/SKILL.md) — 1 skill (v1.4.0)
- [Skill Sync](skill-sync/INDEX.md) — 1 skill
- [Sync](sync/INDEX.md) — 1 skill
- [Tool Readiness](tool-readiness/SKILL.md) — 1 skill
- [What's Next](whats-next/SKILL.md) — 1 skill (v1.0.0)
- [Workstations](workstations/SKILL.md) — 1 skill
- [Work-Queue Workflow](work-queue-workflow/SKILL.md) — 1 skill (v1.0.0)
- [Workflow Gatepass](workflow-gatepass/SKILL.md) — 1 skill (v1.0.0)
- [WRK Lifecycle Testpack](wrk-lifecycle-testpack/SKILL.md) — 1 skill (v1.0.0)

## File Structure Skills Cluster

> Knowledge map: [`.claude/docs/file-structure-skills-map.md`](../docs/file-structure-skills-map.md)

```
                 ┌─────────────────────┐
                 │   repo-structure    │  ← start here for directory questions
                 └──────┬─────────────┘
                        │ see_also
          ┌─────────────┼──────────────┐
          ▼             ▼              ▼
 infrastructure-   file-taxonomy   clean-code
 layout            (where to put   (how big;
 (infra/ package   files + AI log  God Objects)
  sub-domains)      locations)
```

| Skill | Scope | When to Invoke |
|-------|-------|----------------|
| `repo-structure` | Top-level dirs, tier rules, root cleanliness | Before creating any directory or moving source files |
| `file-taxonomy` | Output file placement, formats, gitignore, **AI session log paths** | Before writing any generated/output file; finding AI logs |
| `clean-code` | File/function size limits, God Object detection, refactor guidance | Before accepting or writing any large Python module |
| `infrastructure-layout` | `infrastructure/` sub-domain layout | Adding/auditing cross-cutting shared code |

*Updated WRK-689 (2026-03-03). Full map: `.claude/docs/file-structure-skills-map.md`.*
