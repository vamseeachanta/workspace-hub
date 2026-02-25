# AI-Native Repository Structure Review
## Comparison: Expected vs Current Structure

**Date:** 2025-10-13
**Repositories Reviewed:** assetutilities, digitalmodel
**Reference:** `specs/modules/ai-native/ai_native_infrastructure_input.yaml`

---

## Expected AI-Native Structure

Based on the AI-native infrastructure specification:

```
repository-root/
├── .agent-os/              # Agent OS configuration
│   ├── product/            # mission.md, tech-stack.md, roadmap.md, decisions.md
│   └── instructions/       # Custom workflow instructions (optional)
├── specs/                  # Feature specifications (at root)
│   ├── YYYY-MM-DD-spec-name/
│   └── modules/            # Module-specific specs
├── src/                    # Source code with clear package structure
│   ├── <package_name>/     # Main package
│   └── <module_name>/      # Additional modules
├── tests/                  # Comprehensive test suite
│   ├── unit/               # Unit tests
│   ├── integration/        # Integration tests
│   └── fixtures/           # Test data/fixtures
├── docs/                   # Documentation
│   ├── guides/             # User guides
│   ├── api/                # API documentation
│   └── modules/            # Module-specific docs
├── modules/                # Modular functionality (workspace-level)
│   ├── automation/
│   ├── git-management/
│   ├── ci-cd/
│   ├── monitoring/
│   ├── utilities/
│   ├── documentation/
│   ├── config/
│   └── development/
├── scripts/                # Automation scripts (user-facing)
│   └── utilities/          # Helper utilities
├── data/                   # Data files organized by stage
│   ├── raw/                # Raw/input data
│   ├── processed/          # Processed data
│   └── results/            # Analysis results
├── config/                 # Configuration files
├── reports/                # Generated reports (HTML, PDF)
├── CLAUDE.md               # AI agent configuration
└── README.md               # Human-readable overview
```

---

## Repository 1: assetutilities

### Current Structure Analysis

#### ✅ **COMPLIANT Directories:**

| Directory | Status | Notes |
|-----------|--------|-------|
| `.agent-os/` | ✅ Present | Contains product documentation |
| `specs/` | ✅ Present | Relocated to root with modules/ subdirectory |
| `src/` | ✅ Present | Contains `src/assetutilities/` main package |
| `tests/` | ✅ Present | Has unit/, integration/, fixtures/, modules/ |
| `docs/` | ✅ Present | Extensive documentation structure |
| `scripts/` | ✅ Present | User-facing automation scripts |
| `data/` | ✅ Present | Has raw/, processed/, results/ |
| `config/` | ✅ Present | Configuration files |
| `reports/` | ✅ Present | Generated reports directory |
| `modules/` | ✅ Present | automation/, config/, reporting/ |

#### ⚠️ **ISSUES TO ADDRESS:**

1. **Extra directories (non-standard):**
   - `agents/` - Custom agent definitions (14 subdirectories)
   - `coordination/` - Coordination layer (memory_bank/, orchestration/, subtasks/)
   - `memory/` - Memory management (agents/, sessions/)
   - `slash_commands/` - Custom slash commands
   - `htmlcov/` - Should be in .gitignore, not tracked
   - `dist/` - Build artifacts, should be in .gitignore

2. **Scripts organization:**
   - Currently has: `scripts/au_git_sync/`, `scripts/bash/`, `scripts/bat/`, `scripts/powershell/`, `scripts/dev/`, `scripts/git/`, `scripts/tools/`
   - Expected: `scripts/utilities/` structure
   - **Recommendation:** Consolidate into `scripts/utilities/` or keep as-is if current structure serves specific purpose

3. **Modules structure:**
   - Currently has: `modules/automation/`, `modules/config/`, `modules/reporting/`
   - Expected (for workspace-level): 8 standard modules
   - **Recommendation:** Current structure is appropriate for package-level modules

4. **Tests organization:**
   - Has: `tests/agent_os/`, `tests/bash-setup/`, `tests/modules/`, `tests/unit/`, `tests/integration/`, `tests/fixtures/`
   - Missing clear separation in some areas
   - **Recommendation:** Consolidate module tests into `tests/unit/` and `tests/integration/`

5. **Docs organization:**
   - Extensive structure with many `sub_*` directories (e.g., `docs/sub_automation/`, `docs/sub_ci-cd/`, etc.)
   - Expected: `docs/guides/`, `docs/api/`, `docs/modules/`
   - **Recommendation:** Reorganize into standard structure

#### 📊 **Compliance Score: 70%**

**Strengths:**
- All core directories present
- Good separation of concerns
- Data/ directory properly organized
- Specs relocated to root successfully

**Areas for Improvement:**
- Remove or gitignore build artifacts (htmlcov/, dist/)
- Consider consolidating docs structure
- Standardize scripts organization
- Remove or relocate custom directories (agents/, coordination/, memory/, slash_commands/) to appropriate locations

---

## Repository 2: digitalmodel

### Current Structure Analysis

#### ✅ **COMPLIANT Directories:**

| Directory | Status | Notes |
|-----------|--------|-------|
| `.agent-os/` | ✅ Present | Agent OS configuration |
| `specs/` | ✅ Present | Extensive module-based specs |
| `src/` | ✅ Present | Has `src/digitalmodel/` and `src/marine_engineering/` |
| `tests/` | ✅ Present | Comprehensive test structure |
| `docs/` | ✅ Present | Extensive documentation |
| `scripts/` | ✅ Present | Automation scripts |
| `data/` | ✅ Present | Has raw/, processed/, results/ |
| `config/` | ✅ Present | Configuration files |
| `reports/` | ✅ Present | Generated reports |
| `modules/` | ✅ Present | automation/, config/, reporting/ |

#### ⚠️ **ISSUES TO ADDRESS:**

1. **Extra directories (non-standard):**
   - `agents/` - Custom agent definitions (20+ specialized agents)
   - `coordination/` - Coordination layer (memory_bank/, orchestration/, subtasks/)
   - `memory/` - Memory management (agents/, sessions/)
   - `examples/` - Should be in `docs/examples/` or `tests/fixtures/`
   - `outputs/` - Should be in `data/results/` or `reports/`
   - `logs/` - Should be in .gitignore
   - `htmlcov/` - Should be in .gitignore
   - `htmlcov_engine/` - Should be in .gitignore
   - `tools/` - Should be in `scripts/` or `scripts/utilities/`

2. **Specs organization:**
   - Excellent module-based specs structure
   - Has: `specs/modules/`, `specs/performance/`, `specs/templates/`, `specs/workflows/`
   - **Status:** ✅ Excellent organization

3. **Tests organization:**
   - Very comprehensive: `tests/unit/`, `tests/integration/`, `tests/modules/`, `tests/performance/`, `tests/security/`, `tests/engineering_validation/`, `tests/benchmarks/`
   - **Status:** ✅ Excellent organization (beyond minimum requirements)

4. **Docs organization:**
   - Extensive domain-specific documentation: `docs/domains/` (60+ engineering domains)
   - Has: `docs/guides/`, `docs/modules/`, `docs/examples/`
   - **Status:** ✅ Excellent organization with domain-specific structure

5. **Data organization:**
   - Has specialized data directories: `data/fatigue/`, `data/marine_engineering/`, `data/ocimf/`
   - Also has standard: `data/raw/`, `data/processed/`, `data/results/`
   - **Status:** ✅ Good organization

#### 📊 **Compliance Score: 75%**

**Strengths:**
- All core directories present
- Excellent specs organization (module-based)
- Comprehensive test structure (unit, integration, performance, security)
- Rich domain-specific documentation
- Well-organized data structure
- Good examples and tutorials

**Areas for Improvement:**
- Move `examples/` to `docs/examples/` (partially done)
- Move `outputs/` content to `data/results/` or `reports/`
- Move `tools/` to `scripts/utilities/`
- Remove or gitignore build artifacts (htmlcov/, htmlcov_engine/, logs/)
- Consider relocating custom directories (agents/, coordination/, memory/) or document as extensions

---

## Cross-Repository Observations

### Common Patterns (Good):
1. ✅ Both repositories have `.agent-os/` for Agent OS configuration
2. ✅ Both have `specs/` at root with module-based organization
3. ✅ Both have proper `src/`, `tests/`, `docs/` structure
4. ✅ Both have `data/` with raw/, processed/, results/
5. ✅ Both have `modules/` for package-level functionality
6. ✅ Both have `coordination/` and `memory/` for AI orchestration

### Common Issues (Need Attention):
1. ⚠️ Both have `agents/` directory at root (AI-specific, not in standard spec)
2. ⚠️ Both have build artifacts that should be gitignored (htmlcov/, dist/)
3. ⚠️ Both have `coordination/` and `memory/` directories (AI orchestration extensions)
4. ⚠️ digitalmodel has `tools/` that should be in `scripts/`
5. ⚠️ digitalmodel has `outputs/` that should be in `data/results/` or `reports/`

---

## Recommendations

### Priority 1: Immediate Actions (Both Repos)
1. **Add/Update .gitignore:**
   ```
   htmlcov/
   htmlcov_engine/
   dist/
   logs/
   *.log
   __pycache__/
   *.pyc
   .pytest_cache/
   *.egg-info/
   ```

2. **Document AI Extensions:**
   - Create `docs/ai-extensions.md` explaining `agents/`, `coordination/`, `memory/`, `slash_commands/`
   - These are valid AI orchestration extensions but should be documented

### Priority 2: Structure Refinements (assetutilities)
1. **Consolidate scripts:**
   - Move `scripts/bash/`, `scripts/bat/`, `scripts/powershell/`, `scripts/dev/`, `scripts/tools/` into `scripts/utilities/` with subdirectories
   - Keep `scripts/au_git_sync/` and `scripts/git/` at top level if they are primary tools

2. **Reorganize docs:**
   - Move `docs/sub_*` directories into `docs/guides/` or `docs/modules/`
   - Create clear structure: `docs/guides/`, `docs/api/`, `docs/modules/`, `docs/references/`

3. **Standardize tests:**
   - Move module-specific tests to `tests/unit/modules/` or `tests/integration/modules/`
   - Keep `tests/agent_os/` as integration tests

### Priority 2: Structure Refinements (digitalmodel)
1. **Relocate directories:**
   ```bash
   # Move tools to scripts
   mv tools/* scripts/utilities/
   rmdir tools

   # Move outputs to appropriate locations
   mv outputs/hydrodynamic_charts reports/
   mv outputs/profiling data/results/profiling/
   rmdir outputs

   # Ensure examples are in docs
   # (already has docs/examples/, just verify content)
   ```

2. **Keep domain structure:**
   - digitalmodel's `docs/domains/` structure is excellent for engineering domains
   - This is a valid extension beyond the standard spec

### Priority 3: Documentation Updates (Both Repos)
1. **Update CLAUDE.md:**
   - Document AI extensions (agents/, coordination/, memory/)
   - Explain any deviations from standard structure
   - Reference AI-native infrastructure spec

2. **Create STRUCTURE.md:**
   - Document current directory structure
   - Explain purpose of each top-level directory
   - Map structure to AI-native spec compliance

3. **Update README.md:**
   - Add "Repository Structure" section
   - Link to STRUCTURE.md and AI-native spec
   - Explain any custom extensions

---

## Conclusion

### assetutilities: 70% Compliant
- **Status:** Good foundation, needs refinement
- **Strengths:** Core structure present, good data organization
- **Focus Areas:** Documentation reorganization, script consolidation, artifact cleanup

### digitalmodel: 75% Compliant
- **Status:** Strong compliance with excellent extensions
- **Strengths:** Excellent specs, comprehensive tests, rich domain docs
- **Focus Areas:** Relocate outputs/tools, artifact cleanup, document extensions

### Overall Assessment:
Both repositories demonstrate **strong compliance** with AI-native infrastructure requirements while including valuable AI orchestration extensions (agents/, coordination/, memory/). The core structure is solid. Primary improvements needed are:
1. Artifact cleanup (.gitignore updates)
2. Minor directory relocations
3. Documentation of AI extensions as valid enhancements to the standard spec

**Next Steps:**
1. Implement Priority 1 actions (gitignore updates, AI extension documentation)
2. Review and approve Priority 2 refinements with stakeholders
3. Update repository documentation to reflect current and target state
