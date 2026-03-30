---
name: fe-analyst-what-to-document
description: 'Sub-skill of fe-analyst: What to Document.'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# What to Document

## What to Document


"Other structures" are components that interact with the primary structure but are not the primary line:

```
Other Structures:
├── Attached Buoyancy / Arch Buoys
│   ├── Object name, position (KP or z-coordinate)
│   ├── Mass [Te], displaced volume [m³], net buoyancy [kN]
│   └── Hydrodynamic coefficients (Cd, Ca)
│
├── Bend Stiffeners / Bell Mouths
│   ├── Location (top of riser, PLEM connection)
│   ├── Length, OD, stiffness curve (M-κ relationship)
│   └── Tip constraint (fixed/pinned)
│
├── I-Tubes / J-Tubes (pull-in)
│   ├── Geometry (curved section, exit angle)
│   ├── Friction coefficient
│   └── Guide centraliser positions
│
├── Clamps and Supports
│   ├── Position (KP or global z)
│   ├── Clamp mass, gap, friction coefficient
│   └── Stiffness (restrained DOFs)
│
├── Adjacent Structures (passing ship, jacket, platform)
│   ├── Proximity distance [m]
│   ├── Clearance envelope (min approach)
│   └── Interaction modelling (constraint or hydrodynamic)
│
└── Vessel (FPSO, semi, ship)
    ├── Vessel type, draught, displacement
    ├── RAO origin, heading convention
    └── Relevant motions for analysis (heave, surge, pitch for risers)
```

---
