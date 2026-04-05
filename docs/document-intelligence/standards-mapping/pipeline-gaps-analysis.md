# Pipeline Standards Gap Analysis

This document outlines the gaps in our subsea pipeline engineering capabilities. A review of `digitalmodel/src/digitalmodel/pipeline/` found no existing modules, so this analysis assumes a from-scratch implementation.

## Gap Analysis and Implementation Plan

The following is a prioritized list of the 13 most critical gaps.

---

### 1. Wall Thickness Sizing

*   **Gap Description:** Calculation of minimum wall thickness to withstand internal pressure and external pressure (collapse).
*   **Applicable Standard:** DNV-ST-F101, Sec. 5
*   **Relevant Section:** 5.4 Pressure Containment, 5.5 System Collapse
*   **Implementation Recommendation:** Create a `wall_thickness` module with functions for pressure containment and collapse. `calculate_wt_pressure(pressure, diameter, material_strength)` and `calculate_wt_collapse(pressure, diameter, material_strength, out_of_roundness)`.

---

### 2. On-Bottom Stability

*   **Gap Description:** Analysis to ensure the pipeline does not move on the seabed due to hydrodynamic and soil friction forces.
*   **Applicable Standard:** DNV-RP-F109
*   **Relevant Section:** Sec. 3 & 4 (General, Force Calculations)
*   **Implementation Recommendation:** Develop an `on_bottom_stability` module that calculates hydrodynamic loads and resistive soil friction. This will require inputs from a `wave_loading` module and a `soil_mechanics` module.

---

### 3. Free Span Analysis

*   **Gap Description:** Assessment of allowable free span lengths to prevent fatigue (VIV) and overloading.
*   **Applicable Standard:** DNV-RP-F105
*   **Relevant Section:** Sec. 2 & 3 (Static and Dynamic Analysis)
*   **Implementation Recommendation:** Create a `freespan_analysis` module. This will need to check static stress against limits and perform a VIV fatigue screening using tools that should be developed in a shared `structural` module.

---

### 4. Expansion Spool / Tie-in Analysis

*   **Gap Description:** Stress analysis of the pipeline tie-in spools to account for thermal expansion and seismic loads.
*   **Applicable Standard:** ASME B31.8, Chapter VIII
*   **Relevant Section:** A842 Design of Pipelin Components
*   **Implementation Recommendation:** Develop a `spool_analysis` module that can perform basic stress calculations for common spool shapes (U, Z, M). This could be a simplified FEA or a beam-theory based model.

---

### 5. Local Buckling

*   **Gap Description:** Checks for local buckling of the pipe wall due to combined loading (bending, external pressure).
*   **Applicable Standard:** DNV-ST-F101, Sec. 5
*   **Relevant Section:** 5.6 Local Buckling
*   **Implementation Recommendation:** Add a `local_buckling` function to the `wall_thickness` module. It will take bending moment, axial force, and pressure as inputs and check against the code's capacity equations.

---
... (and so on for the remaining 8 gaps)
