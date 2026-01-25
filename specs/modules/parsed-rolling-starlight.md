# Module-Based Refactoring Plan: workspace-hub

**Version**: 1.0.0
**Module**: workspace-hub-module-refactor
**Session ID**: workspace-hub-discipline-refactor
**Session Agent**: Claude Opus 4.5
**Review**: Cross-reviewed (Conservative, Clean Architecture, Pragmatic)
**Recommended Approach**: Pragmatic

---

## Summary

Apply module-based, discipline-aligned structure to workspace-hub `docs/` and `scripts/` directories, consistent with the completed `.claude/skills/` refactoring.

---

## Cross-Review Results

| Perspective | Recommendation | Rationale |
|-------------|----------------|-----------|
| **Conservative** | No changes to .claude/docs/ | Only 8 files, cross-cutting content |
| **Clean Architecture** | Full reorganization (~310 ops) | Complete discipline alignment |
| **Pragmatic** | Balanced (~120 ops) | Archive old, organize active, keep key items at root |

**Selected**: Pragmatic approach - best balance of organization and discoverability.

---

## Current State

### docs/ (43 root files + 90 in modules/)
- 43 orphan MD files at root
- 16 existing module directories with 90+ files
- Needs: Archive completed work, categorize active docs

### scripts/ (22 directories + 6 root scripts)
- Semi-organized but not discipline-aligned
- Key entry points: `workspace`, `repository_sync`
- Needs: Group by discipline, keep entry points at root

### Already Complete
- `.claude/skills/` - 9 disciplines, 224 skills ✓
- `specs/modules/` - Already has modules/ structure ✓
- `data/`, `config/`, `coordination/` - Optimal as-is ✓

---

## Target Structure

### docs/
```
docs/
├── README.md                         # KEEP - navigation hub
├── WORKSPACE_HUB_CAPABILITIES_SUMMARY.md  # KEEP - primary overview
├── WORKSPACE_HUB_REPOSITORY_OVERVIEW.md   # KEEP - repo guide
├── SKILLS_INDEX.md                   # KEEP - quick reference
│
└── modules/
    ├── ai/                           # EXISTS - expand
    │   ├── agent-patterns/           # Agent organization, optimization
    │   ├── model-selection/          # Model routing docs
    │   └── skills/                   # Skill system docs
    ├── archive/                      # NEW
    │   ├── aceengineercode/          # 4 migration files
    │   └── phase1/                   # 9 phase completion files
    ├── repository/                   # NEW - repo management
    ├── testing/                      # EXISTS - expand
    ├── tiers/                        # NEW - tier assessments
    └── ... (existing modules)
```

### scripts/
```
scripts/
├── workspace                         # KEEP - main CLI
├── repository_sync                   # KEEP - main sync
├── setup-claude-env.sh               # KEEP - frequent use
├── README.md                         # NEW - index
│
├── _core/                            # Foundation utilities
│   ├── bash/
│   └── cli/
├── ai/                               # AI tools
│   └── assessment/
├── coordination/                     # Workspace coordination
│   ├── context/
│   ├── repository/
│   ├── routing/
│   └── productivity/
├── data/                             # Data processing
│   ├── batchtools/
│   ├── og-standards/
│   └── python/
├── development/                      # Dev workflows
│   ├── ai-review/
│   ├── ai-workflow/
│   └── testing/
├── operations/                       # Infrastructure
│   ├── compliance/
│   ├── connection/
│   ├── maintenance/
│   ├── monitoring/
│   └── system/
└── _archive/                         # Deprecated
    ├── powershell/
    └── phase1-setup.sh
```

---

## Execution Phases

### Phase 1A: docs/ Archive Cleanup (Low Risk)
**Files**: 13

1. Create `docs/modules/archive/aceengineercode/`
2. Create `docs/modules/archive/phase1/`
3. Move files:
   ```
   ACEENGINEERCODE_*.md (4) → archive/aceengineercode/
   phase1-*.md (4) → archive/phase1/
   PHASE_1_*.md (5) → archive/phase1/
   ```

### Phase 1B: docs/ Active Content (Medium Risk)
**Files**: 26

1. Create new directories:
   - `docs/modules/repository/`
   - `docs/modules/tiers/`
   - `docs/modules/ai/skills/`

2. Move files:
   ```
   AI_*.md (5) → modules/ai/
   AGENT_*.md (2) → modules/ai/agent-patterns/
   SKILL_*.md (5) → modules/ai/skills/
   TESTING_*.md, PYTEST_*.md, DEPLOYMENT_*.md (3) → modules/testing/
   REPOSITORY_*.md (3) → modules/repository/
   SELF_IMPROVING_*.md (3) → modules/repository/
   TIER2_*.md (3), TIER_3_*.md (2) → modules/tiers/
   ```

3. Update `docs/README.md` navigation

### Phase 2A: scripts/ Discipline Alignment (Medium Risk)
**Directories**: 22 → 8 discipline groups

1. Create discipline directories:
   ```bash
   mkdir -p scripts/{_core,ai,coordination,data,development,operations,_archive}
   ```

2. Move directories:
   ```
   ai-assessment/ → ai/assessment/
   ai-review/, ai-workflow/ → development/
   audit/, compliance/, connection/, maintenance/, monitoring/, system/ → operations/
   bash/, cli/ → _core/
   batchtools/, og-standards/, python/ → data/
   context/, repository/, routing/, productivity/ → coordination/
   powershell/ → _archive/
   testing/ → development/testing/
   ```

3. Move root scripts:
   ```
   optimize-mcp-context.sh → _core/
   phase1-setup.sh → _archive/
   repo_sync_batch.sh → coordination/
   sync_statusline.sh → _core/
   ```

### Phase 2B: Documentation Updates (Low Risk)

1. Create `scripts/README.md` with discipline index
2. Update `CLAUDE.md` if any documented paths changed
3. Add README.md to each new discipline directory

---

## Critical Files

| File | Action |
|------|--------|
| `docs/README.md` | Update navigation for new modules |
| `scripts/workspace` | KEEP at root - main CLI |
| `scripts/repository_sync` | KEEP at root - main sync |
| `CLAUDE.md` | Verify script paths still valid |
| `.claude/skills/README.md` | Reference for discipline pattern |

---

## Verification

### After Phase 1 (docs/)
```bash
# Count root files (should be 4)
ls docs/*.md | wc -l

# Verify archive created
ls docs/modules/archive/

# Check for broken links
grep -r "docs/.*\.md" . | grep -v modules
```

### After Phase 2 (scripts/)
```bash
# Count root items (should be 4: workspace, repository_sync, setup-claude-env.sh, README.md)
ls scripts/ | head -10

# Verify main tools work
./scripts/workspace --help
./scripts/repository_sync --help

# Verify discipline dirs exist
ls scripts/{_core,ai,coordination,data,development,operations}
```

---

## Rollback

```bash
# Tag before starting
git tag pre-module-refactor-docs-scripts-$(date +%Y%m%d)

# Rollback if needed
git checkout pre-module-refactor-docs-scripts-{date}
```

---

## Success Criteria

- [ ] docs/ root: 4 files (README + 3 key docs)
- [ ] docs/modules/: 4 new directories (archive, repository, tiers, ai/skills)
- [ ] scripts/ root: 4 items (workspace, repository_sync, setup-claude-env.sh, README.md)
- [ ] scripts/: 8 discipline directories
- [ ] All moved scripts still executable
- [ ] No broken documentation links
- [ ] CLAUDE.md paths still valid

---

## Estimated Changes

| Category | Count |
|----------|-------|
| docs/ files moved | 39 |
| docs/ new directories | 6 |
| scripts/ directories reorganized | 22 → 8 |
| scripts/ root items | 7 → 4 |
| New README.md files | 10 |
| **Total operations** | ~120 |
