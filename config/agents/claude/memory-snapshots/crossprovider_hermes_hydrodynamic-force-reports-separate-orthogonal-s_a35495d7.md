---
name: crossprovider hermes hydrodynamic-force-reports-separate-orthogonal-s
description: Hydrodynamic force reports separate orthogonal sweeps into independent modules
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [marine-engineering, hydrodynamics, code-patterns]
---

B1528 SIROCCO reports split current-heading-rudder and moored-current-rudder into distinct modules with separate YAML configs + dataclass validators. Avoids Cartesian-product sweep explosion and keeps force output structures orthogonal.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
