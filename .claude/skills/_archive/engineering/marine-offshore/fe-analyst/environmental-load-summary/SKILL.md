---
name: fe-analyst-environmental-load-summary
description: 'Sub-skill of fe-analyst: Environmental Load Summary (+1).'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# Environmental Load Summary (+1)

## Environmental Load Summary


```
Loads:
├── Gravity
│   └── g = 9.81 m/s²; direction: −Z (downward)
│
├── Hydrodynamic (Morison Equation)
│   ├── Drag coefficient Cd (normal) — API RP 2RD typical: 1.0−1.2
│   ├── Inertia coefficient Cm = 1 + Ca — typical Ca = 1.0
│   ├── Lift coefficient Cl (VIV suppression: 0.0 without analysis)
│   └── Added mass coefficient Ca (transverse and axial)
│
├── Wave Loading
│   ├── Wave theory: Airy (linear), Stokes 5th, Dean Stream
│   ├── Sea state: Hs [m], Tp [s], γ (JONSWAP peak factor)
│   ├── Heading: θ_wave [° from North or from vessel heading]
│   └── Direction spread: long-crested or short-crested
│
├── Current
│   ├── Profile: u(z) vs. depth [m/s at each depth]
│   ├── Heading: θ_current [°]
│   └── Type: Gulf Stream, tidal, mean loop current
│
├── Wind (for surface-piercing structures)
│   ├── Speed: U10 [m/s] (10-min mean at 10m elevation)
│   ├── Heading: θ_wind [°]
│   └── Applicable: turret mooring, topsides drag
│
└── Functional Loads
    ├── Internal pressure: Pi [MPa] (operating vs. design)
    ├── Temperature: T [°C] (thermal expansion driving force)
    ├── Lay tension: Th [kN] (installation)
    └── Pre-tension: T_initial [kN] (mooring chains)
```


## Load Combinations (Design Cases)


| Case | Wave | Current | Wind | Notes |
|---|---|---|---|---|
| Operating | 100-yr Hs, Tp | 10-yr | 10-yr | Strength check |
| Extreme | 100-yr Hs, Tp | 100-yr | 100-yr | Combined extreme |
| Fatigue | Scatter diagram | Long-term | N/A | Fatigue damage |
| Survival | 10,000-yr | — | — | Mooring intact check |
| Installation | Workability Hs | — | — | Operability window |

---
