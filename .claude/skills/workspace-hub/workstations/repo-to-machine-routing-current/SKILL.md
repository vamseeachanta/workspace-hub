---
name: workstations-repo-to-machine-routing-current
description: 'Sub-skill of workstations: Repo-to-machine routing (current) (+2).'
version: 3.0.0
category: workspace-hub
type: reference
scripts_exempt: true
---

# Repo-to-machine routing (current) (+2)

## Repo-to-machine routing (current)


| Repo / Workload | Machine | Rationale |
|-----------------|---------|-----------|
| worldenergydata | ace-linux-1 | Data stack + Python env live here |
| workspace-hub (orchestration) | ace-linux-1 | Primary hub machine |
| digitalmodel (Python dev) | ace-linux-1 / ace-linux-2 | Open-source dev, either machine |
| assetutilities | ace-linux-1 / ace-linux-2 | Open-source dev, either machine |
| OrcaFlex work (WRK-121, WRK-131) | acma-ansys05 | Node-locked OrcaFlex license |
| ANSYS / AQWA work | acma-ansys05 | ANSYS license on this machine |
| Windows-only tools | acma-ws014 | Windows 11, office tools |
| Heavy compute (CFD, FEA, batch) | gali-linux-compute-1 | 128 cores, 128 GB RAM, 64 GB VRAM |
| Engineering CAD (SolidWorks etc.) | acma-ws014 | Windows machine; add dedicated CAD node when provisioned |


## When to set computer:


- **Always set `computer:`** — every WRK item must have a machine assigned at Capture
- Use `ace-linux-1` for hub-only meta work (docs, skills, queue management) where any machine would work
- Use the specific machine for tasks that require local tools, licensed software, or hardware
- Use a list `[machine-a, machine-b]` for tasks spanning multiple machines
- Never leave blank on `working/` items


## Multi-machine handoff


When switching machines, `/session-start` checks recent `working/` items for `computer:`
fields and prompts if the current machine differs from the last active one.
