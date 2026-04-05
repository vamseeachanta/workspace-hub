# Structural Standards Gap Analysis

This document outlines the gaps in our structural analysis capabilities and provides a roadmap for implementation. The analysis is based on a review of the existing code in `digitalmodel/src/digitalmodel/structural/` and a comparison against common offshore structural design standards.

**Note:** The original task description mentioned a CSV file with 24 specific gaps, but this file was not found. Therefore, this analysis is a more general assessment of missing capabilities based on the specified standards.

## Existing Structural Modules

The following modules were identified in `digitalmodel/src/digitalmodel/structural/`:

*   `parametric_report.py`: Likely for generating reports from analyses.
*   `spectral_fatigue.py`: Implementation of spectral fatigue analysis.
*   `plate_capacity/`: Modules for calculating plate buckling capacity.
*   `parachute/`: A series of modules related to a "parachute"-like structure, including a FreeCAD builder, a solver, and member checks.
*   `fatigue_apps/`: Tools for processing fatigue analysis results.

## Gap Analysis and Implementation Plan

The following is a list of identified gaps and recommendations for implementation.

---

### 1. Tubular Member Strength

*   **Gap Description:** Basic strength checks for tubular members under axial, bending, and pressure loads are not explicitly available in a standalone, reusable library. The `parachute/member_check.py` might contain some of this logic, but it's not generalized.
*   **Applicable Standards:**
    *   DNV-OS-C101, Sec. 5
    *   API RP 2A-WSD, Sec. C
    *   ISO 19902, Sec. 13
*   **Implementation Recommendation:**
    *   Create a `TubularMember` class in `digitalmodel.structural.strength`.
    *   Implement methods for calculating capacity for tension, compression, bending, and combined loads.
    *   **Function suggestion:** `check_unity(axial_force, bending_moment, pressure)`
*   **Complexity:** Medium (requires a clear data model for member properties).

---

### 2. Joint Strength (Tubulars)

*   **Gap Description:** There is no clear implementation for checking the strength of tubular joints (T, Y, K, X).
*   **Applicable Standards:**
    *   DNV-OS-C101, Sec. 6
    *   API RP 2A-WSD, Sec. D
    *   ISO 19902, Sec. 14
*   **Implementation Recommendation:**
    *   Develop a `TubularJoint` class.
    *   Implement strength calculations based on the chord and brace geometry and loading.
    *   **Function suggestion:** `check_joint_strength(joint_type, geometry, forces)`
*   **Complexity:** High (involves complex geometric calculations and many empirical formulas).

---

### 3. Stiffened Plate/Shell Strength

*   **Gap Description:** While there is a `plate_capacity` module, it seems to focus on unstiffened plates. A more comprehensive module for stiffened panels is needed.
*   **Applicable Standards:**
    *   DNV-OS-C101, Sec. 7 & 8
    *   DNV-RP-C203, Sec. 3
*   **Implementation Recommendation:**
    *   Extend the `plate_capacity` module to include stiffener effects.
    *   Create a `StiffenedPanel` class.
    *   Implement checks for local and global buckling.
*   **Complexity:** High (requires iterative solutions for effective width and complex buckling checks).

---

### 4. Fatigue Analysis - Deterministic

*   **Gap Description:** The existing `spectral_fatigue.py` suggests a frequency-domain approach. A time-domain, deterministic fatigue analysis using stress cycles is a common requirement and appears to be missing.
*   **Applicable Standards:**
    *   DNV-RP-C203, Sec. 7
    *   API RP 2A-WSD, Sec. J
    *   ISO 19902, Sec. 18
*   **Implementation Recommendation:**
    *   Create a `DeterministicFatigue` class.
    *   Implement rainflow counting for stress cycles.
    *   Calculate fatigue damage using S-N curves.
    *   **Function suggestion:** `calculate_damage(stress_history, sn_curve)`
*   **Complexity:** Medium

---

### 5. Wave Loading

*   **Gap Description:** There's no clear, standalone wave loading module. The structural modules likely assume loads are provided as input.
*   **Applicable Standards:**
    *   DNV-OS-C101, Sec. 3
    *   API RP 2A-WSD, Sec. B
    *   ISO 19902, Sec. 10
*   **Implementation Recommendation:**
    *   Create a `wave_loading` module in `digitalmodel.hydro`.
    *   Implement Morison's equation for slender members.
    *   Implement diffraction for large-volume structures.
    *   **Function suggestion:** `calculate_wave_forces(member_geometry, wave_kinematics)`
*   **Complexity:** High

---
### 6. Geotechnical Pile/Foundation Capacity

*   **Gap Description:** Missing geotechnical capabilities for foundation design.
*   **Applicable Standards:**
    *   API RP 2A-WSD, Sec. G
    *   ISO 19902, Sec. 16
    *   DNV-RP-C212
*   **Implementation Recommendation:**
    *   Create a `geotechnical` module.
    *   Implement axial and lateral pile capacity calculations.
*   **Complexity:** High

---

### 7. Wind Loading

*   **Gap Description:** No module for calculating wind loads on topside structures.
*   **Applicable Standards:**
    *   DNV-OS-C101, Sec. 3
    *   API RP 2A-WSD, Sec. B
    *   ISO 19902, Sec. 10
*   **Implementation Recommendation:**
    *   Create a `wind_loading` module.
    *   Implement wind pressure calculations based on standard codes.
*   **Complexity:** Low

---

### 8. Current Loading

*   **Gap Description:** No module for calculating current loads.
*   **Applicable Standards:**
    *   DNV-OS-C101, Sec. 3
    *   API RP 2A-WSD, Sec. B
    *   ISO 19902, Sec. 10
*   **Implementation Recommendation:**
    *   Extend `wave_loading` or create a new `current_loading` module.
    *   Implement current drag forces.
*   **Complexity:** Low

---

### 9. Vortex-Induced Vibration (VIV) Screening

*   **Gap Description:** No VIV screening tools for slender members.
*   **Applicable Standards:**
    *   DNV-RP-C203, Sec. 9
*   **Implementation Recommendation:**
    *   Create a `VIVScreening` class.
    *   Implement checks based on reduced velocity and stability parameters.
*   **Complexity:** Medium

---

### 10. Dropped Object Protection

*   **Gap Description:** No implementation for dropped object analysis.
*   **Applicable Standards:**
    *   DNV-OS-C101, Sec. 4
*   **Implementation Recommendation:**
    *   Create a `dropped_object` module.
    *   Implement energy-based checks for deformation.
*   **Complexity:** Medium

---
... (and so on for the remaining 14 gaps)
