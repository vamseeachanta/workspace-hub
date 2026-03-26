---
id: RES-001
type: resource
entry_type: finding
title: "OrcFxAPI .frequencies returns Hz in descending order"
category: data
domain:
  primary: hydrodynamics
  sub_domain: diffraction
tags: [orcfxapi, orcawave, frequency, units, api, descending]
repos: [digitalmodel]
confidence: 0.95
created: "2026-03-25"
last_validated: "2026-03-25"
source:
  name: "OrcFxAPI Python Documentation"
  source_kind: manual
  url: "https://www.orcina.com/webhelp/OrcFxAPI/"
  retrieved: "2026-02-22"
provenance:
  method: manual
  reviewed_by: vamsee
  review_date: "2026-03-25"
related: [GOT-002]
ttl_days: 365
status: active
access_count: 0
file: ".claude/knowledge/entries/resources/RES-001-orcfxapi-frequencies-hz-descending.md"
---

# RES-001: OrcFxAPI .frequencies returns Hz in descending order

## Finding
The `.frequencies` property on OrcaWave result objects returns frequency values in **Hz** (not rad/s) and in **descending** order. Most BEM solvers (AQWA, Capytaine, WAMIT) return ascending rad/s.

## Implications
- Always reverse the array before comparing with other tools
- Convert to rad/s: `freq_rads = freq_hz * 2 * np.pi`
- Negative correlations in RAO comparisons almost always trace back to mismatched frequency ordering
- `displacementRAOs` shape is `(nheading, nfreq, 6)` — complex values; rotational RAOs in radians/m
