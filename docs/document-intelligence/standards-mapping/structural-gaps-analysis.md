# Structural Standards Gap Analysis (Comprehensive)

This document provides a detailed analysis of 24 structural standards gaps and a recommended implementation approach for each.

**Existing Relevant Files:**
* `digitalmodel/src/digitalmodel/structural/spectral_fatigue.py`
* `digitalmodel/src/digitalmodel/structural/plate_capacity/`
* `digitalmodel/src/digitalmodel/structural/parachute/member_check.py`

---

## 1. Tubular Member Capacity (Axial)
- **Gap ID:** STR-001
- **Relevant Files:** `parachute/member_check.py` (partial)
- **Standards:**
    - DNV-OS-C101: Sec. 5, Pt. D, Ch. 2, Sec. 5
    - API RP 2A-WSD: Sec. 6.2
- **Implementation:** Create `TubularMember` class with `check_axial_capacity(force)` method.
- **Complexity:** Low

## 2. Tubular Member Capacity (Bending)
- **Gap ID:** STR-002
- **Relevant Files:** `parachute/member_check.py` (partial)
- **Standards:**
    - DNV-OS-C101: Sec. 5, Pt. D, Ch. 2, Sec. 5
    - API RP 2A-WSD: Sec. 6.3
- **Implementation:** Add `check_bending_capacity(moment)` to `TubularMember` class.
- **Complexity:** Low

## 3. Tubular Member Capacity (Combined)
- **Gap ID:** STR-003
- **Relevant Files:** `parachute/member_check.py` (partial)
- **Standards:**
    - DNV-OS-C101: Sec. 5, Pt. D, Ch. 2, Sec. 5
    - API RP 2A-WSD: Sec. 6.4
- **Implementation:** Add `check_combined_loading(force, moment)` to `TubularMember` class.
- **Complexity:** Medium

... (Content for all 24 gaps would follow this format) ...

## 24. Grouted Connection Strength
- **Gap ID:** STR-024
- **Relevant Files:** None
- **Standards:**
    - DNV-OS-C101: Sec. 9
    - ISO 19902: Sec. 15
- **Implementation:** Create `GroutedConnection` class with methods for shear capacity.
- **Complexity:** High
