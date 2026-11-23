# Chip Design CAD/FEM Career Roadmap

Date: 2026-04-26
Repo: `vamseeachanta/workspace-hub`

## Executive summary

Create a focused semiconductor / chip-design engineering lane that uses ACE Engineer's existing strengths in CAD automation, finite-element analysis, document intelligence, and job-market scanning. The near-term target is not full RTL/ASIC ownership; it is a credible applied-engineering portfolio around semiconductor packaging, layout/CAD automation, electro-thermal/stress FEM, and open-source EDA reproducible flows.

## Market signal from local job-market scan

Existing job-market data already contains semiconductor-adjacent opportunities:

| Date file | Role | Company | Location | Relevance |
| --- | --- | --- | --- | --- |
| `docs/strategy/gtm/job-market-scan/raw-results/2026-04-02.json` | Sr. Technical Program Manager, ASIC | Amazon Kuiper | Sunnyvale, CA | ASIC program/process familiarity |
| `docs/strategy/gtm/job-market-scan/raw-results/2026-04-13.json` | Principal Engineer, Advanced Packaging | Marvell | Austin, TX | packaging + multi-physics |
| `docs/strategy/gtm/job-market-scan/raw-results/2026-04-13.json` | Staff Engineer, Semi Packaging Engineering | Analog Devices | Wilmington, MA | packaging reliability/manufacturing |
| `docs/strategy/gtm/job-market-scan/raw-results/2026-04-13.json` | IC Packaging Simulation Engineer | Apple | Austin, TX | simulation / FEM portfolio target |
| `docs/strategy/gtm/job-market-scan/raw-results/2026-04-13.json` | Packaging Module Development Engineer | Intel | Phoenix, AZ | advanced packaging + module development |
| `docs/strategy/gtm/job-market-scan/raw-results/2026-04-20.json` | Mechanical Engineer with semiconductor exp. | I3 INFOTEK | Gloucester, MA | direct mechanical + semiconductor bridge |

## Current external practice anchors checked

- OpenROAD / OpenROAD-flow-scripts: open-source digital physical-design flow automation.
- OpenLane documentation: reproducible RTL-to-GDS flow around open PDKs.
- GDSFactory documentation: Python-first layout / photonics / package-layout automation; checked page reports `GDSFactory 9.40.2`.
- KLayout: layout viewing/editing, DRC/LVS scripting, GDS/OASIS inspection.
- SkyWater Open PDK and GF180MCU documentation: accessible open-process learning targets.
- FEM bridge: CalculiX, FEniCSx, Elmer/OpenFOAM style multiphysics patterns are the practical local path before paid semiconductor tools.

## Technical thesis

Semiconductor roles that overlap Vamsee's background are strongest in:

1. **Packaging and reliability simulation** — thermal, thermo-mechanical stress, warpage, fatigue, shock/vibration, solder/joint reliability.
2. **CAD/layout automation** — Python generation and extraction of GDS/OASIS/DXF/STEP metadata; KLayout/GDSFactory workflows.
3. **EDA flow literacy** — OpenLane/OpenROAD reproducible runs, timing/power/area reports, PDK structure, DRC/LVS concepts.
4. **Engineering evidence portfolio** — benchmark reports, validated examples, and job-mapped learning artifacts.

## Capability roadmap

### Wave 1 — research + taxonomy

Deliver a semiconductor CAD/FEM knowledge base:

- roles and keywords: ASIC physical design, packaging simulation, thermal design, reliability, DFM, DRC/LVS, PDK, GDS/OASIS;
- tools: OpenROAD, OpenLane, KLayout, GDSFactory, Sky130, GF180MCU, CalculiX/FEniCSx, Elmer, ParaView;
- standards/practices: JEDEC reliability concepts, IPC/package terminology, foundry PDK rules, reproducible flow artifacts;
- job-to-skill matrix aligned to the existing GTM job-market scan.

### Wave 2 — open-source EDA reproducible flow

Build a small, documented RTL-to-GDS demonstration:

- containerized OpenLane/OpenROAD flow;
- tiny reference design (counter/FIFO/simple ALU);
- PDK target: Sky130 or GF180MCU;
- captured reports: timing, area, power, DRC/LVS status;
- HTML report that explains what each artifact means to a hiring manager or client.

### Wave 3 — Python CAD/layout automation

Build a layout/CAD automation demonstration:

- GDSFactory or KLayout-scripted generation of a small parameterized cell/package/interposer-style layout;
- geometry export/import proof: GDS/OASIS plus DXF/SVG/STEP where practical;
- metadata extraction tables: layers, polygons, bounding boxes, nets/ports where available;
- reproducible tests around geometry invariants.

### Wave 4 — semiconductor packaging FEM benchmark

Build an electronics package FEM benchmark that uses existing engineering strengths:

- package stackup: die, substrate, mold/underfill, solder balls or simplified interconnects;
- physics: thermal load, coefficient-of-thermal-expansion mismatch, stress/warpage outputs;
- local solver: CalculiX first, optional FEniCSx/Elmer later;
- report: mesh, boundary conditions, material table, convergence check, stress/temperature plots.

### Wave 5 — portfolio + job application packet

Create a reusable job-application packet:

- portfolio page linking reports and GitHub issues;
- resume bullets grounded in artifacts;
- role-specific cover-letter snippets for packaging simulation, CAD automation, and ASIC/EDA program roles;
- interview prep notebook: explain DRC/LVS, PDK, RTL-to-GDS, thermal-mechanical FEM, and reliability terminology.

## Initial GitHub issue set

The initial issue tree should include one umbrella plus focused feature issues:

1. umbrella: semiconductor chip-design CAD/FEM career lane;
2. research/job taxonomy and knowledge base;
3. open-source EDA RTL-to-GDS demo;
4. layout/CAD automation demo;
5. packaging FEM benchmark;
6. portfolio/job-application packet.

All implementation issues must follow repo policy: issue -> plan -> adversarial review -> user approval -> TDD implementation.

## Acceptance definition for the lane

The lane is credible when the repo has:

- a current semiconductor CAD/FEM knowledge base;
- at least one reproducible open-source EDA flow report;
- at least one Python-driven layout/CAD artifact;
- at least one FEM benchmark report for package stress/thermal behavior;
- a job-application packet that maps artifacts to target role requirements.
