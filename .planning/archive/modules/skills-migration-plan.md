# Skills Migration Plan

> Consolidating `skills/` into `.claude/skills/`

**Created**: 2026-01-21
**Status**: Planning
**Total Files**: 294 markdown files across both directories

---

## Executive Summary

Two skill directories currently exist:
- `skills/` - 149 files across 13 categories (legacy location)
- `.claude/skills/` - 145 files across 19 categories (target location)

**Recommendation**: Migrate all skills from `skills/` to `.claude/skills/` and deprecate the legacy directory.

---

## Directory Analysis

### Source: `skills/` (Legacy)

| Category | File Count | Description |
|----------|------------|-------------|
| ai-prompting | 11 | AI/LLM prompting techniques |
| automation | 11 | Automation workflows |
| bash | 9 | Bash scripting utilities |
| charts | 6 | Chart/visualization generation |
| communication | 9 | Slack, Teams, Calendly, Miro APIs |
| data-analysis | 16 | Data analysis tools |
| devtools | 13 | Developer tools |
| documentation | 13 | Documentation generation |
| office-docs | 11 | Office document handling |
| productivity | 11 | Notion, Obsidian, Todoist, Trello |
| programming | 6 | Programming utilities |
| sme | 16 | Subject matter expert skills |
| workspace-hub | 14 | Workspace-specific tools |
| **Total** | **149** | |

### Target: `.claude/skills/` (Current)

| Category | File Count | Description |
|----------|------------|-------------|
| agents | 4 | Agent management |
| builders | 2 | Builder patterns |
| communication | 4 | Brand, docs, slack-gif |
| content-design | 4 | Content design |
| context-management | 1 | Context optimization |
| data-engineering | 1 | Data engineering |
| development | 33 | Development workflows |
| devops | 4 | DevOps tools |
| document-handling | 10 | Document processing |
| guidelines | 5 | Style/coding guidelines |
| marketing | 5 | Marketing skills |
| meta | 4 | Meta/self-referential skills |
| optimization | 2 | Performance optimization |
| product | 1 | Product management |
| productivity | 1 | Daily productivity (today) |
| tools | 18 | Utility tools |
| workflows | 5 | Workflow definitions |
| workspace-hub | 40 | Workspace-specific |
| **Total** | **145** | |

---

## Overlap Analysis

### Categories That Exist in Both

| Category | skills/ | .claude/skills/ | Overlap Type |
|----------|---------|-----------------|--------------|
| communication | 9 files | 4 files | **Different content** |
| productivity | 11 files | 1 file | **Different content** |
| workspace-hub | 14 files | 40 files | **Partial overlap** |

### Duplicate Skills (Identical)

| Skill | skills/ Location | .claude/skills/ Location | Status |
|-------|------------------|--------------------------|--------|
| repo-readiness | workspace-hub | workspace-hub | **Identical** - delete from skills/ |
| skill-learner | workspace-hub | workspace-hub | **Identical** - delete from skills/ |

### Duplicate Skills (Different Versions)

| Skill | skills/ Location | .claude/skills/ Location | Status |
|-------|------------------|--------------------------|--------|
| yaml-workflow-executor | workspace-hub (20KB) | development (17KB) | **Different** - merge required |

---

## Migration Plan

### Phase 1: Remove Exact Duplicates

Delete from `skills/` (already exist identically in `.claude/skills/`):

```bash
# Identical copies - safe to remove
rm -rf skills/workspace-hub/repo-readiness
rm -rf skills/workspace-hub/skill-learner
```

**Files affected**: ~12 files

### Phase 2: Migrate Unique Categories

Categories that exist only in `skills/` - migrate entirely:

| Source Category | Target Location | Files |
|-----------------|-----------------|-------|
| `skills/ai-prompting/` | `.claude/skills/ai-prompting/` | 11 |
| `skills/automation/` | `.claude/skills/automation/` | 11 |
| `skills/bash/` | `.claude/skills/bash/` | 9 |
| `skills/charts/` | `.claude/skills/charts/` | 6 |
| `skills/data-analysis/` | `.claude/skills/data-analysis/` | 16 |
| `skills/devtools/` | `.claude/skills/devtools/` | 13 |
| `skills/documentation/` | `.claude/skills/documentation/` | 13 |
| `skills/office-docs/` | `.claude/skills/office-docs/` | 11 |
| `skills/programming/` | `.claude/skills/programming/` | 6 |
| `skills/sme/` | `.claude/skills/sme/` | 16 |

**Total files to migrate**: ~112 files

### Phase 3: Merge Overlapping Categories

#### 3.1 Communication (9 + 4 files)

| skills/communication/ | Action | Target |
|-----------------------|--------|--------|
| calendly-api/ | Migrate | `.claude/skills/communication/calendly-api/` |
| miro-api/ | Migrate | `.claude/skills/communication/miro-api/` |
| slack-api/ | Migrate | `.claude/skills/communication/slack-api/` |
| teams-api/ | Migrate | `.claude/skills/communication/teams-api/` |
| README.md | Skip | Category README not needed |

**Existing in .claude/skills/communication/** (keep as-is):
- brand-guidelines/
- doc-coauthoring/
- internal-comms/
- slack-gif-creator/

#### 3.2 Productivity (11 + 1 files)

| skills/productivity/ | Action | Target |
|----------------------|--------|--------|
| notion-api/ | Migrate | `.claude/skills/productivity/notion-api/` |
| obsidian/ | Migrate | `.claude/skills/productivity/obsidian/` |
| time-tracking/ | Migrate | `.claude/skills/productivity/time-tracking/` |
| todoist-api/ | Migrate | `.claude/skills/productivity/todoist-api/` |
| trello-api/ | Migrate | `.claude/skills/productivity/trello-api/` |
| README.md | Skip | Category README not needed |

**Existing in .claude/skills/productivity/** (keep as-is):
- today/

#### 3.3 Workspace-hub (12 remaining + 40 files)

After removing duplicates, migrate remaining unique skills:

| skills/workspace-hub/ | Action | Target |
|-----------------------|--------|--------|
| agent-os-framework/ | Migrate | `.claude/skills/workspace-hub/agent-os-framework/` |
| bash-script-framework/ | Migrate | `.claude/skills/workspace-hub/bash-script-framework/` |
| claude-reflection/ | **Review** | Compare with claude-reflect in target |
| data-validation-reporter/ | Migrate | `.claude/skills/workspace-hub/data-validation-reporter/` |
| interactive-report-generator/ | Migrate | `.claude/skills/workspace-hub/interactive-report-generator/` |
| pytest-fixture-generator/ | Migrate | `.claude/skills/workspace-hub/pytest-fixture-generator/` |
| python-project-template/ | Migrate | `.claude/skills/workspace-hub/python-project-template/` |
| yaml-workflow-executor/ | **Merge** | Newer version (20KB vs 17KB) |

### Phase 4: Resolve Merge Conflicts

#### yaml-workflow-executor

- **skills/** version: 20,489 bytes (Jan 15, 2026)
- **.claude/skills/** version: 16,649 bytes (Jan 2, 2026)

**Recommendation**: Keep newer/larger version from `skills/`, migrate to `.claude/skills/development/yaml-workflow-executor/`

#### claude-reflection vs claude-reflect

**Action Required**: Manual review to determine if these are the same skill with different names.

---

## Migration Commands

```bash
#!/bin/bash
# Skills Migration Script
# Run from workspace-hub root

set -e

TARGET=".claude/skills"
SOURCE="skills"

# Phase 1: Remove duplicates
rm -rf "$SOURCE/workspace-hub/repo-readiness"
rm -rf "$SOURCE/workspace-hub/skill-learner"

# Phase 2: Migrate unique categories
for cat in ai-prompting automation bash charts data-analysis devtools documentation office-docs programming sme; do
  cp -r "$SOURCE/$cat" "$TARGET/"
done

# Phase 3a: Merge communication
for skill in calendly-api miro-api slack-api teams-api; do
  cp -r "$SOURCE/communication/$skill" "$TARGET/communication/"
done

# Phase 3b: Merge productivity
for skill in notion-api obsidian time-tracking todoist-api trello-api; do
  cp -r "$SOURCE/productivity/$skill" "$TARGET/productivity/"
done

# Phase 3c: Merge workspace-hub (excluding duplicates)
for skill in agent-os-framework bash-script-framework data-validation-reporter interactive-report-generator pytest-fixture-generator python-project-template; do
  cp -r "$SOURCE/workspace-hub/$skill" "$TARGET/workspace-hub/"
done

# Phase 4: Handle yaml-workflow-executor (keep newer)
cp -r "$SOURCE/workspace-hub/yaml-workflow-executor/SKILL.md" "$TARGET/development/yaml-workflow-executor/SKILL.md"

echo "Migration complete. Please review claude-reflection manually."
```

---

## Post-Migration Tasks

1. [ ] Update any references to `skills/` in documentation
2. [ ] Update skill loader paths in scripts
3. [ ] Review and merge claude-reflection / claude-reflect
4. [ ] Remove empty `skills/` directory
5. [ ] Update `.gitignore` if needed
6. [ ] Test skill loading from new locations

---

## File Count Summary

| Phase | Action | Files |
|-------|--------|-------|
| Phase 1 | Remove duplicates | -12 |
| Phase 2 | Migrate unique | +112 |
| Phase 3 | Merge overlapping | +23 |
| Phase 4 | Resolve conflicts | +1 |
| **Net change to .claude/skills/** | | **+136** |

**Final .claude/skills/ count**: ~281 files (145 existing + 136 migrated)

---

## Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| Broken skill references | Search codebase for `skills/` paths before deletion |
| Lost functionality | Git history preserves all changes |
| Naming conflicts | Manual review of similar-named skills |
| Category organization | May need further reorganization post-migration |

---

## Approval

- [ ] Technical review complete
- [ ] Backup created
- [ ] Migration script tested on branch
- [ ] Post-migration validation plan ready
