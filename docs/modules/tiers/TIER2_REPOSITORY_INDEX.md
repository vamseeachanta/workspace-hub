# Tier 2 Repository Index & Deployment Status

**Assessment Date**: 2026-04-02 | **Refreshed**: 2026-04-02 | **Status**: Phase 1c Complete (Q2 Refresh)

---

## Executive Dashboard

### Readiness Summary by Category

```
┌─────────────────────────────────────────────────┐
│   TIER 2 REPOSITORIES: 12 (10 present, 2 removed) │
├─────────────────────────────────────────────────┤
│ 🟢 HIGH READINESS (80%+):   6 repos - Ready   │
│ 🟡 MEDIUM READINESS (70-79%): 4 repos - Some  │
│ 🔴 LOW READINESS (<70%):    2 repos - Investig│
├─────────────────────────────────────────────────┤
│ Overall Readiness: 78% ✅                      │
│ Est. Deployment Time: 30 calendar days         │
│ Total Effort: ~52 hours of configuration       │
└─────────────────────────────────────────────────┘
```

---

## Complete Repository Inventory

### 1. Energy ⚠️ REMOVED

```
Repo:              energy
Status:            ❌ Directory no longer present in workspace-hub (as of 2026-04-02)
Notes:             Energy domain data now consolidated under worldenergydata
```

---

### 2. Rock-Oil-Field

```
Repo:              rock-oil-field
Category:          Work (Tier 2)
Current Branch:    main ✅
Repository Size:   5.2 GB
Python Version:    3.9+
Test Files:        0 ❌
pyproject.toml:    ✅ Present
pytest.ini:        ❌ Missing
Readiness:         75% 🟡 MEDIUM
Priority:          7
Est. Deploy Time:  4-5 days
Status:            NO TESTS - requires bootstrap
Deployment Ready:  YES (Phase 3 - after high priority)
```

**Deployment Details:**
- Python files: 56
- Project name: "rock-oil-field"
- Key dependencies: gitpython, python-certifi-win32
- Special notes: No tests, will need business logic analysis
- Risk: Medium - requires test scaffolding

---

### 3. Frontierdeepwater

```
Repo:              frontierdeepwater
Category:          Work (Tier 1 candidate)
Current Branch:    main ✅
Repository Size:   490 MB ⭐ (SMALLEST WORK)
Python Version:    3.9+
Test Files:        1 (test_smoke.py) ✅
pyproject.toml:    ✅ Present
pytest.ini:        ⚠️ Partial (pyproject.toml config)
Readiness:         85% 🟢 HIGH
Priority:          3
Est. Deploy Time:  2-3 days
Status:            Production-critical, well-structured
Deployment Ready:  YES (Phase 2)
```

**Deployment Details:**
- Python files: 61
- Project name: "frontierdeepwater"
- Key dependencies: gitpython, python-certifi-win32
- Special notes: Marine engineering domain, smallest work repo
- Production status: YES - use with care

---

### 4. Seanation

```
Repo:              seanation
Category:          Work (Tier 2)
Current Branch:    main ✅
Repository Size:   1.5 GB
Python Version:    3.9+
Test Files:        1 (test_smoke.py) ✅
pyproject.toml:    ✅ Present
pytest.ini:        ⚠️ Partial (pyproject.toml config)
Readiness:         85% 🟢 HIGH
Priority:          5
Est. Deploy Time:  2-3 days
Status:            Domain-specific (drilling), smoke test exists
Deployment Ready:  YES (Phase 2)
```

**Deployment Details:**
- Python files: 62
- Project name: "seanation"
- Key dependencies: gitpython, python-certifi-win32
- Special notes: Drilling-specific domain (0122_ct_drilling directory)
- Risk: Low - specialized domain but structured

---

### 5. Doris

```
Repo:              doris
Category:          Work (Tier 2)
Current Branch:    main ✅
Repository Size:   521 MB
Python Version:    3.9+
Test Files:        1 (test_smoke.py) ✅
pyproject.toml:    ✅ Present
pytest.ini:        ⚠️ Partial (pyproject.toml config)
Readiness:         85% 🟢 HIGH
Priority:          6
Est. Deploy Time:  2-3 days
Status:            Good candidate, moderate size, smoke test exists
Deployment Ready:  YES (Phase 2)
```

**Deployment Details:**
- Python files: 48
- Project name: "doris"
- Key dependencies: gitpython, python-certifi-win32
- Special notes: Marine domain, has documentation (charlie.md)
- Risk: Low - well-organized structure

---

### 6. Saipem

```
Repo:              saipem
Category:          Work (Tier 2)
Current Branch:    main ✅
Repository Size:   4.1 GB
Python Version:    3.9+
Test Files:        0 ❌
pyproject.toml:    ✅ Present
pytest.ini:        ❌ Missing
Readiness:         75% 🟡 MEDIUM
Priority:          8
Est. Deploy Time:  4-5 days
Status:            NO TESTS - requires bootstrap
Deployment Ready:  YES (Phase 3 - after high priority)
```

**Deployment Details:**
- Python files: 59
- Project name: "saipem"
- Key dependencies: gitpython, python-certifi-win32
- Special notes: Construction/engineering company domain
- Risk: Medium - no tests, large codebase, business logic needed

---

### 7. OGManufacturing ⚠️

```
Repo:              OGManufacturing
Category:          Mixed (Tier 3)
Current Branch:    main ✅
Repository Size:   2.4 GB
Python Version:    3.9+
Test Files:        0 ❌
pyproject.toml:    ✅ Present
pytest.ini:        ⚠️ Partial (pyproject.toml config)
Readiness:         70% 🔴 NEEDS INVESTIGATION
Priority:          11
Est. Deploy Time:  5-7 days
Status:            🚩 META-REPOSITORY - contains submodule references
Deployment Ready:  NO - Requires architecture investigation first
```

**Deployment Details:**
- Python files: 56
- Project name: "OGManufacturing"
- Key dependencies: gitpython, python-certifi-win32
- ⚠️ SPECIAL ISSUE: Contains references to multiple repositories:
  - aceengineer-admin, aceengineercode, aceengineer-website
  - achantas-data, achantas-media, acma-projects
  - ai-native-traditional-eng, assethold, assetutilities
  - and others
- Risk: High - unclear project boundaries, submodule complications

---

### 8. Aceengineer-Website ⚠️

```
Repo:              aceengineer-website
Category:          Personal (Tier 1 active)
Current Branch:    flask-backup ⚠️ (NOT main)
Repository Size:   281 MB
Python Version:    3.9+
Test Files:        0 ❌
pyproject.toml:    ✅ Present
pytest.ini:        ❌ Missing
Readiness:         65% 🟡 MEDIUM
Priority:          9
Est. Deploy Time:  3-4 days
Status:            Flask web app, on non-main branch
Deployment Ready:  CONDITIONAL - Must resolve branch issue first
```

**Deployment Details:**
- Python files: 73
- Project name: "aceengineer-website"
- Key dependencies: gitpython, python-certifi-win32
- ⚠️ CRITICAL ISSUE: Currently on flask-backup branch, not main
- Special notes: Flask web application, HTML files present
- Risk: Medium - branch mismatch, web app testing complexity

**Action Required**: Confirm intended branch before deployment

---

### 9. Aceengineer-Admin

```
Repo:              aceengineer-admin
Category:          Personal (Tier 1 active)
Current Branch:    main ✅
Repository Size:   821 MB
Python Version:    3.9+
Test Files:        0 ❌
pyproject.toml:    ✅ Present (+ setup.py)
pytest.ini:        ❌ Missing
Readiness:         70% 🟡 MEDIUM
Priority:          10
Est. Deploy Time:  3-4 days
Status:            Office automation, complex domain
Deployment Ready:  YES (Phase 3)
```

**Deployment Details:**
- Python files: 85
- Project name: "aceengineer-automation" (not admin)
- Key dependencies: python-docx>=0.8.11, python-dateutil>=2.8.0, gitpython
- Special notes: Uses python-docx (Word manipulation), has Excel/docx files
- Risk: Medium - office automation domain, complex testing needed

---

### 10. AI-Native-Traditional-Eng ⚠️ REMOVED

```
Repo:              ai-native-traditional-eng
Status:            ❌ Directory no longer present in workspace-hub (as of 2026-04-02)
Notes:             Content likely merged into digitalmodel or docs/modules/ai-native/
```

---

### 11. Client_Projects 🚩

```
Repo:              client_projects
Category:          Mixed (Tier 3)
Current Branch:    main ✅
Repository Size:   13 GB 🚩 (LARGEST - REQUIRES CARE)
Python Version:    3.9+
Test Files:        0 ❌
pyproject.toml:    ✅ Present
pytest.ini:        ⚠️ Partial (pyproject.toml config)
Readiness:         65% 🔴 NEEDS INVESTIGATION
Priority:          12
Est. Deploy Time:  6-8 days
Status:            Multi-project aggregate, complex
Deployment Ready:  NO - Requires architecture clarity first
```

**Deployment Details:**
- Python files: 106 (most of any repo)
- Project name: "client_projects"
- Key dependencies: gitpython, python-certifi-win32
- 🚩 SPECIAL ISSUES:
  - LARGEST repository (13 GB)
  - Contains multiple client projects:
    - 2019 OTC
    - 9016 O&G Website Dev
    - Azure IoT Training
  - Has ci-cd directory (DevOps focus)
- Risk: High - unclear project boundaries, selective testing needed

**Action Required**: Clarify project structure before deployment

---

### 12. Pyproject-Starter

```
Repo:              pyproject-starter
Category:          Reference (Tier 3)
Current Branch:    main ✅
Repository Size:   7.7 MB ⭐ (SMALLEST - TEMPLATE)
Python Version:    3.9+
Test Files:        2 ✅✅ (test_calculation.py, test_main.py)
pyproject.toml:    ✅ Present (+ setup.py)
pytest.ini:        ❌ Missing
Readiness:         90% 🟢 EXCELLENT
Priority:          1
Est. Deploy Time:  1 day ✨ FASTEST & BEST
Status:            REFERENCE IMPLEMENTATION - Already has tests!
Deployment Ready:  YES (Phase 1 - FIRST)
```

**Deployment Details:**
- Python files: 51
- Project name: "pyproject-starter"
- Key dependencies: gitpython, python-certifi-win32
- Special notes: Template/reference repository
- Already has 2 test files (best prepared)
- Clean structure ideal for establishing patterns
- Risk: Low - reference implementation, already configured

---

## Deployment Phasing

### Phase 1: Pilot & Validation (Days 1-2)

| Order | Repository | Time | Reason |
|-------|-----------|------|--------|
| 1️⃣ | pyproject-starter | 1 day | Reference, has tests |
| ~~2️⃣~~ | ~~ai-native-traditional-eng~~ | — | ⚠️ REMOVED from workspace (as of 2026-04-02) |

**Pilot Objectives:**
- Establish testing patterns
- Validate configuration templates
- Document best practices
- Prepare for rollout

---

### Phase 2: High Priority Rollout (Days 3-8)

| Order | Repository | Time | Reason |
|-------|-----------|------|--------|
| 3️⃣ | frontierdeepwater | 2-3 days | Production-critical |
| ~~4️⃣~~ | ~~energy~~ | — | ⚠️ REMOVED; consolidated into worldenergydata (as of 2026-04-02) |
| 5️⃣ | seanation | 2-3 days | Domain-specific |
| 6️⃣ | doris | 2-3 days | Consolidation test |

**Phase 2 Objectives:**
- Deploy to high-readiness repos
- Validate patterns across domains
- Generate baseline coverage metrics
- Build momentum

---

### Phase 3: Medium Priority & Gaps (Days 9-22)

| Order | Repository | Time | Reason |
|-------|-----------|------|--------|
| 7️⃣ | rock-oil-field | 4-5 days | No tests, needs bootstrap |
| 8️⃣ | saipem | 4-5 days | No tests, large |
| 9️⃣ | aceengineer-website | 3-4 days | Web app, branch issue |
| 🔟 | aceengineer-admin | 3-4 days | Office automation |

**Phase 3 Objectives:**
- Address test bootstrap needs
- Handle special cases
- Complete medium-readiness repos
- Build comprehensive coverage

---

### Phase 4: Investigation & Complex Cases (Days 25+)

| Order | Repository | Time | Action Required |
|-------|-----------|------|-----------------|
| 1️⃣1️⃣ | OGManufacturing | 5-7 days | Investigate meta-repo structure 🚩 |
| 1️⃣2️⃣ | client_projects | 6-8 days | Clarify multi-project boundaries 🚩 |

**Phase 4 Objectives:**
- Resolve architectural questions
- Define testing strategy for complex repos
- Plan selective test coverage
- Complete rollout

---

## Summary Statistics

### Repository Metrics

| Metric | Value |
|--------|-------|
| Total Repositories | 12 (10 present, 2 removed) |
| Total Size | ~58.7 GB |
| Average Size | 4.9 GB |
| Total Python Files | ~768 |
| Average Python Files/Repo | 64 |
| Repos with Tests | 5/12 (42%) |
| Total Test Files | 5 |
| Average Tests/Repo | 0.4 |

### Readiness Breakdown

| Readiness | Count | Percentage |
|-----------|-------|-----------|
| 🟢 High (80%+) | 6 | 50% |
| 🟡 Medium (70-79%) | 4 | 33% |
| 🔴 Low (<70%) | 2 | 17% |

### Python Version

| Version | Repos |
|---------|-------|
| 3.9+ | 12/12 |

---

## Configuration Requirements (TO BE DEPLOYED)

### Per Repository (×10 active)
- ✅ pytest.ini - 30 min
- ✅ .coveragerc - 30 min
- ✅ tests/conftest.py - 1 hour
- ✅ .github/workflows/test.yml - 1 hour

### Total Configuration Time: ~43 hours (adjusted for 10 active repos)

---

## Risk Matrix

| Repo | Risk Level | Reason | Mitigation |
|------|-----------|--------|-----------|
| OGManufacturing | 🔴 HIGH | Meta-repo, unclear structure | Investigate first |
| client_projects | 🔴 HIGH | Multi-project, 13 GB | Clarify boundaries |
| rock-oil-field | 🟡 MEDIUM | No tests, large | Bootstrap tests |
| saipem | 🟡 MEDIUM | No tests, large | Domain analysis |
| aceengineer-website | 🟡 MEDIUM | Branch mismatch, web app | Fix branch first |
| aceengineer-admin | 🟡 MEDIUM | No tests, automation | Business logic review |
| All others | 🟢 LOW | Smoke tests exist | Standard deployment |

---

## Next Steps (AWAITING APPROVAL)

### When Approved, Execute:

```bash
# 1. Pilot Phase (Priority: IMMEDIATE)
./deploy_tier2_pilot.sh

# 2. High Priority Rollout (After pilot success)
./deploy_tier2_phase2.sh

# 3. Medium Priority (After phase 2)
./deploy_tier2_phase3.sh

# 4. Investigation & Complex (After phase 3)
./investigate_tier2_special.sh
```

---

## Status Indicators

**Current Status: ASSESSMENT COMPLETE ✅ (Q2 2026 Refresh)**
- All 12 repositories assessed (10 active, 2 removed from workspace)
- Individual plans prepared
- Risk analysis complete
- Timeline established (adjusted for 10 active repos)
- Awaiting approval

**Next Status: PILOT DEPLOYMENT** (when approved)

---

**Document**: Tier 2 Repository Index
**Date**: 2026-04-02
**Phase**: 1c Assessment Complete
**Note**: 2 repos (energy, ai-native-traditional-eng) removed from workspace since original assessment

---

## Related Documents

- Full Assessment: `docs/TIER2_ASSESSMENT_DEPLOYMENT_PLAN.md`
- Quick Reference: `docs/TIER2_QUICK_REFERENCE.md`
- Phase 1 Baseline: `docs/modules/testing/baseline-testing-standards.md`

