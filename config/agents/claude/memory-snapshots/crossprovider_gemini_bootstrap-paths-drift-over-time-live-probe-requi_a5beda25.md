---
name: crossprovider gemini bootstrap-paths-drift-over-time-live-probe-requi
description: Bootstrap paths drift over time; live probe required before policy encoding
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [configuration-management, machine-roles, path-assumptions]
---

OpenFOAM scripts assumed `/usr/lib/openfoam/openfoam2312/etc/bashrc`, but historical notes reference `/opt/openfoam2312/etc/bashrc`; neither may be correct on future machines. Don't encode paths in policy without verifying on target hardware first. Use env-var fallback chains or live `ls` probes.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
