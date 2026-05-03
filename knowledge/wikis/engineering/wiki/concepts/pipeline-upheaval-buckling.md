---
title: "Pipeline Upheaval Buckling"
tags: [pipeline, subsea, upheaval-buckling, buried-pipeline, cover-height, dnv-rp-f110]
added: 2026-05-03
last_updated: 2026-05-03
---

# Pipeline Upheaval Buckling

## Scope

Vertical-plane buckling of buried or trenched pipelines under axial-compressive force from constrained thermal expansion, restrained from above by soil cover. This page covers download (uplift-resistance) sizing, imperfection management, and Palmer-Hobbs-style screening; it does NOT cover lateral buckling (see [[pipeline-lateral-buckling]]) or corroded fitness-for-service (see [[pipeline-integrity-assessment]]).

## Key Concepts

- **Buried-pipeline driver** — trenched and backfilled pipelines cannot relieve axial force laterally, so the failure path is upward; uplift cover must hold the pipeline down.
- **Out-of-straightness imperfection** — local prop or bedding-induced vertical imperfections control the trigger amplitude; even small overbends seed upheaval.
- **Cover-height design** — required uplift resistance is a function of cover-soil weight, friction angle, and an uplift-resistance factor; underburial is a frequent root cause of operating-pipeline upheaval failures.
- **Palmer-Hobbs screening** — analytical relation between effective axial force, imperfection wavelength/amplitude, and minimum download required to keep the pipeline in place.
- **Field-rectification options** — additional rock dump, mattress placement, mechanical anchors, or controlled releasing trench-cuts to relieve axial force.
- **Calc-side reference** — `digitalmodel/src/digitalmodel/subsea/pipeline/upheaval_buckling.py` (NAME only) implements screening and rectification sizing.

## Standards / References

- DNV-RP-F110 (Global Buckling of Submarine Pipelines) — primary methodology. https://www.dnv.com/ <!-- TODO(W4-codify): replace external URL with [[../standards/dnv-rp-f110]] when standards page lands -->
- DNV-ST-F101 [[../../../engineering-standards/wiki/standards/dnv-st-f101]] — design-basis umbrella.
- DNV-RP-F114 (Pipe-Soil Interaction for Submarine Pipelines) — soil-uplift-resistance basis. https://www.dnv.com/ <!-- TODO(W4-codify): replace external URL with [[../standards/dnv-rp-f114]] when standards page lands -->

## Cross-References

- **Related concept**: [[pipeline-soil-interaction]] — uplift-resistance models from cover soil.
- **Related concept**: [[pipeline-lateral-buckling]] — horizontal-plane counterpart.
- **Related concept**: [[pipeline-route-selection]] — trenched-vs-surface-laid choice made upstream.
- **Related concept**: [[pipeline-installation-methods]] — burial method (jet-trenching, ploughing) sets the cover profile.
