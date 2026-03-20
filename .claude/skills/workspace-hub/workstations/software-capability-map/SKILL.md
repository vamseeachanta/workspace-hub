---
name: workstations-software-capability-map
description: 'Sub-skill of workstations: Software Capability Map.'
version: 3.0.0
category: workspace-hub
type: reference
scripts_exempt: true
---

# Software Capability Map

## Software Capability Map


Structured capability reference for machine routing decisions and `CL_MACHINE_MODE` config.

```yaml
machines:
  dev-primary:
    hostname: dev-primary
    programs: [python, uv, git, claude-code, codex, gemini, worldenergydata,
               digitalmodel, assetutilities, assethold, legal-scan, pytest]
    install_method: {claude: native, codex: npm-user, gemini: pip}
    exclusive: []
    shares_hub: null
    isolated: false
    cron_variant: full

  dev-secondary:
    hostname: dev-secondary
    programs: [python, uv, git, claude-code, digitalmodel, assetutilities,
               blender, gmsh, openfoam, calculix, fenics, freecad, elmer, pytest]
    install_method: {claude: npm-sudo}   # WRK-389 pending — switch to native
    exclusive: []
    shares_hub: dev-primary
    isolated: false
    cron_variant: contribute

  licensed-win-1:
    hostname: licensed-win-1
    programs: [orcaflex, ansys, aqwa, python, office, claude-code, codex, gemini]
    install_method: {claude: native, codex: npm-user, gemini: pip}
    exclusive: [orcaflex, ansys, aqwa]   # all three are licensed programs on this machine
    shares_hub: null
    isolated: true
    cron_variant: contribute

  licensed-win-2:
    hostname: ACMA-WS014
    programs: [office, windows-tools]
    exclusive: []
    shares_hub: null
    isolated: false
    cron_variant: contribute

  gali-linux-compute-1:
    hostname: TBD
    programs: [cfd, fea, python, batch]
    exclusive: []
    shares_hub: null
    isolated: false
    cron_variant: full
```
