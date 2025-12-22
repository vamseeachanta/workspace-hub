# Implementation Roadmap: Testing & UV Modernization

**Created:** 2025-09-28
**Status:** Ready for Implementation
**Timeline:** 4-6 weeks

## Overview

This roadmap implements baseline testing and UV environment modernization across 27 repositories based on comprehensive analysis completed on 2025-09-28.

## Current State Summary

### Testing Infrastructure
- **27 total repositories**
- **11 repos (40.7%) have tests** - but most are incomplete
- **16 repos (59.3%) have NO tests** - critical gap
- **Only 1 repo has comprehensive testing** (digitalmodel: 200+ tests, coverage, CI/CD)
- **Only 2 repos have CI/CD** for testing

### UV Environment Status
- **21 repos (84%) already use UV** - excellent modernization
- **4 repos need UV migration** (achantas-data, investments, assethold, assetutilities)
- **All repos use Python 3.8+** - modern versions

## Implementation Phases

---

## Phase 1: Quick Wins (Week 1)
**Goal:** Establish testing baselines for repos with NO tests
**Impact:** High - Covers 59% of repositories
**Effort:** Low - Use templates

### Repositories (16 repos with NO tests):
1. achantas-media
2. acma-projects
3. ai-native-traditional-eng
4. assethold
5. coordination
6. doris
7. energy
8. frontierdeepwater
9. hobbies
10. investments
11. memory
12. sabithaandkrishnaestates
13. sd-work
14. seanation
15. teamresumes
16. worldenergydata

### Actions:
1. ✅ **Add pytest configuration** (5 min per repo)
   - Copy `/docs/testing-templates/pytest.ini.template`
   - Or add to pyproject.toml using `/docs/testing-templates/pyproject.toml.pytest.template`

2. ✅ **Create tests/ directory structure** (2 min per repo)
   ```
   tests/
   ├── __init__.py
   ├── unit/
   │   └── __init__.py
   └── conftest.py (from template)
   ```

3. ✅ **Add initial smoke test** (3 min per repo)
   - Create `tests/test_smoke.py` with basic import tests
   - Target: Verify package imports work

4. ✅ **Add coverage configuration** (3 min per repo)
   - Copy `.coveragerc` template
   - Set minimum coverage to 60% initially

5. ✅ **Add GitHub Actions CI/CD** (5 min per repo)
   - Copy `.github/workflows/python-tests.yml.template`
   - Configure for repo's Python version

**Deliverable:** All 16 repos have baseline testing infrastructure (3 days)

---

## Phase 2: UV Migration for 4 Repos (Week 1)
**Goal:** Complete UV migration for remaining repos
**Impact:** Medium - Standardizes all repos
**Effort:** Low to Medium

### Low Effort (2 repos - 1 hour total):
1. **achantas-data**
   - Add `uv.toml` from template
   - Test with: `uv pip compile pyproject.toml -o requirements.txt`

2. **investments**
   - Add `uv.toml` from template
   - Minimal dependencies make this trivial

### Medium Effort (1 repo - 2 hours):
3. **assethold**
   - Currently uses Poetry + has UV config
   - Decision needed: Keep Poetry or migrate fully to UV
   - If migrating: Remove poetry.lock, test dependencies
   - Recommended: Migrate to UV for consistency

### Higher Effort (1 repo - 4 hours):
4. **assetutilities**
   - Complex dependencies
   - No UV config yet
   - Create `uv.toml` and test thoroughly
   - May need workspace configuration

**Deliverable:** 100% UV adoption across all Python repos (2 days)

---

## Phase 3: Enhance Existing Tests (Week 2-3)
**Goal:** Improve repos that already have tests
**Impact:** High - Increases quality of existing test suites
**Effort:** Medium

### Repositories with Tests (11 repos):

#### Priority 1: Add Coverage (9 repos - no coverage):
1. aceengineer-admin (2 tests)
2. aceengineer-website (21 tests)
3. aceengineercode (20+ tests)
4. achantas-data (5+ tests)
5. assetutilities (10+ tests)
6. client_projects (50+ tests)
7. OGManufacturing (5+ tests)
8. pyproject-starter (3 tests)
9. rock-oil-field (20+ tests)

**Actions per repo (30 min each):**
- Add `.coveragerc` or coverage config to pyproject.toml
- Set minimum coverage threshold (start at 60%)
- Integrate coverage into CI/CD
- Run baseline coverage report

#### Priority 2: Add CI/CD (9 repos - no CI/CD):
Same 9 repos as above

**Actions per repo (20 min each):**
- Add GitHub Actions workflow
- Configure to run tests on PR and push
- Add coverage reporting to workflow
- Add status badges to README

#### Priority 3: Expand digitalmodel (already excellent):
- Already has 200+ tests, coverage, CI/CD
- Expand coverage from current level to 90%+
- Add integration tests if missing
- Document testing strategy

#### Priority 4: Expand saipem CI/CD:
- Has CI/CD but only 5+ tests
- Expand test suite using baseline templates
- Increase coverage

**Deliverable:** All repos with tests have coverage + CI/CD (5 days)

---

## Phase 4: Test Expansion (Week 3-4)
**Goal:** Increase test coverage in all repos
**Impact:** Critical - Ensures quality
**Effort:** High but distributed

### Strategy:
1. **Target 80% coverage** for all production repos
2. **Target 60% coverage** for tool/utility repos
3. **Focus on critical paths** first

### Approach per repository:
1. Run coverage report to identify gaps
2. Prioritize untested critical code
3. Write unit tests for pure functions
4. Write integration tests for workflows
5. Add e2e tests for user-facing features

### Priority Repositories (production code):
1. **digitalmodel** - expand to 90%+ (already at high coverage)
2. **aceengineer-website** - 21 tests, expand for full coverage
3. **aceengineercode** - 20+ tests, expand for engineering calcs
4. **client_projects** - 50+ tests, ensure all client projects covered
5. **rock-oil-field** - 20+ tests, expand for structural analysis

**Time estimate:** 1-3 days per major repository
**Deliverable:** All production repos at 80%+ coverage (10 days)

---

## Phase 5: Documentation & Training (Week 4)
**Goal:** Ensure team can maintain and expand tests
**Impact:** Critical for long-term success
**Effort:** Low

### Actions:
1. **Update all README files** (1 hour total)
   - Add testing section using template
   - Include "How to run tests"
   - Include coverage reporting instructions

2. **Create testing guide** (2 hours)
   - Combine baseline-testing-standards.md with practical examples
   - Add troubleshooting section
   - Add best practices from successful repos

3. **Create UV migration guide** (1 hour)
   - Document migration process
   - Include rollback procedures
   - Add troubleshooting

4. **Team training session** (2 hours)
   - Present testing standards
   - Demonstrate running tests
   - Show coverage reporting
   - Q&A session

**Deliverable:** Complete documentation + trained team (2 days)

---

## Success Metrics

### Testing Metrics (Track Weekly):
- **Baseline Coverage:** % of repos with tests
  - Current: 40.7% (11/27)
  - Target: 100% (27/27)

- **CI/CD Coverage:** % of repos with automated testing
  - Current: 7.4% (2/27)
  - Target: 100% (27/27)

- **Average Code Coverage:** Mean coverage across all repos
  - Current: Unknown (only 1 repo measured)
  - Target: 70%+ average

- **Test Count:** Total tests across all repos
  - Current: ~330+ tests
  - Target: 1,000+ tests

### UV Metrics (Track Once):
- **UV Adoption:** % of Python repos using UV
  - Current: 84% (21/25)
  - Target: 100% (25/25)

- **Standardization:** % using standard uv.toml template
  - Current: 84% (21/25)
  - Target: 100% (25/25)

---

## Risk Mitigation

### Testing Risks:
1. **Risk:** Tests break existing code
   - **Mitigation:** Start with smoke tests, expand gradually
   - **Rollback:** Tests are additive, can disable in CI/CD

2. **Risk:** Team doesn't write new tests
   - **Mitigation:** Training + documentation + PR templates
   - **Enforcement:** Add coverage gates to CI/CD (warning first, then blocking)

3. **Risk:** Test maintenance burden
   - **Mitigation:** Focus on critical paths, use fixtures/factories
   - **Strategy:** Tests should find bugs, not create busywork

### UV Migration Risks:
1. **Risk:** Dependency conflicts during migration
   - **Mitigation:** Test in isolated environment first
   - **Rollback:** Keep old requirements files during transition

2. **Risk:** CI/CD breaks after migration
   - **Mitigation:** Update CI/CD configs simultaneously
   - **Testing:** Test in feature branch before merging

3. **Risk:** Complex dependencies fail (assetutilities)
   - **Mitigation:** Migrate last, extensive testing
   - **Fallback:** Keep pip as backup option

---

## Resource Requirements

### Time Investment:
- **Phase 1 (Testing Baseline):** 3 days (~2 hours/day)
- **Phase 2 (UV Migration):** 2 days (~3 hours/day)
- **Phase 3 (Enhance Tests):** 5 days (~4 hours/day)
- **Phase 4 (Test Expansion):** 10 days (~6 hours/day)
- **Phase 5 (Documentation):** 2 days (~3 hours/day)

**Total:** 22 days of effort over 4-6 week timeline (allows for parallel work)

### Team Members Needed:
- **1 lead engineer** (full roadmap oversight)
- **2-3 developers** (Phase 1-3: setup, Phase 4: test writing)
- **All team members** (Phase 5: training)

### Tools Needed (All Free):
- pytest (already installed in most repos)
- coverage.py (free, add to requirements)
- GitHub Actions (free for public repos)
- UV (free, already adopted in 84% of repos)

---

## Implementation Schedule

### Week 1:
- **Mon-Wed:** Phase 1 (Add baseline tests to 16 repos)
- **Thu-Fri:** Phase 2 (UV migration for 4 repos)

### Week 2:
- **Mon-Wed:** Phase 3.1 (Add coverage to 9 repos)
- **Thu-Fri:** Phase 3.2 (Add CI/CD to 9 repos)

### Week 3:
- **Mon-Fri:** Phase 4.1 (Test expansion - priority repos)

### Week 4:
- **Mon-Wed:** Phase 4.2 (Test expansion - remaining repos)
- **Thu-Fri:** Phase 5 (Documentation + training)

---

## Next Steps

### Immediate Actions (Today):
1. ✅ **Review this roadmap** - Get team buy-in
2. ✅ **Select pilot repository** - Start with 1 repo from Phase 1
3. ✅ **Assign owners** - Who owns Phase 1? Phase 2?
4. ✅ **Schedule kickoff** - 30 min team meeting

### This Week:
1. **Implement Phase 1 for pilot repo** (2 hours)
   - Validate templates work
   - Document any issues
   - Adjust templates if needed

2. **Begin Phase 1 rollout** (6 hours)
   - Batch process remaining 15 repos
   - Use parallel operations
   - Verify all CI/CD runs pass

3. **Begin Phase 2** (4 hours)
   - Start with easy repos (achantas-data, investments)
   - Test UV migration thoroughly

### Next Week:
1. **Complete Phase 2** (remaining UV migrations)
2. **Begin Phase 3** (enhance existing tests)
3. **Track metrics** (update spreadsheet weekly)

---

## Appendix: Templates Location

All templates are ready for use:

### Testing Templates:
- `/mnt/github/github/docs/testing-templates/pytest.ini.template`
- `/mnt/github/github/docs/testing-templates/pyproject.toml.pytest.template`
- `/mnt/github/github/docs/testing-templates/coveragerc.template`
- `/mnt/github/github/docs/testing-templates/conftest.py.template`
- `/mnt/github/github/docs/testing-templates/python-tests.yml.template`

### UV Templates:
- `/mnt/github/github/docs/uv-templates/uv.toml`
- `/mnt/github/github/docs/uv-templates/pyproject.toml`
- `/mnt/github/github/docs/uv-templates/.python-version`

### Documentation:
- `/mnt/github/github/docs/baseline-testing-standards.md`
- `/mnt/github/github/docs/uv-modernization-strategy.md`
- `/mnt/github/github/docs/testing-infrastructure-detailed.md`
- `/mnt/github/github/docs/uv-environment-detailed.md`

---

## Questions or Issues?

Contact the lead engineer or refer to:
- Testing Standards: `/docs/baseline-testing-standards.md`
- UV Strategy: `/docs/uv-modernization-strategy.md`
- Implementation Guide: `/docs/testing-templates/implementation-guide.md`

**This roadmap is ready for immediate implementation. All templates, tools, and documentation are in place.**