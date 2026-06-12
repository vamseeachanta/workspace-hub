---
name: crossprovider hermes orcawave-orcaflex-skills-40-sub-skills-organized
description: OrcaWave/OrcaFlex skills: 40+ sub-skills organized by domain and analysis type
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [orcawave-orcaflex, skill-hierarchy, hydrodynamics-domain]
---

Complex domain with 43 total skills: OrcaWave root (8 sub-skills: analysis, damping-sweep, mesh-generation, multi-body, QTF, AQWA-benchmark, to-orcaflex) + OrcaFlex root (24 sub-skills: batch-manager, code-check, environment-config, extreme-analysis, file-conversion, installation-analysis, jumper-analysis, line-wizard, modal-analysis, model-generator, modeling, model-sanitization, monolithic-to-modular, mooring-iteration, operability, post-processing, rao-import, results-comparison, spec-audit, specialist, static-debug, vessel-setup, visualization, yaml-gotchas). Reporting uses builder pattern with Pydantic config (sections, per-section enable/disable). Each skill links to digitalmodel.* code modules. This is a reference architecture for complex domain skill organization.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
