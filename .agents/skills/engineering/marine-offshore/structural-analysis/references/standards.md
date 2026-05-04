# Structural Analysis — Reference Standards

Supporting detail for `../SKILL.md`. Contains full Python implementations,
material property tables, safety factor tables, complete design examples,
and the design report template.

---

## Section Properties

```python
import numpy as np
from dataclasses import dataclass
from typing import Tuple

@dataclass
class SectionProperties:
    area: float   # m²
    Ix: float     # m⁴
    Iy: float     # m⁴
    J: float      # m⁴
    Zx: float     # m³
    Zy: float     # m³
    rx: float     # m
    ry: float     # m

def circular_tube_properties(outer_diameter: float, wall_thickness: float) -> SectionProperties:
    D, t = outer_diameter, wall_thickness
    d = D - 2 * t
    A = np.pi / 4 * (D**2 - d**2)
    I = np.pi / 64 * (D**4 - d**4)
    J = np.pi / 32 * (D**4 - d**4)
    Z = I / (D / 2)
    r = np.sqrt(I / A)
    return SectionProperties(area=A, Ix=I, Iy=I, J=J, Zx=Z, Zy=Z, rx=r, ry=r)

def rectangular_tube_properties(width: float, height: float, wall_thickness: float) -> SectionProperties:
    b, h, t = width, height, wall_thickness
    bi, hi = b - 2*t, h - 2*t
    A = b*h - bi*hi
    Ix = (b*h**3 - bi*hi**3) / 12
    Iy = (h*b**3 - hi*bi**3) / 12
    J = 2*t*(b-t)**2*(h-t)**2 / (b+h-2*t)
    Zx = 2*Ix/h;  Zy = 2*Iy/b
    rx = np.sqrt(Ix/A);  ry = np.sqrt(Iy/A)
    return SectionProperties(area=A, Ix=Ix, Iy=Iy, J=J, Zx=Zx, Zy=Zy, rx=rx, ry=ry)

def i_beam_properties(flange_width, web_height, flange_thickness, web_thickness) -> SectionProperties:
    bf, hw, tf, tw = flange_width, web_height, flange_thickness, web_thickness
    h_total = hw + 2*tf
    A = 2*bf*tf + hw*tw
    Ix = (bf*h_total**3 - (bf-tw)*hw**3) / 12
    Iy = (2*tf*bf**3 + hw*tw**3) / 12
    J = (2*bf*tf**3 + hw*tw**3) / 3
    Zx = 2*Ix/h_total;  Zy = 2*Iy/bf
    rx = np.sqrt(Ix/A);  ry = np.sqrt(Iy/A)
    return SectionProperties(area=A, Ix=Ix, Iy=Iy, J=J, Zx=Zx, Zy=Zy, rx=rx, ry=ry)
```

---

## Stress Analysis

```python
@dataclass
class LoadCase:
    axial_force: float
    bending_moment_x: float
    bending_moment_y: float
    shear_force_x: float
    shear_force_y: float
    torsional_moment: float

def calculate_stresses(load: LoadCase, section: SectionProperties,
                       distance_x: float = None, distance_y: float = None) -> dict:
    sigma_axial = load.axial_force / section.area
    sigma_bending_x = (load.bending_moment_x * distance_y / section.Ix
                       if distance_y is not None
                       else abs(load.bending_moment_x) / section.Zx)
    sigma_bending_y = (load.bending_moment_y * distance_x / section.Iy
                       if distance_x is not None
                       else abs(load.bending_moment_y) / section.Zy)
    sigma_total = sigma_axial + sigma_bending_x + sigma_bending_y
    if distance_x is not None and distance_y is not None:
        r = np.sqrt(distance_x**2 + distance_y**2)
        tau_torsion = load.torsional_moment * r / section.J
    else:
        tau_torsion = load.torsional_moment / (section.J / np.sqrt(section.rx**2 + section.ry**2))
    tau_shear_x = load.shear_force_x / section.area
    tau_shear_y = load.shear_force_y / section.area
    tau_total = np.sqrt((tau_torsion + tau_shear_x)**2 + tau_shear_y**2)
    sigma_vm = np.sqrt(sigma_total**2 + 3*tau_total**2)
    return {'axial': sigma_axial, 'bending_x': sigma_bending_x,
            'bending_y': sigma_bending_y, 'normal_total': sigma_total,
            'shear_torsion': tau_torsion, 'shear_total': tau_total,
            'von_mises': sigma_vm}

def calculate_principal_stresses(sigma_x, sigma_y, tau_xy) -> Tuple[float, float, float]:
    sigma_avg = (sigma_x + sigma_y) / 2
    R = np.sqrt(((sigma_x - sigma_y)/2)**2 + tau_xy**2)
    return sigma_avg + R, sigma_avg - R, R
```

---

## Column Buckling (DNV)

```python
def dnv_column_buckling_check(axial_force, E, fy, A, I, L, K=1.0, gamma_M=1.15) -> dict:
    Le = K * L
    r = np.sqrt(I / A)
    lambda_ratio = Le / r
    lambda_bar = lambda_ratio * np.sqrt(fy / E) / np.pi
    alpha = 0.21  # Curve 'a' for welded tubulars
    phi = 0.5 * (1 + alpha*(lambda_bar - 0.2) + lambda_bar**2)
    chi = min(1.0, 1 / (phi + np.sqrt(phi**2 - lambda_bar**2)))
    N_b_Rd = chi * A * fy / gamma_M
    unity_check = axial_force / N_b_Rd
    P_cr = np.pi**2 * E * I / Le**2
    return {
        'slenderness_ratio': lambda_ratio,
        'reduced_slenderness': lambda_bar,
        'buckling_reduction_factor': chi,
        'design_resistance': N_b_Rd,
        'applied_force': axial_force,
        'unity_check': unity_check,
        'critical_load_euler': P_cr,
        'status': 'PASS' if unity_check <= 1.0 else 'FAIL'
    }
```

Effective length factors K: 0.5 (fixed-fixed), 0.7 (fixed-pinned),
1.0 (pinned-pinned), 2.0 (fixed-free).

---

## Beam Deflection

```python
def simply_supported_beam_deflection(load_type, E, I, L, load_magnitude, x=None) -> dict:
    if load_type == 'point_center':
        delta_max = load_magnitude * L**3 / (48*E*I);  x_max = L/2
    elif load_type == 'uniform':
        delta_max = 5*load_magnitude*L**4 / (384*E*I);  x_max = L/2
    elif load_type == 'point_arbitrary' and x is not None:
        a, b = x, L - x
        delta_max = load_magnitude*a**2*b**2 / (3*E*I*L);  x_max = a
    else:
        raise ValueError(f"Unknown load_type: {load_type}")
    delta_allowable = L / 360
    unity_check = delta_max / delta_allowable
    return {'max_deflection': delta_max, 'location': x_max,
            'allowable_deflection': delta_allowable,
            'unity_check': unity_check,
            'status': 'PASS' if unity_check <= 1.0 else 'FAIL'}

def cantilever_beam_deflection(load_type, E, I, L, load_magnitude) -> dict:
    if load_type == 'point_end':
        delta_max = load_magnitude*L**3 / (3*E*I)
    elif load_type == 'uniform':
        delta_max = load_magnitude*L**4 / (8*E*I)
    else:
        raise ValueError(f"Unknown load_type: {load_type}")
    delta_allowable = L / 180
    unity_check = delta_max / delta_allowable
    return {'max_deflection': delta_max, 'allowable_deflection': delta_allowable,
            'unity_check': unity_check,
            'status': 'PASS' if unity_check <= 1.0 else 'FAIL'}
```

---

## Tubular Joint Capacity (DNV-RP-C203)

```python
def tubular_joint_capacity_check(chord_diameter, chord_thickness, brace_diameter,
                                  brace_thickness, brace_angle, fy_chord, fy_brace,
                                  axial_load=0, in_plane_bending=0, out_plane_bending=0,
                                  joint_type='T') -> dict:
    D, T = chord_diameter, chord_thickness
    d, t = brace_diameter, brace_thickness
    theta = np.radians(brace_angle)
    beta = d/D;  gamma = D/(2*T);  tau = t/T

    validity_checks = {
        'beta_range': 0.2 <= beta <= 1.0,
        'gamma_range': 10 <= gamma <= 50,
        'theta_range': np.degrees(theta) >= 30
    }
    Qf = 1.0  # No chord pre-stress assumed

    if joint_type in ('T', 'Y'):
        if axial_load >= 0:
            Qu = 5.2 * gamma**(-0.2) * beta**0.5 * (1+beta)**(-0.9) * Qf
        else:
            Qu = (2.8 + 14.2*beta**2) * gamma**(-0.9) * Qf / np.sin(theta)
        N_capacity = Qu * fy_chord * T**2 / np.sin(theta)
        Qf_bend = 1.3 * gamma**(-0.4) * beta**0.2 * Qf
        M_ipb_capacity = Qf_bend * fy_chord * T**2 * d / np.sin(theta)
        M_opb_capacity = Qf_bend * fy_chord * T**2 * d
    else:
        raise NotImplementedError(f"Joint type {joint_type} not implemented")

    p = 2.0
    unity_check = (
        (abs(axial_load)/N_capacity)**p +
        (abs(in_plane_bending)/M_ipb_capacity)**p +
        (abs(out_plane_bending)/M_opb_capacity)**p
    )**(1/p)

    return {
        'beta': beta, 'gamma': gamma, 'tau': tau,
        'axial_capacity': N_capacity,
        'ipb_capacity': M_ipb_capacity,
        'opb_capacity': M_opb_capacity,
        'applied_axial': axial_load,
        'unity_check': unity_check,
        'validity_checks': validity_checks,
        'status': 'PASS' if unity_check <= 1.0 else 'FAIL'
    }
```

---

## ULS and ALS Checks

```python
def uls_combined_loading_check(axial_force, bending_moment_y, bending_moment_z,
                                fy, section: SectionProperties,
                                gamma_M=1.15, load_factors=None) -> dict:
    if load_factors is None:
        load_factors = {'axial': 1.3, 'bending': 1.3}
    Sd_axial = abs(axial_force) * load_factors['axial']
    Sd_My = abs(bending_moment_y) * load_factors['bending']
    Sd_Mz = abs(bending_moment_z) * load_factors['bending']
    N_Rd = section.area * fy / gamma_M
    My_Rd = section.Zy * fy / gamma_M
    Mz_Rd = section.Zx * fy / gamma_M
    uc_linear = Sd_axial/N_Rd + Sd_My/My_Rd + Sd_Mz/Mz_Rd
    uc_eurocode = (Sd_axial/N_Rd)**2 + (Sd_My/My_Rd + Sd_Mz/Mz_Rd)
    unity_check = max(uc_linear, uc_eurocode)
    return {
        'unity_check_linear': uc_linear,
        'unity_check_eurocode': uc_eurocode,
        'unity_check': unity_check,
        'utilization': {'axial': Sd_axial/N_Rd, 'bending_y': Sd_My/My_Rd,
                        'bending_z': Sd_Mz/Mz_Rd},
        'status': 'PASS' if unity_check <= 1.0 else 'FAIL'
    }

def als_dented_pipe_check(D, t, dent_depth, internal_pressure, fy, safety_factor=1.0) -> dict:
    delta_ratio = dent_depth / D
    if delta_ratio < 0.06:
        category = "Acceptable"
    elif delta_ratio < 0.20:
        category = "Engineering Assessment Required"
    else:
        category = "Repair/Replacement Required"
    f_dent = max(0, 1 - 5*delta_ratio)
    P_burst_intact = 2*t*fy/D
    P_burst_dented = f_dent * P_burst_intact
    P_design = internal_pressure * safety_factor
    unity_check = P_design/P_burst_dented if P_burst_dented > 0 else float('inf')
    return {
        'dent_depth_ratio': delta_ratio,
        'category': category,
        'burst_pressure_intact': P_burst_intact,
        'burst_pressure_dented': P_burst_dented,
        'reduction_factor': f_dent,
        'unity_check': unity_check,
        'status': 'PASS' if unity_check <= 1.0 else 'FAIL'
    }
```

---

## Stiffened Panel Buckling

```python
def stiffened_panel_buckling_analysis(plate_width, plate_length, plate_thickness,
                                       stiffener_spacing, stiffener_height,
                                       stiffener_thickness, applied_stress,
                                       E=210e9, nu=0.3, fy=355e6) -> dict:
    a, b, t = plate_length, stiffener_spacing, plate_thickness
    aspect_ratio = a / b
    k = 4.0 if aspect_ratio >= 1 else (1 + aspect_ratio**2)**2 / aspect_ratio**2
    sigma_cr_plate = k * np.pi**2 * E / (12*(1-nu**2)) * (t/b)**2
    panel_buckling_uc = applied_stress / sigma_cr_plate

    b_eff = min(b, 30*t*np.sqrt(E/fy))
    A_f = b_eff * t;     y_f = stiffener_height + t/2
    A_w = stiffener_height * stiffener_thickness;  y_w = stiffener_height/2
    A_total = A_f + A_w
    y_c = (A_f*y_f + A_w*y_w) / A_total
    I_f = b_eff*t**3/12 + A_f*(y_f - y_c)**2
    I_w = stiffener_thickness*stiffener_height**3/12 + A_w*(y_w - y_c)**2
    I_total = I_f + I_w
    r = np.sqrt(I_total / A_total)
    lambda_ratio = plate_length / r
    sigma_cr_column = np.pi**2 * E / lambda_ratio**2
    column_buckling_uc = applied_stress / sigma_cr_column
    overall_uc = max(panel_buckling_uc, column_buckling_uc)

    return {
        'plate_buckling_stress': sigma_cr_plate,
        'panel_buckling_uc': panel_buckling_uc,
        'column_buckling_stress': sigma_cr_column,
        'column_buckling_uc': column_buckling_uc,
        'overall_unity_check': overall_uc,
        'status': 'PASS' if overall_uc <= 1.0 else 'FAIL',
        'stiffener_properties': {'area': A_total, 'moment_of_inertia': I_total,
                                  'radius_of_gyration': r,
                                  'slenderness_ratio': lambda_ratio},
        'plate_properties': {'aspect_ratio': aspect_ratio,
                              'buckling_coefficient': k,
                              'effective_width': b_eff}
    }
```

---

## Material Properties (Standard Marine Steels)

```python
MATERIALS = {
    'S355': {'fy': 355e6, 'fu': 490e6, 'E': 210e9, 'nu': 0.3, 'density': 7850,
             'description': 'High strength structural steel (DNV-OS-B101)'},
    'S420': {'fy': 420e6, 'fu': 530e6, 'E': 210e9, 'nu': 0.3, 'density': 7850,
             'description': 'Very high strength structural steel'},
    'API 5L X65': {'fy': 448e6, 'fu': 530e6, 'E': 210e9, 'nu': 0.3, 'density': 7850,
                   'description': 'Pipeline steel grade'},
}
```

---

## Safety Factors (DNV)

```python
SAFETY_FACTORS = {
    'ULS': {'gamma_F': 1.3, 'gamma_F_variable': 1.5, 'gamma_M': 1.15},
    'ALS': {'gamma_F': 1.0, 'gamma_M': 1.0},
    'FLS': {'gamma_F': 1.0, 'gamma_Mf': 1.0},
    'SLS': {'gamma_F': 1.0, 'gamma_M': 1.0},
}
```

---

## Design Workflow

Steps for a complete member or joint design:

1. Define geometry and loads
2. Calculate section properties (`circular_tube_properties` / `i_beam_properties`)
3. ULS checks — `uls_combined_loading_check` for all load combinations
4. ALS checks — accidental scenarios (`als_dented_pipe_check` if applicable)
5. FLS checks — fatigue assessment (see `../fatigue-analysis/SKILL.md`)
6. SLS checks — deflection (`simply_supported_beam_deflection`)
7. Buckling checks — `dnv_column_buckling_check`; stiffened panels if relevant
8. Optimize if any unity check > 1.0 (increase D/t or add stiffening)
9. Generate design report (template below)

---

## Design Report Template

```markdown
# Structural Design Calculation Report

## Project Information
- Project: <name>
- Location: <location>
- Design Date: <date>
- Engineer: <name>

## Applicable Codes and Standards
- DNV-OS-C101 (ULS)
- DNV-RP-C201 (buckling)
- DNV-RP-C203 (fatigue/joints)
- <others>

## Design Criteria
- Design Life: <N> years
- ULS: γ_F = 1.3, γ_M = 1.15
- ALS: γ_F = 1.0, γ_M = 1.0
- Material: S355 / S420 / API 5L X65

## Structural Member Details
[Dimensions, section properties]

## Load Cases
[ULS, ALS, FLS combinations with factors]

## Design Checks
### ULS Combined Loading
[Unity checks per load case]

### Column Buckling
[Slenderness ratios, reduction factors, unity checks]

### Fatigue
[S-N curve, Palmgren-Miner damage, fatigue life]

### Deflection (SLS)
[Max deflection vs allowable L/360]

## Conclusions
Overall Design Status: PASS / FAIL

## Revisions
| Rev | Date | Description |
|-----|------|-------------|
| 0   | <date> | Initial issue |
```

---

## Standards List

### DNV
- **DNV-OS-C101** — Design of Offshore Steel Structures, General (LRFD)
- **DNV-RP-C201** — Buckling Strength of Plated Structures
- **DNV-RP-C203** — Fatigue Design of Offshore Steel Structures
- **DNV-RP-C205** — Environmental Conditions and Environmental Loads
- **DNV-RP-C206** — Fatigue Methodology of Offshore Ships
- **DNV-ST-0126** — Support Structures for Wind Turbines
- **DNV-OS-E301** — Position Mooring

### API
- **API RP 2A** — Planning, Designing and Constructing Fixed Offshore Platforms
- **API RP 2FPS** — Planning, Designing, and Constructing Floating Production Systems
- **API RP 2SK** — Design and Analysis of Stationkeeping Systems
- **API Spec 2B** — Fabrication of Structural Steel Pipe

### Other
- **ISO 19902** — Fixed steel offshore structures
- **Eurocode 3** — Design of steel structures (EN 1993)
- **AISC 360** — Specification for Structural Steel Buildings

### Textbooks
- Chakrabarti, S.K. (2005). *Handbook of Offshore Engineering*
- Bai, Y., Bai, Q. (2014). *Subsea Structural Engineering Handbook*
- Marshall, P.W. (1992). *Design of Welded Tubular Connections*
- Young, W.C., Budynas, R.G. (2002). *Roark's Formulas for Stress and Strain*
