#!/usr/bin/env python3
"""fluids library evaluation for issue #1450.

Tests:
1. Module listing and version
2. Friction factor validation against Moody chart values
3. Crane TP-410 fittings K-factors
4. API 520 relief valve sizing
5. Compressible flow
"""

import sys
import json

results = {}

# 1. Version and modules
try:
    import fluids
    results['version'] = fluids.__version__
    results['modules'] = [
        'friction', 'fittings', 'piping', 'safety_valve',
        'compressible', 'two_phase', 'open_flow', 'control_valve',
        'flow_meter', 'pump', 'atmosphere', 'packed_bed',
        'filters', 'geometry', 'separator', 'core',
    ]
    # Check which modules actually exist
    available = []
    for mod in results['modules']:
        try:
            __import__(f'fluids.{mod}')
            available.append(mod)
        except ImportError:
            pass
    results['available_modules'] = available
except Exception as e:
    results['import_error'] = str(e)
    print(json.dumps(results, indent=2))
    sys.exit(1)

# 2. Friction factor validation (Moody chart reference values)
# Colebrook equation for fully turbulent flow
# Reference: Re=1e5, roughness/D=0.001 -> f ≈ 0.02219 (Moody chart)
try:
    from fluids.friction import friction_factor

    ff_tests = []

    # Test case 1: Re=1e5, eD=0.001
    f1 = friction_factor(Re=1e5, eD=0.001)
    ff_tests.append({
        'case': 'Re=1e5, eD=0.001',
        'computed': round(f1, 6),
        'moody_ref': 0.02219,
        'error_pct': round(abs(f1 - 0.02219) / 0.02219 * 100, 3)
    })

    # Test case 2: Re=1e6, eD=0.0001 -> f ≈ 0.01350
    f2 = friction_factor(Re=1e6, eD=0.0001)
    ff_tests.append({
        'case': 'Re=1e6, eD=0.0001',
        'computed': round(f2, 6),
        'moody_ref': 0.01350,
        'error_pct': round(abs(f2 - 0.01350) / 0.01350 * 100, 3)
    })

    # Test case 3: Laminar flow Re=1000 -> f = 64/Re = 0.064
    f3 = friction_factor(Re=1000, eD=0.0)
    ff_tests.append({
        'case': 'Re=1000 (laminar)',
        'computed': round(f3, 6),
        'moody_ref': 0.064,
        'error_pct': round(abs(f3 - 0.064) / 0.064 * 100, 3)
    })

    # Test case 4: Re=4000, eD=0.0 (smooth pipe, transition) -> f ≈ 0.0399
    f4 = friction_factor(Re=4000, eD=0.0)
    ff_tests.append({
        'case': 'Re=4000, smooth',
        'computed': round(f4, 6),
        'moody_ref': 0.0399,
        'error_pct': round(abs(f4 - 0.0399) / 0.0399 * 100, 3)
    })

    results['friction_factor_tests'] = ff_tests
except Exception as e:
    results['friction_error'] = str(e)

# 3. Crane TP-410 fittings
try:
    from fluids.fittings import bend_rounded, K_from_f, entrance_sharp, exit_normal

    fittings_tests = []

    # 90-degree bend, r/D=1.5
    K_bend = bend_rounded(Di=0.1, angle=90, rc=0.15)
    fittings_tests.append({
        'case': '90-deg rounded bend r/D=1.5, Di=0.1m',
        'K_computed': round(K_bend, 4)
    })

    # Sharp entrance
    K_ent = entrance_sharp()
    fittings_tests.append({
        'case': 'Sharp entrance',
        'K_computed': round(K_ent, 4),
        'expected': 0.5,
        'matches': abs(K_ent - 0.5) < 0.01
    })

    # Normal exit
    K_exit = exit_normal()
    fittings_tests.append({
        'case': 'Normal exit',
        'K_computed': round(K_exit, 4),
        'expected': 1.0,
        'matches': abs(K_exit - 1.0) < 0.01
    })

    results['fittings_tests'] = fittings_tests
except Exception as e:
    results['fittings_error'] = str(e)

# 4. API 520 relief valve sizing
try:
    from fluids.safety_valve import API520_A_g, API520_A_steam

    rv_tests = []

    # Gas relief valve sizing
    # Typical example: air at 1 MPa set pressure, 10% overpressure
    A_gas = API520_A_g(
        m=1.0,           # mass flow rate kg/s
        T=348.15,        # temperature K (75°C)
        Z=1.0,           # compressibility
        MW=28.97,        # air molecular weight
        k=1.4,           # Cp/Cv ratio
        P1=1.1e6,        # relieving pressure Pa
        Kb=1.0,          # backpressure correction
        Kd=0.975,        # discharge coefficient
        Kc=1.0           # combination correction
    )
    rv_tests.append({
        'case': 'API 520 gas (air, 1 MPa, 1 kg/s)',
        'area_m2': round(A_gas, 8),
        'area_mm2': round(A_gas * 1e6, 2)
    })

    # Steam relief valve
    A_steam = API520_A_steam(
        m=1.0,           # mass flow rate kg/s
        T=473.15,        # temperature K (200°C)
        P1=1.1e6,        # relieving pressure Pa
        Kd=0.975,
        Kb=1.0,
        Kc=1.0
    )
    rv_tests.append({
        'case': 'API 520 steam (200°C, 1.1 MPa, 1 kg/s)',
        'area_m2': round(A_steam, 8),
        'area_mm2': round(A_steam * 1e6, 2)
    })

    results['relief_valve_tests'] = rv_tests
except Exception as e:
    results['relief_valve_error'] = str(e)

# 5. Compressible flow
try:
    from fluids.compressible import isothermal_gas

    comp_tests = []

    # Isothermal gas flow in a pipe
    # 100m pipe, 0.1m diameter, air
    flow = isothermal_gas(
        rho=10.0,        # density kg/m3
        fd=0.02,         # friction factor
        P1=1e6,          # upstream pressure Pa
        P2=9e5,          # downstream pressure Pa
        L=100.0,         # length m
        D=0.1            # diameter m
    )
    comp_tests.append({
        'case': 'Isothermal gas flow (100m, 0.1m pipe, 1MPa->0.9MPa)',
        'mass_flow_kg_s': round(flow, 4)
    })

    results['compressible_tests'] = comp_tests
except Exception as e:
    results['compressible_error'] = str(e)

# 6. Pipe schedule data
try:
    from fluids.piping import nearest_pipe

    pipe_tests = []

    # Get nearest standard pipe for 100mm target
    nps, Di, Do, t = nearest_pipe(Di=0.1)
    pipe_tests.append({
        'case': 'Nearest pipe to Di=100mm',
        'NPS': nps,
        'Di_mm': round(Di * 1000, 2),
        'Do_mm': round(Do * 1000, 2),
        't_mm': round(t * 1000, 2)
    })

    results['piping_tests'] = pipe_tests
except Exception as e:
    results['piping_error'] = str(e)

print(json.dumps(results, indent=2))
