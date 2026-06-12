---
name: crossprovider hermes dnv-rp-c205-and-pianc-121-are-normative-standard
description: DNV-RP-C205 and PIANC 121 are normative standards for naval hydrodynamics
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [naval-architecture, standards, hydrodynamics, reference-docs]
---

Forward speed corrections throughout the codebase reference DNV-RP-C205 §7.4 (encounter frequency transformation, Salvesen-Tuck-Faltinsen 1970 theory). Shallow water analysis uses DNV-RP-C205 Table 7-1 (analytical validation factors) and PIANC 121 (bank suction/clearance). These three normative references appear in parametric_hull_analysis and shallow_water modules; developers should cite them when modifying seaway analysis.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
