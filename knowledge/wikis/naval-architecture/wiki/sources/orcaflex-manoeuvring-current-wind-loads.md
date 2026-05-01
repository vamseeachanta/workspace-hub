---
title: "OrcaFlex Vessel Theory: Manoeuvring, Current, and Wind Loads"
tags: [orcaflex, yaw, current-load, wind-load, maneuvering]
sources:
  - "/mnt/ace/digitalmodel/llm-wiki/orcaflex/topics/Vesseltheory,Manoeuvringload.md"
  - "/mnt/ace/digitalmodel/llm-wiki/orcaflex/topics/Vesseltheory,Currentandwindloads.md"
  - "/mnt/ace/digitalmodel/llm-wiki/orcaflex/topics/Referencesandlinks.md"
added: 2026-04-30
last_updated: 2026-04-30
---

# OrcaFlex Vessel Theory: Manoeuvring, Current, and Wind Loads

Raw paths:

- `/mnt/ace/digitalmodel/llm-wiki/orcaflex/topics/Vesseltheory,Manoeuvringload.md`
- `/mnt/ace/digitalmodel/llm-wiki/orcaflex/topics/Vesseltheory,Currentandwindloads.md`
- `/mnt/ace/digitalmodel/llm-wiki/orcaflex/topics/Referencesandlinks.md`

## Relevance

Useful as an implementation caution for combining maneuvering yaw moment, current yaw moment, wind yaw moment, and yaw-rate drag.

## Key extracted content

- OrcaFlex manoeuvring yaw moment uses low-frequency added-mass/potential-flow terms.
- If current load is enabled, OCIMF current yaw load is assumed already to include classic Munk moment terms; OrcaFlex omits those Munk terms from manoeuvring yaw moment to avoid double counting.
- Current/wind yaw moment follows `m_z = 0.5 * C_yaw * rho * |v|^2 * A_yaw`.
- OCIMF conventions: current yaw `A_yaw = L^2 D`; wind yaw `A_yaw = L * A_sway`.
- Current yaw-rate drag is separate from OCIMF translational current coefficients and should be viscous-only if manoeuvring load is also active.

Related: [[environmental-yaw-moment-coefficients]], [[yaw-moment-rudder-sweep]].
