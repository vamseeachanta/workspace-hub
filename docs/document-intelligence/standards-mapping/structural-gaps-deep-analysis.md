# Structural Standards Gaps — Deep Analysis & Implementation Recommendations

Generated: Overnight batch — 2026-04-06
Analyzes 24 structural standards gaps identified in existing gap analysis.
Maps to DNV-OS-C101, API RP 2A-WSD, ISO 19902, NORSOK N-004.

## Gap Inventory by Category

### Category A: Member Capacity (STR-001 through STR-008)
These 8 gaps cover individual member capacity checks. All are LOW-MEDIUM complexity.
Priority: HIGH — foundation for all structural checks.

| Gap | Check | Standard | Complexity | Effort |
|-----|-------|----------|------------|--------|
| STR-001 | Axial tension | DNV-OS-C101 Sec 5 | Low | 1-2 hrs |
| STR-002 | Axial compression | DNV-OS-C101 Sec 5 | Low | 1-2 hrs |
| STR-003 | Bending | DNV-OS-C101 Sec 5 | Low | 1-2 hrs |
| STR-004 | Shear | DNV-OS-C101 Sec 5 | Low | 1 hr |
| STR-005 | Torsion | DNV-OS-C101 Sec 5 | Low | 1 hr |
| STR-006 | Combined axial+bending | DNV-OS-C101 Sec 5 | Medium | 2-3 hrs |
| STR-007 | Combined all loads | DNV-OS-C101 Sec 5 | Medium | 2-3 hrs |
| STR-008 | Local buckling | DNV-OS-C101 Sec 7 | Medium | 3-4 hrs |

Implementation skeleton:
```
class TubularMemberCheck:
    - check_axial_tension(N_ed, A, fy, gamma_M) -> UtilizationCheck
    - check_axial_compression(N_ed, A, fy, kappa, gamma_M) -> UtilizationCheck
    - check_bending(M_ed, W, fy, gamma_M) -> UtilizationCheck
    - check_shear(V_ed, A_v, fy, gamma_M) -> UtilizationCheck
    - check_torsion(T_ed, W_t, fy, gamma_M) -> UtilizationCheck
    - check_combined(N_ed, M_ed, V_ed, ...) -> UtilizationCheck
    - check_local_buckling(D, t, fy) -> UtilizationCheck
```

### Category B: Tubular Joint Capacity (STR-009 through STR-014)
These 6 gaps cover K-, T-, Y-, X-joint capacity checks per API RP 2A-WSD Sec 4.7.
Priority: HIGH — joint failure is the dominant fatigue/failure mode.

| Gap | Check | Standard | Complexity | Effort |
|-----|-------|----------|------------|--------|
| STR-009 | K-joint axial | API RP 2A-WSD Sec 4.3 | Medium | 3-4 hrs |
| STR-010 | K-joint bending | API RP 2A-WSD Sec 4.3 | Medium | 3-4 hrs |
| STR-011 | T/Y-joint axial | API RP 2A-WSD Sec 4.3 | Medium | 3-4 hrs |
| STR-012 | X-joint | API RP 2A-WSD Sec 4.3 | Medium | 3-4 hrs |
| STR-013 | Joint punch shear | API RP 2A-WSD Sec 4.3 | High | 4-6 hrs |
| STR-014 | Joint chord plastification | API RP 2A-WSD Sec 4.3 | High | 4-6 hrs |

### Category C: Global Stability (STR-015 through STR-018)
These 4 gaps cover frame-level buckling and stability.
Priority: MEDIUM — depends on structural analysis results.

| Gap | Check | Standard | Complexity | Effort |
|-----|-------|----------|------------|--------|
| STR-015 | Column buckling (global) | DNV-OS-C101 Sec 7 | Medium | 3-4 hrs |
| STR-016 | Frame buckling | DNV-OS-C101 Sec 7 | High | 4-6 hrs |
| STR-017 | Lateral torsional buckling | DNV-OS-C101 Sec 7 | High | 4-6 hrs |
| STR-018 | Progressive collapse | API RP 2A-WSD Sec 4.3.8 | High | 6-8 hrs |

### Category D: Foundation & Soil (STR-019 through STR-021)
These 3 gaps interface with the geotechnical module.
Priority: MEDIUM — shared dependency with geotechnical module.

| Gap | Check | Standard | Complexity | Effort |
|-----|-------|----------|------------|--------|
| STR-019 | Pile capacity | API RP 2GEO Sec 9 | Medium | 3-4 hrs |
| STR-020 | Mudmat capacity | DNV-RP-C212 Sec 2 | Medium | 2-3 hrs |
| STR-021 | Skirt foundation | API RP 2GEO Sec 9 | Medium | 3-4 hrs |

### Category E: Specialized Connections (STR-022 through STR-024)
These 3 gaps cover connection types not in standard member checks.
Priority: LOW-MEDIUM — specialized applications.

| Gap | Check | Standard | Complexity | Effort |
|-----|-------|----------|------------|--------|
| STR-022 | Flange connection | DNV-OS-C101 Sec 8 | Medium | 3-4 hrs |
| STR-023 | Bolted connection | DNV-OS-C101 Sec 8 / AISC 360 | Medium | 3-4 hrs |
| STR-024 | Grouted connection | DNV-OS-C101 Sec 9 / ISO 19902 Sec 15 | High | 4-6 hrs |

## Implementation Order

### Phase 1: Member Capacity (Week 1-2)
1. Implement STR-001 through STR-004 (axial, bending, shear, torsion)
2. Add comprehensive unit tests with analytical verification
3. Implement STR-005 through STR-008 (combined, local buckling)
4. Verify against DNV OS-C101 worked examples

### Phase 2: Joint Capacity (Week 3-4)
1. Implement STR-009 through STR-012 (K, T/Y, X joints)
2. Implement STR-013 through STR-014 (punch shear, chord plastification)
3. Validate against API RP 2A-WSD example problems
4. Create joint interaction diagrams

### Phase 3: Global Stability + Foundations (Week 5-6)
1. Implement STR-015 through STR-018 (buckling, stability)
2. Implement STR-019 through STR-021 (foundations)
3. Link with existing geotechnical module

### Phase 4: Specialized Connections (Week 7-8)
1. Implement STR-022 through STR-024 (flanges, bolts, grouted)
2. Full integration testing with member + joint modules
3. Documentation and API specification

## Cross-Module Dependencies
- fatigue/sn_curves.py → structural member stress output
- hydrodynamics/ → environmental loading inputs
- geotechnical/ → foundation capacity data
- asset_integrity/ → remaining life assessment
- orcaflex/ → structural input models

## Total Effort Estimate
- Phase 1: 12-16 hours (8 gaps)
- Phase 2: 26-36 hours (6 gaps)
- Phase 3: 16-24 hours (6 gaps)
- Phase 4: 10-14 hours (4 gaps)
- Total: 64-90 hours across 4 phases
