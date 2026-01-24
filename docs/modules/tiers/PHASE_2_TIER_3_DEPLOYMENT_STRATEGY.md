# Phase 2 Tier 3 Test Coverage Expansion Strategy

**Status:** In Progress
**Target:** 75% Test Coverage Baseline Deployment
**Date:** 2025-01-14

## Executive Summary

Phase 2 Tier 3 focuses on deploying pytest baseline infrastructure to **7 FULL DEPLOY repositories** and managing **2 ARCHIVE repositories** with minimal new test requirements.

## Repository Classification

### FULL DEPLOY (7 repositories - Active Development)

These repositories have active Python codebase with existing test infrastructure:

| Repository | pyproject.toml | tests/ | src/ Python Files | Status |
|------------|---|---|---|---|
| **assethold** | ✓ | ✓ (33 files) | ✓ (42 files) | **PRODUCTION READY** |
| **pyproject-starter** | ✓ | ✓ (2 files) | ✓ (5 files) | **READY FOR EXPANSION** |
| **ai-native-traditional-eng** | ✓ | ✓ (1 file) | ✓ (3 files) | **READY FOR EXPANSION** |
| **achantas-data** | ✓ | ✓ (2 files) | ✓ (2 files) | **READY FOR EXPANSION** |
| **seanation** | ✓ | ✓ (1 file) | ✓ (1 file) | **READY FOR EXPANSION** |
| **saipem** | ✓ | ✓ (0 files) | ✓ (2 files) | **NEEDS TEST CREATION** |
| **acma-projects** | ✓ | ✓ (1 file) | ✓ (2 files) | **READY FOR EXPANSION** |

### ARCHIVE (2 repositories - Maintenance Only)

These repositories are marked for archive with minimal active development:

| Repository | Status | Notes |
|------------|--------|-------|
| **client_projects** | ARCHIVE | Large legacy codebase, minimal maintenance |
| **OGManufacturing** | ARCHIVE | Reference/documentation repository |
| **achantas-media** | ARCHIVE | Media storage, no development |

*Total Active Development: 7 FULL DEPLOY repositories*

## Phase 2 Deployment Steps

### Step 1: Deploy pytest.ini to FULL DEPLOY Repositories

**Tier 3 Minimal pytest.ini Configuration:**

```ini
[pytest]
testpaths = tests
python_files = test_*.py *_test.py
python_classes = Test*
python_functions = test_*
addopts =
    -v
    --tb=short
    --strict-markers
    --disable-warnings
markers =
    slow: marks tests as slow (deselect with '-m "not slow"')
    integration: marks tests as integration tests
    unit: marks tests as unit tests
```

**Tier 3 Dependencies (3 plugins):**
```
pytest>=7.4.0
pytest-cov>=4.1.0
pytest-mock>=3.11.1
```

### Step 2: Update pyproject.toml for Each Repository

Add test dependencies section:

```toml
[project.optional-dependencies]
test = [
    "pytest>=7.4.0",
    "pytest-cov>=4.1.0",
    "pytest-mock>=3.11.1",
]
```

### Step 3: Run Test Collection and Coverage Baseline

For each repository:
1. Install test dependencies
2. Run pytest --collect-only
3. Run pytest --cov=src --cov-report=term
4. Document baseline coverage

### Step 4: Expand Test Coverage to 75% Target

For each repository with baseline < 75%:
1. Identify gaps in test coverage
2. Create minimal tests for untested modules
3. Target 75% coverage (not 90% - Tier 3 efficiency)
4. Generate coverage reports

### Step 5: Archive Status Documentation

For archive repositories:
1. Mark as ARCHIVE in documentation
2. Document current state
3. Note: No new tests required
4. Preserve existing structure

## Expected Outcomes

### Coverage Targets (75% for Tier 3)

| Repository | Current Estimate | Target | Gap |
|-----------|---|---|---|
| assethold | ~70% | 75% | +5% |
| pyproject-starter | ~50% | 75% | +25% |
| ai-native-traditional-eng | ~40% | 75% | +35% |
| achantas-data | ~45% | 75% | +30% |
| seanation | ~30% | 75% | +45% |
| saipem | ~0% | 75% | +75% |
| acma-projects | ~50% | 75% | +25% |

### Deliverables

1. **pytest.ini** in each FULL DEPLOY repository root
2. **Updated pyproject.toml** with test dependencies
3. **Baseline coverage report** for each repository
4. **Test expansion plan** for repositories < 75%
5. **ARCHIVE status documentation** for 3 archive repositories
6. **Phase 2 Tier 3 Comprehensive Report**

## Timeline

| Phase | Duration | Key Milestones |
|-------|----------|-----------------|
| **Deployment** | 2-3 hours | pytest.ini + pyproject.toml updates |
| **Baseline Testing** | 1-2 hours | Coverage collection and analysis |
| **Test Expansion** | 4-6 hours | Create/expand tests to 75% target |
| **Documentation** | 1 hour | Archive status, comprehensive report |
| **Git Commit** | 30 mins | Phase 2 Tier 3 deployment commit |

**Total Estimated Time: 8-12 hours**

## Success Criteria

✅ All 7 FULL DEPLOY repos have pytest.ini
✅ All 7 FULL DEPLOY repos have updated pyproject.toml
✅ 75% coverage baseline established for each FULL DEPLOY repo
✅ Test expansion roadmap created for each repo
✅ ARCHIVE status documented for 3 repos
✅ Comprehensive Phase 2 Tier 3 report generated
✅ All changes committed to git

## Risk Mitigation

| Risk | Impact | Mitigation |
|------|--------|-----------|
| Test suite complexity varies | HIGH | Use minimal Tier 3 approach, focus on coverage not quality |
| Dependency conflicts | MEDIUM | Test each repo independently, resolve before moving to next |
| Time constraints | MEDIUM | Prioritize assethold and pyproject-starter first |
| Archive repo confusion | LOW | Clear documentation of ARCHIVE vs FULL DEPLOY status |

## Next Steps (Phase 3)

- Monitor test execution performance
- Expand coverage further if time permits
- Begin Phase 3: Monitoring & Reporting Dashboards

---

*This strategy ensures systematic deployment while respecting Tier 3 efficiency requirements.*
