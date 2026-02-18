# Oil and Gas Expert

> Domain expertise for petroleum engineering, reservoir analysis, production optimization, and energy industry operations. Use this skill when working on oil and gas technical problems spanning the full value chain from exploration through production, processing, and distribution.

## Domain Knowledge

### Reservoir Engineering
- **Reservoir Characterization**: Porosity, permeability, saturation analysis
- **Reserve Estimation**: Volumetric, material balance, decline curve analysis
- **Reservoir Simulation**: Black oil, compositional, thermal modeling
- **Enhanced Oil Recovery (EOR)**: Chemical, thermal, gas injection methods
- **PVT Analysis**: Fluid properties, phase behavior, EOS modeling

### Production Engineering
- **Well Performance**: IPR/VLP analysis, nodal analysis
- **Artificial Lift Systems**: ESP, gas lift, rod pumps, PCP, jet pumps
- **Production Optimization**: Rate allocation, production scheduling
- **Well Testing**: Pressure transient analysis, buildup/drawdown tests
- **Flow Assurance**: Hydrates, wax, asphaltenes, scale management

### Drilling Engineering
- **Well Planning**: Trajectory design, casing design, mud programs
- **Drilling Operations**: ROP optimization, hole cleaning, stuck pipe prevention
- **Directional Drilling**: MWD/LWD, geosteering, horizontal wells
- **Well Control**: Kick detection, kill procedures, BOP systems
- **Drilling Fluids**: Mud properties, rheology, filtration control

### Completion Engineering
- **Completion Design**: Open hole, cased hole, multilateral completions
- **Sand Control**: Gravel packs, screens, chemical consolidation
- **Stimulation**: Hydraulic fracturing, matrix acidizing, acid fracturing
- **Perforating**: Charge selection, underbalance design, oriented perforating
- **Smart Wells**: ICVs, downhole monitoring, intelligent completions

### Facilities Engineering
- **Separation Systems**: Two/three-phase separators, slug catchers
- **Processing Equipment**: Dehydration, sweetening, NGL recovery
- **Compression Systems**: Reciprocating, centrifugal compressors
- **Pipeline Design**: Hydraulics, material selection, corrosion control
- **Storage Facilities**: Tank design, vapor recovery, custody transfer

### Offshore Engineering
- **Platform Types**: Fixed, floating (FPSO, TLP, SPAR, semi-sub)
- **Subsea Systems**: Trees, manifolds, pipelines, umbilicals
- **Riser Systems**: SCR, TTR, flexible risers, hybrid systems
- **Mooring Systems**: Spread mooring, turret mooring, DP systems
- **Installation Methods**: Heavy lift, float-over, J-lay, S-lay, reel-lay

## Industry Standards and Regulations

### API Standards
- **API RP 2A-WSD**: Fixed offshore platforms
- **API RP 14E**: Offshore production systems
- **API RP 14C**: Safety systems for offshore production
- **API 6A**: Wellhead and christmas tree equipment
- **API 17 Series**: Subsea production systems

### International Standards
- **ISO 19900 Series**: Petroleum and natural gas industries — offshore structures
- **ISO 13703**: Design and installation of piping systems on offshore platforms
- **NORSOK Standards**: Norwegian petroleum industry standards
- **DNV Standards**: Classification and certification

### Regulatory Bodies
- **BSEE (US)**: Bureau of Safety and Environmental Enforcement
- **HSE (UK)**: Health and Safety Executive
- **PSA (Norway)**: Petroleum Safety Authority
- **NOPSEMA (Australia)**: National Offshore Petroleum Safety Authority

### Data Standards
- **WITSML**: Wellsite information transfer standard
- **PRODML**: Production data standards
- **RESQML**: Reservoir characterization markup language
- **PPDM**: Professional petroleum data management

## Key Analysis Methods

### Economic Evaluation
- **NPV/IRR Analysis**: Project economics, sensitivity analysis
- **Decline Curve Analysis**: Arps equations, type curves
- **Monte Carlo Simulation**: Risk assessment, probabilistic forecasting
- **Real Options Valuation**: Investment timing, abandonment options

### Technical Analysis
- **Material Balance**: Tank models, aquifer models, gas cap expansion
- **Pressure Transient Analysis**: Well test interpretation, skin factor
- **Rate Transient Analysis**: Production data analysis, EUR estimation
- **Network Modeling**: Integrated production system optimization

### Software Tools
- **Reservoir Simulation**: Eclipse, CMG (IMEX/GEM/STARS), Petrel, tNavigator
- **Production Engineering**: PROSPER, GAP, PIPESIM, OLGA
- **Python Domain Libraries**: lasio (LAS files), welly (well logs), striplog (lithology)

## Common Calculations

### Volumetrics
```python
# Stock Tank Oil Initially In Place (STOIIP)
STOIIP = 7758 * A * h * phi * (1 - Sw) / Boi   # STB

# Gas Initially In Place (GIIP)
GIIP = 43560 * A * h * phi * (1 - Sw) / Bgi    # SCF
```

### Decline Curves
```python
import numpy as np

# Exponential decline
q_exp = qi * np.exp(-D * t)

# Hyperbolic decline
q_hyp = qi / (1 + b * D * t) ** (1 / b)

# Harmonic decline (b = 1)
q_harm = qi / (1 + D * t)
```

### Material Balance (General Form)
```python
# F = N * Et + We - Wp * Bw
# F  = underground withdrawal
# Et = total expansion
# We = water influx
```

### STOIIP Function with Validation
```python
def calculate_oil_in_place(
    area_acres: float,
    thickness_ft: float,
    porosity: float,
    water_saturation: float,
    formation_volume_factor: float
) -> float:
    """
    Calculate Stock Tank Oil Initially In Place (STOIIP).

    Args:
        area_acres: Reservoir area in acres
        thickness_ft: Net pay thickness in feet
        porosity: Porosity fraction (0-1)
        water_saturation: Water saturation fraction (0-1)
        formation_volume_factor: Oil FVF in RB/STB

    Returns:
        STOIIP in stock tank barrels (STB)
    """
    return (7758 * area_acres * thickness_ft * porosity *
            (1 - water_saturation) / formation_volume_factor)


def validate_reservoir_parameters(params: dict) -> None:
    """Validate reservoir parameters are within reasonable ranges."""
    if not 0 < params.get('porosity', 0) <= 0.4:
        raise ValueError(
            f"Porosity {params['porosity']} outside valid range (0, 0.4]"
        )
    if not 0 <= params.get('water_saturation', 0) < 1:
        raise ValueError(
            f"Water saturation {params['water_saturation']} outside valid range [0, 1)"
        )
```

## Python Libraries for Oil and Gas

### Core Libraries
```python
import pandas as pd
import numpy as np
import scipy.optimize

import matplotlib.pyplot as plt
import plotly.graph_objects as go

from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler

import lasio      # LAS file reading
import welly      # Well log analysis
import striplog   # Lithology and stratigraphy
```

### worldenergydata Custom Modules
```python
from worldenergydata.decline_curves import arps_decline
from worldenergydata.pvt import standing_correlation
from worldenergydata.material_balance import tank_model
from worldenergydata.economics import npv_analysis
```

## Best Practices

### Data Quality
1. Always validate input data ranges against physical constraints
2. Check for missing or anomalous values before analysis
3. Apply appropriate data cleaning techniques
4. Document data sources and assumptions

### Analysis Workflow
1. Start with exploratory data analysis
2. Apply domain-specific correlations (Standing, Beggs-Brill, etc.)
3. Validate results against field analogues
4. Perform sensitivity analysis
5. Document uncertainties explicitly

### Safety and Environment
1. Follow HSE guidelines in all technical work
2. Consider environmental impact in design decisions
3. Apply risk assessment methodologies (bow-tie, HAZID/HAZOP)
4. Maintain regulatory compliance throughout

### Code Standards
1. Use industry-standard units (field or SI — be explicit)
2. Include unit conversion utilities
3. Implement robust error handling with physical constraint checks
4. Provide comprehensive docstrings
5. Follow PEP 8 style guide

### Response Standards When Providing Technical Solutions
1. Start with fundamentals: explain underlying principles before complex solutions
2. Use industry terminology with explanations where needed
3. Include calculations: show relevant equations and example calculations
4. Reference standards: cite applicable API, ISO, or regulatory standards
5. Consider safety: always prioritize HSE considerations in recommendations

## Integration with WorldEnergyData

### BSEE Module
- Production data analysis from BSEE databases
- Safety incident tracking and trend analysis
- Regulatory compliance reporting
- Well performance monitoring

### Energy Markets
- Oil price correlation with production data
- Supply/demand analysis and forecasting
- Market volatility assessment
- Project economics evaluation

### Environmental Impact
- Emissions monitoring and carbon footprint analysis
- Sustainability metrics and ESG reporting
- Regulatory compliance tracking

## References

1. Petroleum Engineering Handbook — SPE
2. Reservoir Engineering Handbook — Tarek Ahmed
3. Production Optimization Using Nodal Analysis — Beggs
4. Applied Petroleum Reservoir Engineering — Craft and Hawkins
5. Fundamentals of Reservoir Engineering — Dake

## Usage

Invoke this skill when:
- Performing reservoir characterization or reserve estimation
- Analyzing or designing production systems (artificial lift, nodal analysis)
- Working on completion design or stimulation programs
- Evaluating offshore platform, subsea, or riser system design
- Calculating STOIIP/GIIP volumetrics or decline curve analysis
- Performing material balance or pressure transient analysis
- Generating Python code for petroleum engineering calculations
- Analyzing BSEE production data or safety statistics
- Evaluating project economics (NPV, IRR, Monte Carlo)
- Assessing environmental impact or ESG metrics for oil and gas assets
