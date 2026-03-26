---
id: RES-004
type: resource
entry_type: datapoint
title: "DNV-RP-C203 provides 221 SN curves from 17 international standards"
category: data
domain:
  primary: marine_offshore
  sub_domain: fatigue
tags: [dnv, sn-curve, fatigue, standards, digitalmodel]
repos: [digitalmodel]
confidence: 1.0
created: "2026-03-25"
last_validated: "2026-03-25"
source:
  name: "DNV-RP-C203 Fatigue Design of Offshore Steel Structures"
  source_kind: standard
  section: "Tables 2-1 through 2-8"
  edition: "2021-09"
  retrieved: "2026-03-25"
provenance:
  method: manual
  reviewed_by: vamsee
  review_date: "2026-03-25"
related: [PAT-002]
ttl_days: 730
status: active
access_count: 0
file: ".claude/knowledge/entries/resources/RES-004-dnv-rp-c203-sn-curves.md"
---

# RES-004: DNV-RP-C203 — 221 SN curves from 17 standards

## Datapoint
The digitalmodel fatigue-analysis module implements **221 SN curves** sourced from **17 international standards**, with DNV-RP-C203 (2021 edition) as the primary reference.

Key T-curve parameters for tubular joints in seawater with cathodic protection (Table 2-2):
- `log_a1 = 12.164`, `m1 = 3.0`
- `log_a2 = 16.106`, `m2 = 5.0`
- Fatigue limit at 1e7 cycles: **52.63 MPa**

## Coverage
Standards implemented include DNV-RP-C203, API RP 2A, BS 7608, Eurocode 3, AWS D1.1, and 12 others. The module supports both in-air and cathodic protection environments.
